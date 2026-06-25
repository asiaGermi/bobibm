#!/usr/bin/env python3
"""
Deploy MCP Server to IBM Cloud Code Engine via Source-to-Image build.
No Docker or IBM Cloud CLI required — uses IBM Cloud APIs directly.

Usage:
    $env:IBM_CLOUD_API_KEY = "your-key"
    python scripts/deploy_mcp.py
"""

import os
import sys
import time
import requests
from pathlib import Path

# Carica .env da bobibm/ se IBM_CLOUD_API_KEY non è già settata
_env_path = Path(__file__).parent.parent / "bobibm" / ".env"
if _env_path.exists() and not os.environ.get("IBM_CLOUD_API_KEY"):
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

REGION = "eu-de"
CE_PROJECT_NAME = "ce-675000bo4y"
APP_NAME = "financial-risk-mcp"
IMAGE = "private.de.icr.io/financial-risk/mcp-server:latest"
GITHUB_REPO = "https://github.com/asiaGermi/bobibm"
# Build context = repo root; Dockerfile is at mcp_server/Dockerfile
DOCKERFILE_PATH = "mcp_server/Dockerfile"
BUILD_NAME = "financial-risk-mcp-build"

CE_API = f"https://api.{REGION}.codeengine.cloud.ibm.com/v2"
IAM_URL = "https://iam.cloud.ibm.com/identity/token"


def get_iam_token(api_key: str) -> str:
    resp = requests.post(
        IAM_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_project_id(token: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{CE_API}/projects", headers=headers, timeout=30)
    print(f"  API status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Response: {resp.text}")
        resp.raise_for_status()
    data = resp.json()
    print(f"  Raw response keys: {list(data.keys())}")
    projects = data.get("projects", [])
    print(f"  Projects found: {len(projects)}")
    for p in projects:
        print(f"    - {p.get('name')} / {p.get('id')}")
        if p.get("name") == CE_PROJECT_NAME or p.get("id") == CE_PROJECT_NAME:
            print(f"  Project: {p['name']} (ID: {p['id']})")
            return p["id"]
    # If empty, maybe the project ID is actually a direct UUID — try it directly
    print(f"\n  Projects list empty. Trying '{CE_PROJECT_NAME}' as direct project ID...")
    resp2 = requests.get(f"{CE_API}/projects/{CE_PROJECT_NAME}", headers=headers, timeout=30)
    print(f"  Direct lookup status: {resp2.status_code}")
    if resp2.status_code == 200:
        p = resp2.json()
        print(f"  Found: {p.get('name')} (ID: {p.get('id')})")
        return p.get("id", CE_PROJECT_NAME)
    print(f"  Direct lookup response: {resp2.text[:300]}")
    raise RuntimeError(f"Project '{CE_PROJECT_NAME}' not found. Available: {[p['name'] for p in projects]}")


def get_icr_secret(token: str, project_id: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{CE_API}/projects/{project_id}/secrets", headers=headers, timeout=30)
    resp.raise_for_status()
    secrets = resp.json().get("secrets", [])
    for s in secrets:
        if "icr" in s.get("name", "").lower():
            print(f"  ICR secret: {s['name']}")
            return s["name"]
    for s in secrets:
        if s.get("format") == "registry":
            print(f"  Registry secret: {s['name']}")
            return s["name"]
    raise RuntimeError("No ICR secret found. Ensure IBM Container Registry is linked to the project.")


def create_or_update_build(token: str, project_id: str, icr_secret: str) -> None:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "source_url": GITHUB_REPO,
        "source_type": "git",
        "strategy_type": "dockerfile",
        "strategy_spec_file": DOCKERFILE_PATH,
        "output_image": IMAGE,
        "output_secret": icr_secret,
    }
    resp = requests.get(f"{CE_API}/projects/{project_id}/builds/{BUILD_NAME}", headers=headers, timeout=30)
    if resp.status_code == 200:
        print(f"  Updating build '{BUILD_NAME}'...")
        resp = requests.patch(
            f"{CE_API}/projects/{project_id}/builds/{BUILD_NAME}",
            headers={**headers, "If-Match": resp.headers.get("Etag", "*")},
            json=payload, timeout=30,
        )
    else:
        print(f"  Creating build '{BUILD_NAME}'...")
        resp = requests.post(
            f"{CE_API}/projects/{project_id}/builds",
            headers=headers,
            json={"name": BUILD_NAME, **payload}, timeout=30,
        )
    resp.raise_for_status()


def trigger_build(token: str, project_id: str) -> str:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    run_name = f"{BUILD_NAME}-{int(time.time())}"
    resp = requests.post(
        f"{CE_API}/projects/{project_id}/build-runs",
        headers=headers,
        json={"name": run_name, "build_name": BUILD_NAME}, timeout=30,
    )
    resp.raise_for_status()
    print(f"  Build run '{run_name}' triggered.")
    return run_name


def wait_for_build(token: str, project_id: str, run_name: str, timeout: int = 600) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{CE_API}/projects/{project_id}/build-runs/{run_name}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        reason = resp.json().get("status_details", {}).get("reason", "")
        if reason == "Succeeded":
            print("  Build succeeded!")
            return
        if reason in ("Failed", "Error"):
            raise RuntimeError(f"Build failed: {resp.json()}")
        print(f"  Build: {reason or 'running'}... (15s)")
        time.sleep(15)
    raise TimeoutError(f"Build did not complete within {timeout}s")


def create_or_update_app(token: str, project_id: str) -> None:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    app_config = {
        "image_reference": IMAGE,
        "image_port": 8080,
        "scale_min_instances": 1,
        "scale_max_instances": 3,
        "scale_cpu_limit": "0.5",
        "scale_memory_limit": "1G",
        "run_env_variables": [
            {"type": "literal", "name": "MCP_TRANSPORT", "value": "sse"},
            {"type": "literal", "name": "PORT", "value": "8080"},
        ],
    }
    resp = requests.get(f"{CE_API}/projects/{project_id}/apps/{APP_NAME}", headers=headers, timeout=30)
    if resp.status_code == 200:
        print(f"  Updating app '{APP_NAME}'...")
        resp = requests.patch(
            f"{CE_API}/projects/{project_id}/apps/{APP_NAME}",
            headers={**headers, "If-Match": resp.headers.get("Etag", "*")},
            json=app_config, timeout=30,
        )
    else:
        print(f"  Creating app '{APP_NAME}'...")
        resp = requests.post(
            f"{CE_API}/projects/{project_id}/apps",
            headers=headers,
            json={"name": APP_NAME, **app_config}, timeout=30,
        )
    resp.raise_for_status()


def wait_for_app_ready(token: str, project_id: str, timeout: int = 300) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{CE_API}/projects/{project_id}/apps/{APP_NAME}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        status = resp.json().get("status", "unknown")
        if status == "ready":
            print("  App ready!")
            return
        print(f"  App: {status}... (10s)")
        time.sleep(10)
    raise TimeoutError(f"App not ready after {timeout}s")


def get_app_url(token: str, project_id: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{CE_API}/projects/{project_id}/apps/{APP_NAME}", headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("endpoint", f"https://{APP_NAME}.{project_id}.{REGION}.codeengine.appdomain.cloud")


def main():
    api_key = os.environ.get("IBM_CLOUD_API_KEY")
    if not api_key:
        print("ERROR: IBM_CLOUD_API_KEY not set.")
        print("  $env:IBM_CLOUD_API_KEY = 'your-key'")
        sys.exit(1)

    print("=" * 60)
    print("MCP Server Deploy — IBM Cloud Code Engine")
    print("=" * 60)

    print("\n[1/5] IAM token...")
    token = get_iam_token(api_key)

    # Debug: mostra quale account IBM Cloud sta usando questa chiave
    acc_resp = requests.get(
        "https://iam.cloud.ibm.com/v1/apikeys/details",
        headers={"Authorization": f"Bearer {token}", "IAM-Apikey": os.environ.get("IBM_CLOUD_API_KEY","")},
        timeout=15
    )
    if acc_resp.status_code == 200:
        acc = acc_resp.json()
        print(f"  API key owner: {acc.get('name')} | account: {acc.get('account_id')} | created_by: {acc.get('iam_id')}")
    else:
        print(f"  (account info non disponibile: {acc_resp.status_code})")

    print("\n[2/5] Code Engine project...")
    project_id = get_project_id(token)

    print("\n[3/5] Source-to-Image build (2-5 min)...")
    icr_secret = get_icr_secret(token, project_id)
    create_or_update_build(token, project_id, icr_secret)
    run_name = trigger_build(token, project_id)
    wait_for_build(token, project_id, run_name)

    print("\n[4/5] Deploying app...")
    create_or_update_app(token, project_id)
    wait_for_app_ready(token, project_id)

    print("\n[5/5] URL...")
    app_url = get_app_url(token, project_id)

    print("\n" + "=" * 60)
    print("DEPLOY COMPLETE")
    print("=" * 60)
    print(f"\nMCP Server : {app_url}")
    print(f"SSE        : {app_url}/sse")
    print(f"Health     : {app_url}/health")
    print("\nStep 3 — registra in watsonx Orchestrate:")
    print(f"""
  orchestrate toolkits add `
    --kind mcp `
    --name financial-risk-mcp `
    --description "Financial Risk Management: 5 MCP tools for AML/fraud analysis powered by IBM Granite" `
    --url {app_url}/sse `
    --transport sse `
    --tools "*"
""")


if __name__ == "__main__":
    main()
