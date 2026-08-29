from __future__ import annotations

import fcntl
import json
import os
import re
import time
from pathlib import Path
from typing import Iterable, Mapping

from honest_agent.core.policy import ActionPolicy
from honest_agent.ops.pmf import PolicySimulation, simulate_policy
from honest_agent.schemas.models import EvaluationRequest, PolicyRule


class PolicyRegistryError(ValueError):
    pass


_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class PolicyRegistry:
    """Durable customer policy lifecycle: draft, approve, activate, and rollback."""

    def __init__(self, path: str = "policies/registry.json"):
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"active_version": "default-v1", "versions": {}}
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            state.setdefault("active_version", "default-v1")
            state.setdefault("versions", {})
            return state
        except (OSError, json.JSONDecodeError) as exc:
            raise PolicyRegistryError("policy registry is unreadable") from exc

    def _write(self, state: dict) -> None:
        temp = self.path.with_suffix(self.path.suffix + f".{os.getpid()}.tmp")
        temp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temp, self.path)

    def _transaction(self):
        self.lock_path.touch(exist_ok=True)
        return self.lock_path.open("r+")

    @staticmethod
    def _validate_version(version: str) -> None:
        if not _VERSION_RE.fullmatch(version):
            raise PolicyRegistryError("policy version must be 1-64 safe identifier characters")

    @staticmethod
    def _normalize_rules(rules: Mapping[str, PolicyRule | Mapping]) -> dict[str, dict]:
        if not rules:
            raise PolicyRegistryError("policy must define at least one tool rule")
        normalized: dict[str, dict] = {}
        for tool_name, rule in rules.items():
            if not tool_name.strip() or len(tool_name) > 128:
                raise PolicyRegistryError("tool names must be non-empty and at most 128 characters")
            model = rule if isinstance(rule, PolicyRule) else PolicyRule.model_validate(rule)
            normalized[tool_name] = model.model_dump(mode="json")
        return normalized

    def import_policy(self, version: str, rules: Mapping[str, PolicyRule | Mapping], imported_by: str) -> dict:
        self._validate_version(version)
        if not imported_by.strip():
            raise PolicyRegistryError("importer identity is required")
        normalized = self._normalize_rules(rules)
        with self._transaction() as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            state = self._load()
            if version in state["versions"]:
                raise PolicyRegistryError("policy version already exists")
            record = {"version": version, "rules": normalized, "imported_by": imported_by, "imported_at": time.time(), "approved_by": [], "active": False}
            state["versions"][version] = record
            self._write(state)
            self._state = state
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            return record

    def approve(self, version: str, reviewer: str) -> dict:
        if not reviewer.strip():
            raise PolicyRegistryError("approver identity is required")
        with self._transaction() as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            state = self._load()
            record = state["versions"].get(version)
            if record is None:
                raise PolicyRegistryError("unknown policy version")
            if reviewer not in record["approved_by"]:
                record["approved_by"].append(reviewer)
            self._write(state)
            self._state = state
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            return record

    def activate(self, version: str, actor: str) -> ActionPolicy:
        if not actor.strip():
            raise PolicyRegistryError("activation identity is required")
        with self._transaction() as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            state = self._load()
            record = state["versions"].get(version)
            if record is None:
                raise PolicyRegistryError("unknown policy version")
            if not record["approved_by"]:
                raise PolicyRegistryError("policy must be approved before activation")
            previous = state.get("active_version")
            for item in state["versions"].values():
                item["active"] = False
            record["active"] = True
            record["activated_by"] = actor
            record["activated_at"] = time.time()
            record["previous_active_version"] = previous
            state["active_version"] = version
            self._write(state)
            self._state = state
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            return ActionPolicy({name: PolicyRule.model_validate(rule) for name, rule in record["rules"].items()}, version=version)

    def rollback(self, version: str, actor: str) -> ActionPolicy:
        if version == self.active_version:
            raise PolicyRegistryError("rollback target must differ from active version")
        return self.activate(version, actor)

    @property
    def active_version(self) -> str:
        self._state = self._load()
        return self._state["active_version"]

    def get_policy(self, version: str | None = None) -> ActionPolicy:
        selected = version or self.active_version
        if selected == "default-v1" and selected not in self._state.get("versions", {}):
            return ActionPolicy(version="default-v1")
        self._state = self._load()
        record = self._state["versions"].get(selected)
        if record is None:
            raise PolicyRegistryError("unknown policy version")
        return ActionPolicy({name: PolicyRule.model_validate(rule) for name, rule in record["rules"].items()}, version=selected)

    def simulate(self, requests: Iterable[EvaluationRequest], version: str | None = None) -> PolicySimulation:
        return simulate_policy(requests, self.get_policy(version))
