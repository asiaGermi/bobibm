# watsonx Orchestrate Environment Setup Scripts

These scripts help you quickly add and activate a new watsonx Orchestrate SaaS environment for the ADK.

## Prerequisites

- watsonx Orchestrate ADK installed (`pip install ibm-watsonx-orchestrate`)
- Service instance URL from your watsonx Orchestrate instance
- API key generated from your watsonx Orchestrate instance

## Getting Your Credentials

### For IBM Cloud Environments:

1. Log in to your watsonx Orchestrate instance
2. Click your user icon (top right) → **Settings**
3. Go to the **API details** tab
4. Copy the **service instance URL**
5. Click **Generate API key** button
6. Follow the IBM Cloud IAM prompts to create and copy your API key

### For AWS/SaaS Environments:

1. Log in to your watsonx Orchestrate instance
2. Click your user icon (top right) → **Settings**
3. Go to the **API details** tab
4. Copy the **service instance URL**
5. Click **Generate API key** button and copy the key

**Note:** API keys are not retrievable after creation. Store them securely.

## Usage

### Linux/macOS (Bash)

```bash
# Make the script executable
chmod +x setup-wxo-env.sh

# Run the script
./setup-wxo-env.sh
```

### Windows (PowerShell)

```powershell
# Run the script
.\setup-wxo-env.ps1
```

## What the Scripts Do

1. **Prompt for environment details:**
   - Environment name (e.g., "production", "dev", "staging")
   - Service instance URL
   - API key (entered securely)

2. **Auto-detect environment type:**
   - IBM Cloud (ibm_iam)
   - AWS/SaaS (mcsp)
   - On-premises (cpd)
   - Falls back to manual selection if detection fails

3. **Add the environment:**
   - Runs `orchestrate env add` with appropriate parameters

4. **Activate the environment:**
   - Runs `orchestrate env activate` with your API key
   - Makes the environment active for all subsequent commands

## After Setup

Once the environment is activated, you can:

```bash
# List available agents
orchestrate agents list

# List available tools
orchestrate tools list

# Start an interactive chat
orchestrate chat start

# Import an agent
orchestrate agents import -f agent.yaml

# Import a tool
orchestrate tools import -k python -f tool.py
```

## Important Notes

- **Authentication expires every 2 hours** for remote environments
- To re-activate after expiration:
  ```bash
  orchestrate env activate <environment-name>
  ```
- You can have multiple environments configured
- Switch between environments using `orchestrate env activate <name>`
- List all configured environments: `orchestrate env list`

## Environment Types

- **ibm_iam**: IBM Cloud environments using IBM Identity and Access Management
- **mcsp**: AWS/SaaS environments using Multi-Cloud SaaS Platform authentication
- **cpd**: On-premises Cloud Pak for Data environments

## Troubleshooting

### "orchestrate: command not found"
- Ensure the ADK is installed: `pip install ibm-watsonx-orchestrate`
- Verify your PATH includes Python scripts directory

### Authentication Errors
- Verify your API key is correct and not expired
- Check that the service instance URL is correct
- Ensure you have the right permissions in your watsonx Orchestrate instance

### SSL Certificate Errors (On-premises only)
- For self-signed certificates, add `--insecure` flag when adding environment:
  ```bash
  orchestrate env add -n <name> -u <url> --insecure
  ```

## Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Add environment
orchestrate env add -n <environment-name> -u <service-instance-url> --type <type>

# Activate environment
orchestrate env activate <environment-name> --api-key <your-api-key>
```

## Security Best Practices

- Never commit API keys to version control
- Store API keys in a secure password manager
- Rotate API keys regularly
- Use different API keys for different environments
- Limit API key permissions to minimum required access

## Support

For more information, visit:
- [watsonx Orchestrate ADK Documentation](https://developer.watson-orchestrate.ibm.com)
- [Environment Configuration Guide](https://developer.watson-orchestrate.ibm.com/environment/initiate_environment)