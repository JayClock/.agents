# Scoped Security Review

Use this reference when `/check` reviews authentication, authorization, command execution, filesystem paths, network egress, URL handling, rendering, secrets, or other trust-boundary changes.

## Review Standard

Report fewer findings with stronger evidence. A valid security finding must have:

- An untrusted or lower-trust input source.
- A sensitive sink or privileged action.
- A reachable path from source to sink.
- Existing guardrails identified, even when they are insufficient.
- A concrete impact and a specific fix.

Suppress broad hardening advice, style issues, and theoretical vulnerabilities without reachability.

## Authentication and Authorization

Look for:

- API, tool, route, or job entrypoints missing identity checks.
- Privileged actions without role, tenant, ownership, or workspace scoping.
- Session, token, or callback handling regressions.
- Bypass flags, debug modes, or allow-all fallbacks reachable outside tests.

Finding shape:

```text
[SEVERITY] file:line -- auth/authz boundary weakened
Attack path: external/user-controlled entry -> missing or weakened check -> privileged action
Guardrails present: ...
Fix: ...
Class: security
Autofix: manual
```

## Command and Process Execution

Look for:

- Shell execution with interpolated input.
- Process spawning where user input controls executable, flags, cwd, env, or file paths.
- Container, sandbox, or local tool control paths exposed through user-triggered actions.
- Validation that only checks UI or caller side, not the execution boundary.

Prefer root-cause findings. Group related variants under one finding instead of reporting every call site separately.

## SSRF and Network Egress

Look for:

- Fetch/proxy/client code where untrusted input controls full URL, host, scheme, base URL, redirect target, or headers.
- Access to localhost, private networks, metadata endpoints, internal service names, or file-like schemes.
- Missing scheme allowlists, host allowlists, DNS/IP range checks, redirect restrictions, or timeout/size limits.

Only report when the changed code introduces or materially widens the reachable network sink.

## Output Rule

For each security finding, include:

- `root cause`
- `affected locations`
- `attack path`
- `why it matters`
- `guardrails present`
- `recommended fix`
- `confidence`

If the path is not provable from the diff and nearby context, downgrade to a risk note or suppress it.
