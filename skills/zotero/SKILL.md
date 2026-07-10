---
name: zotero
description: Operate a local Zotero Desktop library through Zotero's local API and Connector server. Search items, collections, and tags; export or synchronize BibTeX; insert citation keys into LaTeX or Markdown; retrieve requested attachment metadata or indexed full text; and import BibTeX/RIS records with explicit confirmation. Proactively use this skill whenever the user mentions Zotero, a local citation library, references.bib, BibTeX export, localhost:23119, citation insertion, or importing references into Zotero.
compatibility: Requires Python 3, command execution access, and Zotero Desktop on the same machine. The helper uses only the Python standard library and Zotero's loopback HTTP endpoints.
---

# Zotero

Use this skill to work with a user's local Zotero Desktop library without depending on a specific agent product or plugin runtime.

## Helper location

The command-line helper is bundled with this skill:

```bash
python3 <skill-dir>/scripts/zotero.py <command>
```

Resolve `<skill-dir>` as the directory containing this `SKILL.md`. Do not assume a fixed installation root, home-directory layout, plugin directory, or agent-specific environment variable.

The helper is dependency-free and communicates only with Zotero Desktop's local HTTP services at `http://127.0.0.1:23119` by default. Override the endpoint with `ZOTERO_LOCAL_BASE_URL` when necessary.

## Fast starts

Check readiness first:

```bash
python3 <skill-dir>/scripts/zotero.py status --json
```

Enable the local API and restart Zotero when needed:

```bash
python3 <skill-dir>/scripts/zotero.py enable --restart
```

Search and export citation data:

```bash
python3 <skill-dir>/scripts/zotero.py search "transformer" --json
python3 <skill-dir>/scripts/zotero.py export-bibtex --out references.bib
```

Insert a citation into a draft and keep `references.bib` synchronized:

```bash
python3 <skill-dir>/scripts/zotero.py cite --query "Attention Is All You Need" --tex paper.tex --bib references.bib --marker '<cite>'
```

## Workflow

1. Run `status --json` before other operations. Use the helper's detected profile, preference, API, and Connector status instead of manually guessing ports or profile paths.
2. If `local_api_enabled_pref` is false and the user asked to operate the local library, run `enable --restart`. The helper backs up `prefs.js` before changing the preference.
3. Prefer read-only commands for discovery and normal research work:
   - `inventory` for item summaries.
   - `collections`, `tags`, and `groups` for library organization.
   - `search <query>` for matching top-level items.
   - `export-bibtex` or `sync-bib` for bibliography files.
   - `citations` for rendered citation text.
4. Use `cite` only when the user wants a LaTeX or Markdown file edited. Report both the edited draft and bibliography file.
5. Retrieve attachment file URLs or indexed full text only when the user explicitly asks for attachment paths, PDFs, or full-text content, because these operations can expose local paths or document contents.
6. Treat `import-bibtex`, `import-ris`, and other Connector writes as Zotero library modifications. Confirm the exact source and selected destination unless the user already gave an explicit import instruction.
7. If command execution, loopback networking, Zotero Desktop, or the local API is unavailable, state the exact blocker instead of inventing library results.

## Common commands

```bash
# Readiness and route map
python3 <skill-dir>/scripts/zotero.py status --json
python3 <skill-dir>/scripts/zotero.py probe --json

# Library inventory
python3 <skill-dir>/scripts/zotero.py inventory
python3 <skill-dir>/scripts/zotero.py collections
python3 <skill-dir>/scripts/zotero.py tags
python3 <skill-dir>/scripts/zotero.py groups

# Search and export
python3 <skill-dir>/scripts/zotero.py search "BERT"
python3 <skill-dir>/scripts/zotero.py search "BERT" --with-bibtex-keys --json
python3 <skill-dir>/scripts/zotero.py export-bibtex --out references.bib
python3 <skill-dir>/scripts/zotero.py export-bibtex --item-key PXW99EKT
python3 <skill-dir>/scripts/zotero.py citations --style apa --json

# Draft editing
python3 <skill-dir>/scripts/zotero.py cite --item-key PXW99EKT --tex paper.tex --bib references.bib --marker '<cite>'
python3 <skill-dir>/scripts/zotero.py cite --query "BERT" --markdown notes.md --bib references.bib --marker '<cite>'

# Attachments and full text; use only on request
python3 <skill-dir>/scripts/zotero.py children PXW99EKT --json
python3 <skill-dir>/scripts/zotero.py fulltext 2JAZS9U8 --out attention-fulltext.txt
python3 <skill-dir>/scripts/zotero.py file-url 2JAZS9U8

# Writes to Zotero; confirm unless the request is already explicit
python3 <skill-dir>/scripts/zotero.py selected-target --json
python3 <skill-dir>/scripts/zotero.py import-bibtex --file new-reference.bib --yes
python3 <skill-dir>/scripts/zotero.py import-ris --file new-reference.ris --yes
```

## Output standards

- For inventory and search results, include title, creators, year, Zotero item key, and BibTeX key when requested or available.
- Explain the distinction when relevant: a Zotero item key such as `PXW99EKT` is not the same as an exported BibTeX key such as `vaswani_attention_2023`.
- For `.bib` export, report the absolute output path and entry count.
- For citation insertion, report the edited file, inserted citation key, and updated `.bib` path.
- For imports, report the selected Zotero destination, source file or record, session identifier, and server response.
- For failures, identify the exact gate: Zotero missing, local API disabled, port closed, Connector unavailable, no matching item, unsupported environment, or write confirmation missing.

## Route details

Read `references/local-api-routes.md` only when endpoint details beyond the helper commands are required.
