# Agents Skills

Custom Codex skills for research, design, writing, debugging, review, and content utilities.

## Prerequisites

- Codex or another agent runtime that can discover local `skills/*/SKILL.md` directories
- Node.js and `bun` or `npx` for script-backed skills:
  - `youtube`
  - `markdown-html`
  - `image-tools`
- Python 3 for the Fulfillment Modeling self-check script

## Installation

Clone this repository as an `.agents` directory:

```bash
git clone https://github.com/JayClock/.agents.git ~/.agents
```

Or copy one skill into an existing agents directory:

```bash
cp -R skills/read ~/.agents/skills/
```

After adding or updating skills, restart the agent session if your runtime does not hot-reload local skill definitions.

## Available Skills

Skills are organized by the kind of work they own.

### Thinking and Research

| Skill | Solves |
|-------|--------|
| `think` | Turns rough ideas into decision-complete implementation plans, architecture choices, or keep/kill/pivot judgments. |
| `learn` | Turns multiple sources into notes, knowledge classification, cognitive progression paths, articles, canonical references, or publish packages. |
| `read` | Fetches URLs and PDFs as clean Markdown, including GitHub, WeChat, Feishu/Lark, X/Twitter, and Chinese-platform pages. |

### Engineering

| Skill | Solves |
|-------|--------|
| `hunt` | Diagnoses root causes for errors, regressions, broken behavior, crashes, and failing tests before applying fixes. |
| `check` | Reviews diffs, extracts repository constraints, verifies changes, and handles ship/release follow-through. |
| `fulfillment-modeling` | Models business/software requirements into contract-centered Fulfillment Modeling graphs shaped like React Flow nodes and edges. |

### Writing and Design

| Skill | Solves |
|-------|--------|
| `write` | Rewrites, proofreads, translates, formats Markdown, and removes AI-taste from Chinese or English prose. |
| `design` | Builds and improves production UI, visual systems, frontend styling, and screenshot-driven visual fixes. |

### Content Utilities

| Skill | Solves |
|-------|--------|
| `youtube` | Downloads YouTube transcripts, subtitles, metadata, chapters, speaker-labelled transcript drafts, and cover images. |
| `markdown-html` | Converts Markdown into styled standalone HTML, including WeChat-compatible themes and citation mode. |
| `image-tools` | Compresses and converts images to WebP, PNG, or JPEG. |

## Common Workflows

### Research to Publish Package

Use `learn` when the output should be more than a summary. It can collect sources through `read` and `youtube`, classify knowledge, produce cognitive progression paths, and package the result:

```text
research-{topic}/
├── sources/
├── notes/
├── outline.md
├── draft.md
├── final.md
├── assets/
├── publish/
│   ├── article.html
│   └── images/
└── README.md
```

Choose a target based on the desired artifact:

| Target | Output |
|--------|--------|
| `Notes` | Structured notes, source index, open questions |
| `Article` | Long-form `final.md` |
| `Canonical Reference` | One-stop reference article |
| `WeChat HTML` | `final.md` plus `publish/article.html` |
| `Slide Outline` | Slide-ready outline and speaker notes |
| `Visual Brief` | Source-grounded visual brief for diagrams, infographics, covers, or cards |
| `Publish Package` | Full reusable research folder |

### Web and Video Capture

- Use `read` for normal pages, PDFs, GitHub, WeChat, Feishu/Lark, and X/Twitter links.
- Use `youtube` when the useful material is captions, transcript, chapters, metadata, or cover image.
- Do not scrape a YouTube watch page when the goal is transcript extraction.

### Markdown to WeChat-Ready HTML

1. Use `write` Markdown Formatting Mode to stabilize `final.md`.
2. Use `markdown-html` to create styled HTML.
3. Use citation mode only when the user asks for bottom references or WeChat-friendly external links.
4. Use `image-tools` to compress copies of publish images while keeping originals in `assets/`.

## Structure

```text
skills/
├── check/
├── design/
├── hunt/
├── image-tools/
├── learn/
├── markdown-html/
├── modeling/
├── read/
├── think/
├── write/
└── youtube/
```

## Configuration

Skill-level preferences should live next to the skill when needed:

```text
.agents/skills/{skill-name}/EXTEND.md
```

Script-backed skills may also support user-level config paths documented in their own `SKILL.md`.

## Validation

When editing the Fulfillment Modeling skill, run the bundled checker with a graph JSON file:

```bash
python3 skills/modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

When editing script-backed skills, run the local checks where available:

```bash
(cd skills/youtube/scripts && bun test)
(cd skills/markdown-html/scripts && bun install && bun test)
(cd skills/image-tools/scripts && bun run main.ts --help)
```

Remove generated `node_modules` after local validation unless the repository later decides to track dependencies differently.

## Credits

The `youtube`, `markdown-html`, and `image-tools` skills are adapted from `JimLiu/baoyu-skills` and keep its practical script-based workflow.
