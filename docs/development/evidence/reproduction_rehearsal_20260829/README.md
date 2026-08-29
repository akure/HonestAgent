# Clean-Checkout Reproduction Rehearsal

**Status: REHEARSAL — not independent third-party evidence.**

The repository was freshly cloned and checked out at commit `0d67f436e74f2c3d2d38cd98ef8ff4d3287d3621`. The author-controlled environment then created a clean virtual environment, installed `requirements.txt`, and ran the documented tests, benchmark, and deep evaluation commands.

This confirms that the documented procedure works from a fresh checkout, but it does **not** qualify as independent reproduction because the run was initiated and observed by the project author. The benchmark and deep-evaluation JSON files are retained for handoff to an independent reviewer.

Observed results:

- Full test command completed successfully; the repository currently contains 81 tests.
- Benchmark: baseline caught `0/10`; solution caught `10/10` unsafe cases.
- Deep evaluation: `20/20` unsafe intercepted and `20/20` safe allowed.
- Rehearsal latency is hardware-dependent and must not be compared as a guaranteed target.
