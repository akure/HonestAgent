# Security Policy

## Scope

HonestAgent is a pre-execution safety boundary for AI-agent tool calls. The highest-severity issues are those that allow an action to bypass deterministic policy, execute after rejection or without an authorized handoff, fail open after verifier/provider failure, expose credentials or sensitive payloads, corrupt checkpoint or audit state, or misrepresent the decision trajectory.

The repository is currently **NO-GO for unrestricted production**. Local tests and offline evaluation do not establish live-provider, enterprise-identity, container, host, network, monitoring, backup, or kill-switch readiness. Consult the release evidence and production-readiness documents before deployment.

## Supported versions

| Version / branch | Security-fix status |
|---|---|
| `main` | Best-effort fixes while the project is under active development |
| Tagged releases | Support status is defined by the applicable commercial or release notice |
| Unmodified historical commits | No guaranteed security maintenance |

## Reporting a vulnerability

Do not disclose exploitable details in a public issue, pull request, discussion, or chat. Use GitHub’s private vulnerability-reporting flow when enabled: <https://github.com/akure/HonestAgent/security/advisories/new>. If that flow is unavailable, contact the repository owner through <https://github.com/akure/HonestAgent> and request a private security channel.

Include a concise description and severity estimate, affected commit/release/component, reproduction steps or a minimal sanitized fixture, security impact, and any suggested mitigation. Never include live credentials, private keys, customer data, personal data, or unredacted trajectories. Replace them with synthetic values and revoke any credential accidentally disclosed.

## Response process

The maintainers will acknowledge a report when reasonably practicable, validate the reproduction, assess impact, coordinate a fix or mitigation, and communicate a disclosure decision. Timelines may vary because this is an early project and not a guaranteed 24×7 security service. Commercial customers receive the response commitments stated in their signed agreement.

Do not publicly disclose a vulnerability until a fix, mitigation, or coordinated disclosure decision is agreed with the maintainers. Do not use the issue-reporting channel to request account support, billing changes, license permissions, or general product help.

## Deployment security requirements

Before enabling real side effects, operators must provide authentication, reviewer authorization, managed secret injection and rotation, durable shared checkpoint storage, append-only or immutable audit storage, retention controls, provider-failure handling, request-size limits, network isolation, DNS-rebinding and TLS controls, container and host hardening, backup/restore evidence, monitoring, alerting, an incident procedure, and a tested emergency disable or kill-switch path.

Consequential or irreversible actions must remain behind deterministic policy and an explicit qualified human approval checkpoint. The model verifier may inform a decision but must not directly authorize an irreversible action. Do not log secrets, raw credentials, unnecessary personal data, or full sensitive provider payloads.

## Security claims and evidence

Every security or evaluation claim must identify its fixture set, configuration, environment, source commit, and retained evidence artifact. Offline synthetic tests are useful regression evidence but are not evidence of production security, live-provider reliability, or compliance certification.

## Third-party dependencies

Review dependency licenses and security advisories before distribution. Run the pinned dependency audit and retain its output with each release candidate. Third-party components remain subject to their original licenses.
