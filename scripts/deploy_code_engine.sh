#!/usr/bin/env bash
# Deploy su IBM Code Engine — Financial Risk API
# Uso: ./scripts/deploy_code_engine.sh [messaggio commit opzionale]

set -e

BUILD_NAME="financial-risk-api-build-ktk8x"
APP_NAME="financial-risk-api"
COMMIT_MSG="${1:-fix: deploy aggiornamento}"

echo "=== 1. Git push ==="
git add -A
git commit -m "$COMMIT_MSG

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>" || echo "(nessuna modifica da committare)"
git push origin main

echo ""
echo "=== 2. Build Code Engine ==="
BUILD_RUN=$(ibmcloud ce buildrun submit --build "$BUILD_NAME" --output jsonpath='{.metadata.name}' 2>/dev/null || true)

# Fallback: ricava il nome dall'output testuale
if [ -z "$BUILD_RUN" ]; then
  BUILD_RUN=$(ibmcloud ce buildrun submit --build "$BUILD_NAME" 2>&1 | grep -oP "(?<=Inoltro dell'esecuzione della build ')[\w\-]+" | head -1)
fi

if [ -z "$BUILD_RUN" ]; then
  echo "Impossibile ricavare il nome del buildrun. Controlla manualmente con:"
  echo "  ibmcloud ce buildrun list"
  exit 1
fi

echo "Build avviata: $BUILD_RUN"

echo ""
echo "=== 3. Attesa completamento build ==="
until ibmcloud ce buildrun get -n "$BUILD_RUN" 2>&1 | grep -qE "succeeded|failed"; do
  STATUS=$(ibmcloud ce buildrun get -n "$BUILD_RUN" 2>&1 | grep "Stato:" | awk '{print $2}')
  echo "  stato: $STATUS — attendo 15s..."
  sleep 15
done

FINAL=$(ibmcloud ce buildrun get -n "$BUILD_RUN" 2>&1 | grep "Stato:")
echo "  $FINAL"

if echo "$FINAL" | grep -q "failed"; then
  echo "BUILD FALLITA. Logs:"
  ibmcloud ce buildrun logs -n "$BUILD_RUN"
  exit 1
fi

echo ""
echo "=== 4. App update ==="
ibmcloud ce app update -n "$APP_NAME"

echo ""
echo "=== FATTO ==="
echo "URL: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
echo "Aspetta 30s poi Ctrl+F5 sul dashboard."
