# Change Log — CP-2 provider reliability

No application code was changed. The existing provider evidence runner was executed and produced a redacted `NOT_MEASURED` artifact because approved live-provider configuration was unavailable. Local provider and adversarial tests passed 12 tests.

The runner’s fail-closed precondition prevented a credential-less network attempt. Live endpoint, provider model, latency distribution, timeout/retry/cancellation matrix, and operator approval remain target-environment evidence requirements.
