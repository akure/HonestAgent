# Change Log — CP-3 durable storage and recovery

No application code was changed. The existing storage controls were exercised as a target-environment evidence sprint. Eight tests passed for restart survival, compare-and-set concurrency, backup/restore, retention pruning, and durable webhook checkpoint behavior.

Production topology, failover, backup target, restore RTO/RPO, and retention/legal-hold controls remain `NOT MEASURED`; CP-3 is recorded as `PARTIAL`.
