# FastAPI OpenTelemetry → Dynatrace Demo

This repo packages a minimal FastAPI service that is instrumented with OpenTelemetry and ships traces to Dynatrace through an OpenTelemetry Collector. The project includes:

- `app/`: FastAPI application plus OTEL setup
- `docker/`: container image definition
- `k8s/`: Kubernetes manifests for the service, service mesh, and OTEL collector
- `argocd/`: Argo CD `Application` for GitOps-driven deployment

## Architecture

```
FastAPI Pod ──OTLP HTTP──▶ in-cluster OTEL Collector ──OTLP HTTP──▶ Dynatrace tenant
```

## Prerequisites

- Python 3.11+
- Docker 24+
- kubectl + access to a Kubernetes cluster
- Argo CD (optional, for GitOps rollout)
- Dynatrace environment URL and API token with OTLP ingest permissions

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r app/requirements.txt
   ```

3. Run the app:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Test endpoints:

   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/slow
   ```

### OpenTelemetry locally

The helper module `app/otel.py` configures a tracer provider that exports to `http://otel-collector:4318/v1/traces`. When running outside Kubernetes, either:

- run an OTEL Collector locally and map that hostname, or
- override the exporter endpoint via environment variable before starting `uvicorn`:

  ```bash
  export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
  uvicorn app.main:app ...
  ```

## Container Image

```
docker build -t your-dockerhub/fastapi-otel:latest -f docker/Dockerfile .
docker push your-dockerhub/fastapi-otel:latest
```

Update the image reference inside `k8s/deployment.yaml` before deploying.

## Kubernetes Manifests

- `k8s/deployment.yaml`: FastAPI workload (2 replicas)
- `k8s/service.yaml`: ClusterIP service on port 80 → 8000
- `k8s/collector-deployment.yaml`: collector `Deployment` and ConfigMap mount
- `k8s/otel-collector.yaml`: ConfigMap containing Dynatrace exporter settings

Apply them manually:

```bash
kubectl apply -f k8s/otel-collector.yaml
kubectl apply -f k8s/collector-deployment.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Dynatrace wiring

1. Replace `YOUR_ENV` and `YOUR_API_TOKEN` in `k8s/otel-collector.yaml` with real values (store tokens in `Secret`s for production).
2. Ensure outbound connectivity from the cluster to Dynatrace ingest endpoints.

## Argo CD Automation

`argocd/application.yaml` defines a GitOps workflow that watches this repo and applies the manifests under `k8s/`. To use it:

```bash
kubectl apply -n argocd -f argocd/application.yaml
```

Argo CD will continuously sync, self-heal, and prune Kubernetes resources in the `default` namespace.

## Endpoints

| Method | Path   | Description                 |
|--------|--------|-----------------------------|
| GET    | `/`    | Health probe / hello world  |
| GET    | `/slow`| Sleeps 2 seconds for tracing |

## Troubleshooting

- Use `kubectl logs deployment/fastapi-otel` to inspect the app.
- Use `kubectl logs deployment/otel-collector` to ensure spans are exported.
- Confirm spans arrive in Dynatrace under service name `fastapi-otel-app`.
- Verify OTLP traffic with `kubectl port-forward service/otel-collector 4318:4318` and send spans locally for debugging.

## Next Steps

- Secure sensitive values with Kubernetes Secrets and sealed-secrets / External Secrets.
- Add metrics and logs pipelines via OTEL Collector.
- Add CI to build and push the container image automatically.
