# Security Policy

## Scope

Honest Agent is a safety boundary for AI agent tool calls. The most serious issues are those that allow an action to bypass policy, execute after a rejected checkpoint, fail open after verifier failure, or produce an audit record that misrepresents the decision.

## Reporting

Please do not disclose exploitable details in a public issue. Report security concerns privately to the maintainers with reproduction steps, affected version, impact, and a minimal fixture. Do not include secrets or customer data; sanitize all traces before sharing.

## Deployment warning

The development server is not a security boundary. Before production use, add authentication, reviewer authorization, durable shared state, append-only audit storage, data retention controls, provider-failure handling, and network isolation. The project does not guarantee that a model verifier detects every unsafe action.
