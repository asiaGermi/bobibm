# Ottimizzazione Registry IBM Container Registry

## Problema
La quota di **storage** (512 MB piano Free) si supera quando si accumulano immagini attive non taggate + immagini nel trash. Le immagini nel trash non si possono eliminare definitivamente prima dei 30 giorni.

## ✅ Rimedio Immediato (TESTATO il 25 giugno 2026)

**Cancellare le immagini attive NON taggate dalla UI:**

1. Vai su **https://cloud.ibm.com/containers/registry/images** → Location: **Frankfurt**
2. Seleziona tutte le immagini **senza tag** (NON toccare quella con tag `latest`)
3. Clicca **Delete** → vanno in trash ma liberano storage perché le layer condivise non vengono duplicate
4. Verifica con `ibmcloud cr quota` → storage deve scendere sotto 512 MB
5. Rilancia il buildrun

**Risultato:** da 554 MB → 146 MB dopo aver eliminato 4 immagini non taggate.

> **Nota:** NON tentare `ibmcloud cr image-rm` sulle immagini in trash — le rimanda in trash azzerando il countdown dei 30 giorni.
> NON tentare `ibmcloud cr quota-set --storage` — il limite è fisso a 512 MB sul piano Free.

## Prevenzione

Evitare rebuild multipli ravvicinati — ogni build che sovrascrive `latest` lascia un'immagine non taggata che accumula storage. Verificare con `ibmcloud cr quota` prima di ogni deploy.

## Soluzioni Alternative

### 1. Attendere il Reset Mensile
La quota di storage si resetta automaticamente il primo giorno del mese.

### 2. Richiedere Aumento Quota
```bash
# Verifica quota attuale
ibmcloud cr quota

# Richiedi aumento (esempio: 1GB)
ibmcloud cr quota-set --traffic 1024
```

### 3. Migrare a Registry Alternativo

#### Opzione A: GitHub Container Registry (Consigliato)
```bash
# Login a GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag e push dell'immagine
docker tag financial-risk-api:latest ghcr.io/USERNAME/financial-risk-api:latest
docker push ghcr.io/USERNAME/financial-risk-api:latest
```

#### Opzione B: Docker Hub
```bash
# Login a Docker Hub
docker login

# Tag e push
docker tag financial-risk-api:latest USERNAME/financial-risk-api:latest
docker push USERNAME/financial-risk-api:latest
```

## Best Practices per Evitare il Problema

### 1. Build Locale + Push Selettivo
```bash
# Build locale senza push automatico
docker build -t financial-risk-api:latest .

# Test locale
docker run -p 8000:8000 financial-risk-api:latest

# Push solo quando necessario
docker tag financial-risk-api:latest de.icr.io/financial-risk/api:v1.0.0
docker push de.icr.io/financial-risk/api:v1.0.0
```

### 2. Utilizzare Tag Semantici
```bash
# Evita rebuild inutili usando tag specifici
docker build -t de.icr.io/financial-risk/api:v1.0.0 .
docker push de.icr.io/financial-risk/api:v1.0.0

# Non usare :latest per ogni build
```

### 3. Multi-Stage Build per Ridurre Dimensioni
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (più piccola)
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Layer Caching Efficiente
```dockerfile
# Copia requirements prima del codice
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia il codice dopo (cambia più spesso)
COPY . .
```

### 5. GitHub Actions con Cache
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Cache Docker layers
        uses: actions/cache@v3
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-buildx-
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          cache-from: type=local,src=/tmp/.buildx-cache
          cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
      
      - name: Move cache
        run: |
          rm -rf /tmp/.buildx-cache
          mv /tmp/.buildx-cache-new /tmp/.buildx-cache
```

## Migrazione da IBM CR a GitHub CR

### 1. Aggiorna Dockerfile (se necessario)
Il Dockerfile rimane identico.

### 2. Aggiorna Script di Deploy
```bash
# deployment/deploy_to_github_cr.sh
#!/bin/bash

set -e

REGISTRY="ghcr.io"
REPO="USERNAME/financial-risk-api"
TAG="${1:-latest}"

echo "Building image..."
docker build -t ${REGISTRY}/${REPO}:${TAG} .

echo "Pushing to GitHub Container Registry..."
docker push ${REGISTRY}/${REPO}:${TAG}

echo "Deploy to IBM Code Engine..."
ibmcloud ce application update financial-risk-api \
  --image ${REGISTRY}/${REPO}:${TAG} \
  --registry-secret github-cr-secret
```

### 3. Crea Secret in Code Engine
```bash
# Crea secret per GitHub CR
ibmcloud ce secret create --name github-cr-secret \
  --from-literal username=USERNAME \
  --from-literal password=GITHUB_TOKEN

# Aggiorna applicazione per usare il nuovo registry
ibmcloud ce application update financial-risk-api \
  --image ghcr.io/USERNAME/financial-risk-api:latest \
  --registry-secret github-cr-secret
```

## Monitoraggio Quota

### Script di Monitoraggio
```bash
#!/bin/bash
# check_quota.sh

QUOTA=$(ibmcloud cr quota --output json)
USED=$(echo $QUOTA | jq -r '.traffic.used')
LIMIT=$(echo $QUOTA | jq -r '.traffic.limit')
PERCENT=$((USED * 100 / LIMIT))

echo "Quota utilizzata: ${USED}MB / ${LIMIT}MB (${PERCENT}%)"

if [ $PERCENT -gt 80 ]; then
  echo "⚠️  ATTENZIONE: Quota oltre l'80%"
  exit 1
fi
```

## Contatti Supporto IBM

Se hai bisogno di un aumento urgente della quota:
1. Apri un ticket di supporto IBM Cloud
2. Specifica l'account: itz-saas-290 (3115951)
3. Specifica il namespace: financial-risk (eu-de)
4. Richiedi aumento temporaneo o permanente

## Riferimenti
- [IBM Container Registry Quota](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_quota)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub](https://docs.docker.com/docker-hub/)