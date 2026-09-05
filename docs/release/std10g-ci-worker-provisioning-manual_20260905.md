# STD-10G CI Worker Provisioning Manual

**Audience:** HonestAgent maintainers, release engineers, and pilot operators  
**Purpose:** Provision a disposable worker with Docker, Trivy, Cosign, and Syft, then generate real STD-10G release evidence  
**Platforms:** Ubuntu/Debian Linux, Fedora/RHEL-family Linux, Windows 11, and macOS Intel/Apple Silicon  
**Evidence boundary:** A local laptop can generate build, SBOM, signature, and scan evidence. It cannot by itself establish production deployment, registry governance, enterprise key custody, operational monitoring, or rollback readiness.

## 1. Executive decision

The current sandbox cannot complete STD-10G because Docker, Trivy, Cosign, Syft, Helm, and kubectl are unavailable. The repository’s runbook correctly stops at the first missing prerequisite and reports `BLOCKED`.

The cleanest path is to provision one of the following:

| Option | Best use | What it can prove |
|---|---|---|
| Linux CI runner | Preferred release evidence path | Reproducible build, SBOM, signature, scan, registry and staging integration |
| Windows or macOS laptop with Docker Desktop | Developer or controlled rehearsal | Build, SBOM, signing, scan, and optionally registry evidence |
| Local laptop with disposable test registry | Offline or isolated validation | Toolchain and artifact binding; not production authorization |
| Production-like CI/staging worker | Required for final STD-10G and pilot gate | Full target-like release and deployment evidence |

Do not treat a laptop run as production approval. Treat it as a signed evidence-generation run that still requires independent review and target-environment sign-off.

## 2. Required architecture

Use a clean checkout and an ephemeral worker. The worker needs outbound access to the approved container registry, vulnerability database endpoints, Sigstore services if using keyless signing, and the source repository. It must not contain long-lived registry passwords or private signing keys in shell history, source files, or logs.

The minimum toolchain is:

| Component | Role | Required validation |
|---|---|---|
| Docker Engine or Docker Desktop | Build and inspect OCI image | `docker version`, `docker info` |
| Syft | Generate image SBOM | `syft version` |
| Cosign | Sign and verify immutable image digest | `cosign version` |
| Trivy | Scan image and dependency inputs | `trivy --version` |
| Git | Pin source commit and record provenance | `git --version` |
| Registry | Store and retrieve immutable digest | Push/pull and digest equality |
| Optional Helm/kubectl | Staging deployment and rollback rehearsal | Client version and authenticated target check |

Pin versions in CI. Do not use floating `latest` tags for the release worker or scanner image. Docker’s official installation documentation covers Docker Desktop and Docker Engine platform choices.[1] Trivy’s official documentation lists supported installation methods, including packages, Homebrew, Windows archives, and official container images.[2] Sigstore documents Cosign installation and release verification.[3] Syft’s official project documentation covers SBOM generation and installation options.[4]

## 3. Prepare the repository

Clone the repository and switch to the approved commit. The checkout must be clean before the runbook starts.

```bash
git clone https://github.com/akure/HonestAgent.git
cd HonestAgent
git fetch --tags origin
git checkout <APPROVED_COMMIT>
git status --short --branch
git rev-parse HEAD
```

The final `git status` must show no uncommitted changes. Record the commit hash in the release ticket before starting. Do not run the release procedure from a branch containing local edits.

## 4. Linux provisioning

### 4.1 Ubuntu or Debian

For a CI worker, prefer Docker Engine installed from Docker’s official repository rather than an unofficial distribution package. Follow the current Docker Engine instructions for the exact operating-system release. After installation, enable and start Docker:

```bash
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Start a new login session after the group change. Then validate the daemon:

```bash
docker version
docker info
sudo docker run --rm hello-world
```

For a one-time CI worker, running Docker commands through `sudo` is acceptable if the CI service account is deliberately configured. Avoid granting the Docker socket to untrusted users because access to the socket is effectively host-level control.

Install Trivy from its official Debian repository or a pinned release package. The repository method is documented by Trivy and should be preferred for managed workers.[2]

```bash
sudo apt-get update
sudo apt-get install -y wget gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/trivy.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" \
  | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install -y trivy
trivy --version
```

Install Syft using a pinned release or the official Anchore installation method. Inspect the installer or verify the downloaded release checksum before placing the binary in a system path.[4]

```bash
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
syft version
```

For a controlled enterprise worker, replace the convenience installer with an internally mirrored, checksum-verified release artifact.

Install Cosign from a pinned official release binary, package, or Homebrew. Verify the Cosign release before use, following Sigstore’s documented release-verification process.[3]

```bash
# Prefer the official release instructions for the selected pinned version.
# After installation:
cosign version
```

Do not use `go install ...@latest` in a reproducible release job. If Go installation is used for local development, pin the Cosign module version and record it.

### 4.2 Fedora, RHEL, or compatible distributions

Install Docker Engine using Docker’s official RPM instructions, then enable the daemon:

```bash
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Install Trivy from its official RPM repository or pinned RPM package. Install Syft and Cosign from verified pinned release artifacts. Validate every tool:

```bash
docker version
docker info
trivy --version
syft version
cosign version
```

The exact package commands vary by distribution version. Use the vendor documentation linked in the References section rather than copying an unverified third-party repository configuration.

## 5. Windows provisioning

### 5.1 Install Docker Desktop

Install Docker Desktop for Windows from Docker’s official distribution. Use the WSL 2 backend unless the organization has approved an alternative. Enable hardware virtualization in UEFI/BIOS if Docker Desktop reports that virtualization is unavailable.[1]

After installation, open Docker Desktop and wait until the engine reports that it is running. In PowerShell, validate:

```powershell
docker version
docker info
docker run --rm hello-world
```

Use a Git checkout inside the WSL 2 Linux filesystem when running the Bash-based HonestAgent script. This avoids path and file-permission differences common with mounted Windows paths.

### 5.2 Install WSL 2 and tools

From an elevated PowerShell prompt:

```powershell
wsl --install -d Ubuntu
wsl --update
```

Open Ubuntu from the Start menu, then follow the Ubuntu/Debian Linux provisioning steps in Section 4. Docker Desktop must have WSL integration enabled for that distribution.

Alternatively, install the Windows Trivy and Syft archives and add their directories to `PATH`. Trivy documents Windows release archives as an official installation method.[2] Syft documents Windows package-manager and release options in its installation documentation.[4]

Install Cosign using a pinned Windows release binary or an approved package-manager distribution. Verify the release before use according to Sigstore’s release-verification guidance.[3]

Validate from WSL or PowerShell, depending on where the runbook will execute:

```powershell
docker version
trivy --version
syft version
cosign version
git --version
```

If the Bash runbook is used inside WSL, all four executable tools must be visible inside WSL. A tool installed only in Windows `PATH` may not be visible in the WSL environment.

## 6. macOS provisioning

### 6.1 Install Docker Desktop

Install Docker Desktop for the correct architecture: Apple Silicon or Intel. Start Docker Desktop and wait for the engine to become ready. Validate:

```bash
docker version
docker info
docker run --rm hello-world
```

On Apple Silicon, build for the target deployment architecture when necessary. If the target is Linux AMD64, use BuildKit platform selection and record the platform in the release evidence:

```bash
docker buildx build --platform linux/amd64 --load -t <local-tag> .
```

Do not silently mix an ARM64 laptop image with an AMD64 production target.

### 6.2 Install tools with Homebrew

Install Homebrew from its official source if it is not already present. Then install Trivy and Cosign through approved, pinned formulas where available:

```bash
brew install trivy cosign
trivy --version
cosign version
```

Install Syft using its official release method or an approved Homebrew formula if available:

```bash
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
syft version
```

On Apple Silicon, `/opt/homebrew/bin` is commonly used. Confirm the actual paths:

```bash
command -v docker trivy cosign syft git
```

## 7. Provision registry access safely

STD-10G signs an immutable digest. A local image tag is not sufficient because Docker may not provide a registry digest until the image is pushed to an OCI registry.

Create a dedicated repository in an approved registry. Use a short-lived token with only the permissions required to push and read the image. Store the token in the platform’s secret manager or a temporary environment injection. Do not commit it or place it in a script.

Log in without writing credentials into shell history where the registry supports token-based login:

```bash
echo "$REGISTRY_TOKEN" | docker login "$REGISTRY_HOST" \
  --username "$REGISTRY_USER" --password-stdin
```

Use a repository name such as:

```text
registry.example/honestagent
```

The final evidence must bind all of the following to one digest:

| Artifact | Required subject |
|---|---|
| Image | `registry.example/honestagent@sha256:<digest>` |
| SBOM | Exact image digest or a clearly verified image identity |
| Signature | Exact image digest |
| Vulnerability report | Exact image digest and scan timestamp |
| Deployment manifest | Exact digest, not a mutable tag |

## 8. Validate the toolchain before building

Run this preflight from the clean checkout:

```bash
set -euo pipefail

git status --short --branch
git rev-parse HEAD
docker version
trivy --version
syft version
cosign version
```

Then perform a harmless local test:

```bash
docker run --rm alpine:3.20 /bin/sh -c 'printf healthy'
trivy image --download-db-only
```

The Trivy database download may require outbound network access and can take time. Capture the Trivy version and database status in the evidence bundle. Do not silently use an old vulnerability database when the release policy requires freshness.

## 9. Run the HonestAgent STD-10G runbook

Set the approved repository and run without deployment first:

```bash
export IMAGE_REPOSITORY="registry.example/honestagent"
export EVIDENCE_DIR="$PWD/.std10g-evidence/$(git rev-parse HEAD)"

./scripts/run_std10g_local.sh
```

The runbook performs the following sequence:

1. Checks Docker, Trivy, and Cosign.
2. Requires `IMAGE_REPOSITORY`.
3. Requires a clean checkout.
4. Builds the image with the source revision label.
5. Inspects the local image identity.
6. Requires Syft and generates a CycloneDX SBOM.
7. Requires an immutable registry digest; it stops unless `PUSH_IMAGE=1` is explicitly enabled.
8. Signs and verifies the digest with Cosign.
9. Scans the digest with Trivy for HIGH and CRITICAL findings.
10. Leaves deployment disabled unless `DEPLOY=1` is explicitly configured.

The current repository runbook should be reviewed before use because the SBOM subject-binding warning is intentionally conservative. A warning is not a release pass. If the generated SBOM does not clearly bind to the final registry digest, stop and fix the evidence workflow before approval.

For an approved registry-enabled run:

```bash
export PUSH_IMAGE=1
./scripts/run_std10g_local.sh
```

Do not enable `PUSH_IMAGE=1` on a personal registry or unapproved account and then treat the result as pilot evidence.

## 10. Optional staging deployment rehearsal

Deployment requires a separate approved target and is not established by local Docker alone. Provision Helm and kubectl, authenticate to the isolated staging cluster using short-lived credentials, and validate the current context before deploying:

```bash
helm version
kubectl version --client
kubectl config current-context
kubectl auth can-i get deployments
```

Set the deployment variables only after the target owner approves them:

```bash
export DEPLOY=1
export HELM_CHART=./deploy
export KNOWN_GOOD_REVISION=<approved-known-good-revision>
./scripts/run_std10g_local.sh
```

The runbook records deployment and rollout output but does not automatically perform rollback. Execute rollback through the approved deployment procedure and record:

- The deployed digest.
- The known-good digest or revision.
- Rollback start and completion timestamps.
- Health-check result.
- Whether any protected side effect occurred during the failure.
- The owner who authorized and verified rollback.

## 11. Cosign signing modes

Choose one approved signing mode before the run:

| Mode | Appropriate use | Governance requirement |
|---|---|---|
| Keyless signing | CI with approved OIDC identity | Verify certificate identity and issuer; retain transparency-log evidence |
| KMS-backed key | Enterprise release pipeline | Restrict signing role; audit key use; rotate under policy |
| Local key pair | Development or isolated test only | Never treat a personal local key as enterprise release authority |

For a local test, use a disposable key only if the evidence is explicitly labeled as test evidence. For a pilot, use keyless or KMS-backed signing under the organization’s approved identity and key-custody policy.

Never use `cosign sign --yes` against an image that is not the approved digest. Confirm the exact digest before signing and verify the same digest afterward.

## 12. Evidence bundle contents

Preserve the following files under an immutable evidence location:

```text
source-commit.txt
worker-platform.txt
tool-versions.txt
build.log
image-digest.txt
local-image-id.txt
sbom.cdx.json
sign.log
verify-signature.log
trivy.json
push.log
deploy.log
rollout.log
rollback.log
release-decision.md
```

Generate tool and platform metadata before the run:

```bash
{
  uname -a 2>/dev/null || ver
  git rev-parse HEAD
  docker version
  trivy --version
  syft version
  cosign version
} > "$EVIDENCE_DIR/tool-versions.txt" 2>&1
```

Hash the evidence bundle after completion:

```bash
find "$EVIDENCE_DIR" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "$EVIDENCE_DIR/evidence-manifest.sha256"
```

The release owner must review the manifest and verify that all artifact subjects refer to the same immutable image digest.

## 13. Troubleshooting decision tree

| Symptom | Correct response |
|---|---|
| `BLOCKED: missing required tool: docker` | Install/start Docker; do not create a fake executable. |
| Docker daemon unavailable | Start Docker Desktop or the Docker service; verify `docker info`. |
| `syft is unavailable` | Install and verify Syft; no SBOM means no release evidence. |
| No `RepoDigests` value | Use an approved registry and explicitly enable push; do not sign a mutable tag. |
| Cosign login or certificate failure | Stop; fix identity/key policy; do not bypass verification. |
| Trivy database unavailable | Restore approved network/cache access; record database freshness. |
| HIGH/CRITICAL findings | Apply the approved exception process or fix the image; do not suppress findings silently. |
| Architecture mismatch | Rebuild for the target platform and record `--platform`. |
| Dirty checkout | Reset or reclone; rebuild only from the approved commit. |
| Deployment health failure | Stop rollout, activate the kill switch if required, and rehearse rollback. |

## 14. Completion criteria for STD-10G

STD-10G is complete only when all of the following are true:

1. The approved commit is recorded.
2. The image is built and pushed to the approved registry.
3. The final image digest is immutable and recorded.
4. The SBOM describes the final image digest and is retained.
5. Cosign signature verification succeeds under approved policy.
6. Trivy and dependency scans complete with no unresolved blocking findings.
7. The digest can be pulled and verified from the registry.
8. The digest-pinned deployment succeeds in an approved production-like staging target.
9. Kill-switch, alerting, health, and rollback drills pass.
10. The evidence bundle is hashed, stored immutably, independently reviewed, and signed off by the release, security, platform, and accountable business owners.

A local laptop can satisfy items 1–7 if it has approved registry and signing access. Items 8–10 require target-like infrastructure and accountable operational ownership.

## 15. Security and licensing cautions

Docker Desktop may have commercial subscription requirements for larger organizations; verify the applicable Docker terms before using it for enterprise work.[1] Do not copy private registry credentials into `.env` files that can be committed. Do not use production signing keys on a personal device. Do not upload proprietary source or SBOM data to an unapproved service. Do not claim a conditional pilot or production release based solely on local or mock results.

## References

[1]: https://docs.docker.com/desktop/setup/install/ "Docker official installation overview"
[2]: https://trivy.dev/docs/latest/getting-started/installation/ "Trivy official installation documentation"
[3]: https://docs.sigstore.dev/cosign/system_config/installation/ "Sigstore Cosign official installation and verification documentation"
[4]: https://github.com/anchore/syft "Anchore Syft official project and installation guidance"
[5]: https://docs.docker.com/engine/install/ "Docker Engine official installation documentation"
[6]: https://github.com/akure/HonestAgent/blob/main/scripts/run_std10g_local.sh "HonestAgent STD-10G local runbook"
