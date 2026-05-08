# Agents Skills

This repository contains custom Codex skills.

## Skills

- `check`: reviews diffs, extracts repo constraints, and handles ship/release follow-through.
- `design`: builds distinctive production UI and screenshot-driven visual fixes.
- `fulfillment-modeling`: turns software or business requirements into contract-centered Fulfillment Modeling graph models, with bundled FM rules and a graph self-check script.
- `hunt`: diagnoses root causes before applying a fix.
- `image-tools`: compresses and converts images to WebP, PNG, or JPEG.
- `learn`: turns multiple sources into structured research output.
- `markdown-html`: converts Markdown into styled standalone HTML, including WeChat-compatible themes and citation mode.
- `read`: fetches URLs and PDFs as clean Markdown.
- `think`: turns rough ideas into approved implementation plans.
- `write`: rewrites prose to sound natural in Chinese or English.
- `youtube`: downloads YouTube transcripts, subtitles, metadata, chapters, speaker-labelled transcript drafts, and cover images.

## Install

Clone this repository as an `.agents` directory:

```bash
git clone https://github.com/JayClock/.agents.git ~/.agents
```

Or copy a skill folder into an existing agents skills directory:

```bash
cp -R skills/read ~/.agents/skills/
```

## Structure

```text
skills/
├── check/
├── design/
├── fulfillment-modeling/
├── hunt/
├── image-tools/
├── learn/
├── markdown-html/
├── read/
├── think/
├── write/
└── youtube/
```

The Waza skills were migrated from `tw93/Waza` and kept in the same folder layout so Codex can discover them directly. Waza's MIT license is included in `WAZA-LICENSE`.

The `youtube`, `markdown-html`, and `image-tools` skills are adapted from `JimLiu/baoyu-skills` and keep its practical script-based workflow.

## Validation

When editing the FM skill, run the bundled checker with a graph JSON file:

```bash
cd skills/fulfillment-modeling
python3 scripts/self_check_fm_graph.py /tmp/fm-graph.json
```
