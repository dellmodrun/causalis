# CAUSALIS

CAUSALIS is a usable, local-first mandate auditor and downloadable Agent Skill for autonomous-capital agents. The browser tool validates user-supplied JSON against the published schema and twelve deterministic rules. It does not connect wallets, upload mandates, infer missing controls, or produce financial safety scores.

## Live site

`https://dellmodrun.github.io/causalis/`

## Local URL

`http://localhost:4189/causalis/`

## Pages

- `/`
- `/theory/`
- `/audit/`
- `/research/`
- `/method/`
- `/faq/`
- `/token/`

## Run

```powershell
node server.mjs
```

The site is served from `site/`. GitHub Actions deploys that directory to GitHub Pages and creates direct-entry files for every public route. The Skill package, schema, rule registry, and blank mandate template are under `site/downloads/causalis-audit/`.

## Use the auditor

Open `/audit/`, then paste JSON, open a local file, load the passing example, or load the blank template. A completed report includes schema issues, all twelve rule results, exact field paths, a timestamp, the input byte count, an SHA-256 fingerprint of the exact submitted document, and the verification boundary. Reports can be exported as JSON. Press `Ctrl+Enter` or `Cmd+Enter` to run an audit from the editor.

## Use the Skill locally

Download `site/downloads/causalis-audit.zip` and extract it into a compatible agent's Skill directory. The package includes a dependency-free CLI:

```powershell
python scripts/audit_mandate.py examples/valid.mandate.json
python scripts/audit_mandate.py path\to\mandate.json --output audit-report.json
```

The CLI performs no network requests and never asks for wallet access or private material.

The published v0.1 ZIP is 5,486 bytes. Its SHA-256 checksum is:

```text
27d1fbe3624bd48c4a6a7545ece6dca7f9717e8cf0a40ae9dd6b8b634dd1d435
```

## Verification boundary

A passing result means the supplied document declares the checked controls. It does not prove that deployed code enforces them, establish program ownership, certify financial safety, or predict an outcome.
