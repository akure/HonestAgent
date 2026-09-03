from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any, Iterable


REQUIRED_FILES = ("Dockerfile", "pyproject.toml", "requirements.txt", "LICENSE", "SECURITY.md")
PACKAGING_TOOLS = ("docker", "podman", "syft", "trivy", "grype", "pip-audit")
STD10G_TOOLS = ("docker", "podman", "syft", "cosign", "trivy", "grype", "pip-audit", "kubectl", "helm")


def source_manifest_hash(root: str | Path, files: Iterable[str] | None = None) -> str:
    """Hash named release inputs in a deterministic order; do not include secrets or build output."""
    base = Path(root)
    selected = sorted(files or REQUIRED_FILES)
    digest = hashlib.sha256()
    for relative in selected:
        path = base / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def verify_release_inputs(root: str | Path) -> dict[str, Any]:
    base = Path(root)
    missing = [relative for relative in REQUIRED_FILES if not (base / relative).is_file()]
    dockerfile = (base / "Dockerfile").read_text(encoding="utf-8") if (base / "Dockerfile").is_file() else ""
    safe_markers = {
        "non_root_user": "USER honestagent" in dockerfile,
        "pinned_dependency_manifest": (base / "requirements.txt").is_file() and (base / "pyproject.toml").is_file(),
        "no_privileged_runtime_user": "USER root" not in dockerfile,
    }
    tools = {tool: shutil.which(tool) is not None for tool in PACKAGING_TOOLS}
    return {
        "report_version": "std10f-v1",
        "required_files": {"missing": missing, "pass": not missing},
        "source_manifest_sha256": None if missing else source_manifest_hash(base),
        "dockerfile_safety": safe_markers,
        "packaging_tools": tools,
        "image_build": "NOT_RUN" if not (tools["docker"] or tools["podman"]) else "AVAILABLE_NOT_RUN",
        "sbom": "NOT_RUN" if not tools["syft"] else "AVAILABLE_NOT_RUN",
        "vulnerability_scan": "NOT_RUN" if not (tools["trivy"] or tools["grype"] or tools["pip-audit"]) else "AVAILABLE_NOT_RUN",
        "claims": {"production_ready": False, "safety_certified": False, "commercial_entitlement": False},
    }


def verify_std10g_prerequisites() -> dict[str, Any]:
    """Return a conservative gate; never run a partial release workflow."""
    tools = {tool: shutil.which(tool) is not None for tool in STD10G_TOOLS}
    missing = [tool for tool, available in tools.items() if not available]
    builder = tools["docker"] or tools["podman"]
    scanner = tools["trivy"] or tools["grype"] or tools["pip-audit"]
    return {
        "gate_version": "std10g-v1",
        "tools": tools,
        "required_capabilities": {
            "image_builder": builder,
            "sbom_generator": tools["syft"],
            "image_signer": tools["cosign"],
            "vulnerability_scanner": scanner,
            "deployment_client": tools["kubectl"] or tools["helm"],
        },
        "missing_tools": missing,
        "status": "READY" if not missing else "BLOCKED",
        "action": "NO_RELEASE_EXECUTION" if missing else "REQUIRES_APPROVED_TARGET_AND_CREDENTIALS",
    }


__all__ = ["PACKAGING_TOOLS", "REQUIRED_FILES", "STD10G_TOOLS", "source_manifest_hash", "verify_release_inputs", "verify_std10g_prerequisites"]
