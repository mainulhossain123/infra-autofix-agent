# Kustomize Overlays

Quick deployment with Kustomize for different environments.

## Structure

```
k8s/
├── kustomization.yaml          # Base configuration
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

## Deploy with Kustomize

### Development
```bash
kubectl apply -k k8s/overlays/dev
```

### Staging
```bash
kubectl apply -k k8s/overlays/staging
```

### Production
```bash
kubectl apply -k k8s/overlays/prod
```

## Update Images

```bash
# Update specific image
cd k8s
kustomize edit set image ghcr.io/mainulhossain123/infra-autofix-agent-app:v1.2.0

# Apply changes
kubectl apply -k .
```

## View Generated Manifests

```bash
# Preview what will be applied
kustomize build k8s/overlays/prod

# Save to file
kustomize build k8s/overlays/prod > manifests.yaml
```
