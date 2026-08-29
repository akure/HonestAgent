# Change Log — B-6 enterprise policy governance

Added signed policy records, configurable approval quorum, and an optional mandatory simulation-before-activation gate. The changes address the prior failure mode where a file-backed policy could be modified after import or activated after only a single approval without recorded simulation evidence.

Evidence: 76 tests pass, including quorum enforcement, simulation-gate enforcement, rollback compatibility, and tamper detection. Production customer IAM, signing-key custody, and deployment rollback evidence remain `NOT MEASURED`; the release remains `NO-GO` for unrestricted production.
