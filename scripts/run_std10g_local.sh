#!/usr/bin/env bash
set -Eeuo pipefail

# STD-10G local runbook. This script is intentionally conservative:
# - it never fabricates missing tools or evidence;
# - it never pushes or deploys unless explicitly enabled;
# - it signs/scans one immutable digest and fails on mismatch.
#
# Required tools for build/evidence: docker, trivy, cosign.
# Optional: syft for SBOM; helm and kubectl for explicitly enabled staging rehearsal.
# Required environment: IMAGE_REPOSITORY (for example registry.example/honestagent).
# Optional: PUSH_IMAGE=1, DEPLOY=1, HELM_CHART=./deploy, KNOWN_GOOD_REVISION=<revision>.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "BLOCKED: missing required tool: $1" >&2; exit 2; }
}

need docker
need trivy
need cosign

: "${IMAGE_REPOSITORY:?Set IMAGE_REPOSITORY to an approved OCI repository}"
COMMIT="$(git rev-parse HEAD)"
TAG="${IMAGE_REPOSITORY}:${COMMIT}"
EVIDENCE_DIR="${EVIDENCE_DIR:-$ROOT/.std10g-evidence/$COMMIT}"
mkdir -p "$EVIDENCE_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "BLOCKED: checkout is dirty; use an immutable approved commit" >&2
  exit 2
fi

git rev-parse HEAD > "$EVIDENCE_DIR/source-commit.txt"

echo "[1/8] Build local image from pinned commit"
docker build --pull --label "org.opencontainers.image.revision=$COMMIT" -t "$TAG" . | tee "$EVIDENCE_DIR/build.log"

LOCAL_ID="$(docker image inspect "$TAG" --format '{{.Id}}')"
if [[ -z "$LOCAL_ID" ]]; then
  echo "BLOCKED: Docker returned no local image identity" >&2
  exit 3
fi
printf '%s\n' "$LOCAL_ID" > "$EVIDENCE_DIR/local-image-id.txt"

if command -v syft >/dev/null 2>&1; then
  echo "[2/8] Generate SBOM"
  syft "$TAG" -o cyclonedx-json="$EVIDENCE_DIR/sbom.cdx.json"
else
  echo "BLOCKED: syft is unavailable; SBOM evidence cannot be produced" >&2
  exit 2
fi

DIGEST="$(docker image inspect "$TAG" --format '{{index .RepoDigests 0}}' 2>/dev/null || true)"
if [[ -z "$DIGEST" ]]; then
  echo "[3/8] No registry digest exists locally; push is required before signing the immutable digest"
  if [[ "${PUSH_IMAGE:-0}" != "1" ]]; then
    echo "BLOCKED: set PUSH_IMAGE=1 only in an approved registry-enabled environment" >&2
    exit 2
  fi
  docker push "$TAG" | tee "$EVIDENCE_DIR/push.log"
  DIGEST="$(docker inspect --format '{{index .RepoDigests 0}}' "$TAG")"
fi
printf '%s\n' "$DIGEST" > "$EVIDENCE_DIR/image-digest.txt"

if [[ "$DIGEST" != *"@sha256:"* ]]; then
  echo "BLOCKED: image reference is not immutable: $DIGEST" >&2
  exit 3
fi

if ! grep -q "$DIGEST" "$EVIDENCE_DIR/sbom.cdx.json" 2>/dev/null; then
  echo "WARNING: SBOM subject does not contain the registry digest; review subject binding before release" >&2
fi

echo "[4/8] Sign immutable digest"
cosign sign --yes "$DIGEST" | tee "$EVIDENCE_DIR/sign.log"
echo "[5/8] Verify immutable digest signature"
cosign verify "$DIGEST" | tee "$EVIDENCE_DIR/verify-signature.log"

echo "[6/8] Scan immutable image"
trivy image --exit-code 1 --severity HIGH,CRITICAL --format json --output "$EVIDENCE_DIR/trivy.json" "$DIGEST"

if [[ "${PUSH_IMAGE:-0}" == "1" ]]; then
  echo "[7/8] Push is enabled and was completed before signing/scanning"
else
  echo "[7/8] Push disabled; artifact remains local and cannot be a deployment release"
fi

if [[ "${DEPLOY:-0}" == "1" ]]; then
  need helm
  need kubectl
  : "${HELM_CHART:?Set HELM_CHART for an approved staging chart}"
  : "${KNOWN_GOOD_REVISION:?Set KNOWN_GOOD_REVISION for rollback rehearsal}"
  echo "[8/8] Deploy digest to approved staging and verify rollout"
  helm upgrade --install honestagent "$HELM_CHART" --set image.digest="${DIGEST#*@}" | tee "$EVIDENCE_DIR/deploy.log"
  kubectl rollout status deployment/honestagent | tee "$EVIDENCE_DIR/rollout.log"
  echo "Rollback must be executed manually with the approved runbook and recorded in $EVIDENCE_DIR" >&2
else
  echo "[8/8] Deployment disabled; no cluster was contacted"
fi

echo "STD-10G local run completed as far as configured. Review evidence under $EVIDENCE_DIR."
