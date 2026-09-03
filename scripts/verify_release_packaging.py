#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from honest_agent.ops.release_packaging import verify_release_inputs  # noqa: E402


if __name__ == "__main__":
    print(json.dumps(verify_release_inputs(ROOT), indent=2, sort_keys=True))
