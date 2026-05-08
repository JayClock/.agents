---
name: learn
description: "Run a six-phase research workflow to turn unfamiliar domains, multiple sources, or collected materials into notes, a deep-dive article, a canonical reference, or publish-ready output. Use for 学习一下, 深入研究, 研究一下, 整理成文章, 一站式参考, 一篇就够, research, deep dive, help me understand, or compile sources. Not for quick lookups or single-file reads."
---

# Learn: From Raw Materials to Published Output

Collect, organize, translate, explain, structure. Support the user's thinking; do not replace it.

**Boundary**: single URL that only needs fetching belongs in `/read`. A single URL that needs summary or analysis can use `/read` as the fetch step, but the final answer should satisfy the user's requested summary or analysis. `/learn` is for multi-source research that produces a new structured output.

## Pre-check

Check whether supporting skills are installed (look for their SKILL.md in the skills directories). Warn if missing, do not block:
- `/read` missing -- Phase 1 fetch falls back to native `WebFetch` / `curl`; coverage on paywalled, JS-heavy, and Chinese-platform pages degrades.
- `/write` missing -- Phase 5 AI-pattern stripping, translation, and Markdown formatting fall back to manual scan. Phases 1-4 are unaffected.
- `/youtube` missing -- YouTube materials can only be treated as regular web pages; transcripts, chapters, and cover extraction degrade.
- `/markdown-html` missing -- publish packages can still include Markdown, but not styled standalone HTML.
- `/image-tools` missing -- image compression and WebP/JPEG/PNG conversion remain manual.
- `/design` missing -- visual briefs can still be written, but diagrams, infographics, image cards, and cover directions are not executed by this skill.

## Choose Mode

Ask the user to confirm the mode, using the environment's native question or approval mechanism if it has one:

| Mode | Goal | Entry | Exit |
|------|------|-------|------|
| **Deep Research** | Understand a domain well enough to write about it | Phase 1 | Phase 6: publish-ready draft |
| **Quick Reference** | Build a working mental model fast, no article planned | Phase 2 | Phase 2: notes only |
| **Write to Learn** | Already have materials, force understanding through writing | Phase 3 | Phase 6: publish-ready draft |
| **Canonical Article** | One article that covers a topic so thoroughly readers need nothing else | Phase 1 | Phase 6: single authoritative reference |

If unsure, suggest Quick Reference.

## Choose Output Target

After mode is known, confirm the target artifact. If the user already asked for a specific artifact, use it without asking.

| Target | Output |
|--------|--------|
| **Notes** | Structured learning notes with sources and open questions |
| **Article** | Long-form draft with references and publish-ready prose |
| **Canonical Reference** | One-stop article intended to replace further searching |
| **WeChat HTML** | Final Markdown plus styled HTML via `/markdown-html` |
| **Slide Outline** | Slide-ready outline and speaker notes, no image generation by default |
| **Visual Brief** | Diagram, infographic, cover, or image-card brief handed to `/design` or another visual skill |
| **Publish Package** | Reusable project folder containing sources, notes, draft, final output, assets, and publish files |

Default by mode:
- Quick Reference -> Notes
- Deep Research -> Article
- Write to Learn -> Article
- Canonical Article -> Canonical Reference

Do not upload, post, or distribute content as part of any target. Publishing actions require a separate explicit user request.

## Canonical Article Mode

Activate when: "一篇就够", "一站式参考", "整理成长文", "目的是大家只需要看这篇就好了", or the user wants a single authoritative reference on a topic.

Goal: after reading the article, no one should need to search for anything else on this topic.

Additional requirements on top of standard Deep Research:
- Every major sub-topic must have its own section; nothing left as a footnote
- Include worked examples, not just principles
- Cover common mistakes and how to avoid them
- Add a "Further Reading" section with the 3-5 sources that go deepest; flag which ones are the best starting points
- Phase 6 self-review must confirm: "Could a reader implement/understand this from this article alone?"

## Phase 1: Collect

Gather primary sources only: papers that introduced key ideas, official lab/product blogs, posts from builders, canonical "build it from scratch" repositories. Not summaries. Not explainers.

Three ordered steps per source -- no shortcuts, no merging:

1. **Discover** -- use an installed search plugin (e.g., PipeLLM) to map the landscape, then deep-search the 2-3 most promising sub-topics. No plugin: use the environment's native web search. Output is a URL list; do not fetch content here.
2. **Route** -- choose the right material extractor before fetching:
   - Ordinary web pages, PDFs, GitHub, WeChat, Feishu/Lark, X/Twitter, and Chinese-platform pages -> `/read`
   - YouTube URLs where transcript, subtitles, chapters, metadata, speaker labels, or cover images matter -> `/youtube`
   - Local Markdown or text files -> copy into the research project; do not refetch or rewrite during collection
   - Screenshots, diagrams, or images -> save as source assets and write a short observation note; do not infer more than the image shows
3. **Fetch** -- every routed web URL goes through `/read` or `/youtube`. `/read` owns the proxy cascade, paywall detection, and platform routing. `/youtube` owns transcript, chapter, metadata, speaker draft, and cover extraction. `WebFetch` and raw `curl` silently fail on JS-heavy or paywalled sites and skip all of that. If the required skill is missing (Pre-check warned), fall back to native fetch and accept reduced coverage.
4. **File** -- `/read` saves to `~/Downloads/{title}.md` when called from `/learn`; `/youtube` saves into its transcript output directory. Move each source file into a sub-topic directory under the research project after the fetch returns. Move, don't refetch.

Target: 5-10 sources for a blog post, 15-20 for a deep technical survey.

## Research Project Folder

For multi-source work, create or reuse a project folder named `research-{topic-slug}` unless the user gives a path. Keep intermediate files. The folder should be useful after the conversation ends.

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

For Quick Reference, `sources/`, `notes/`, and `README.md` are enough. For Publish Package or WeChat HTML, fill `publish/`.

## Phase 2: Digest

Work through the materials. For each piece: read it fully, keep what is good, cut what is not. At the end of this phase, cut roughly half of what was collected.

For key claims, ask before including in the outline:
- Does this idea appear in at least two different contexts from the same source?
- Can this framework predict what the source would say about a new problem?
- Is this specific to this source, or would any expert in the field say the same thing?

Generic wisdom is not worth distilling. Passes two or three: belongs in the outline. Passes one: background material. Passes zero: cut it.

When two sources contradict on a factual claim, note both positions and the evidence each gives. Do not silently pick one.

## Phase 3: Outline

Write the outline for the article. For each section: note the source materials it draws from. If a section has no sources, either it does not belong or a source needs to be found first.

The outline must include two learning-oriented sections unless the user explicitly asks for a different structure:
- **Knowledge classification** -- classify the material into useful knowledge types, such as concepts, facts, frameworks, procedures, examples, tacit knowledge, assumptions, controversies, and meta-cognitive lessons. Explain what each type is useful for and which parts of the source material belong there.
- **How to raise cognitive level** -- explain how the reader can move from confusion to understanding, from trial-and-error to expert judgment, and from expert judgment to reusable explicit knowledge. Include concrete practices, feedback loops, diagnostic questions, and examples tied to the topic.

Do not start Phase 4 until the outline is solid.

## Visual Structure Brief

When the target is Visual Brief, Slide Outline, WeChat HTML, Publish Package, or the material would be clearer with a diagram, add a visual structure section to the outline. This is a brief, not final artwork.

Choose one or more structures based on the content:

| Content Shape | Visual Structure |
|---------------|------------------|
| Timeline, history, evolution | timeline |
| Step-by-step process, workflow, lifecycle | flow |
| Protocol, request/response, handoff between actors | sequence |
| Architecture, components, topology | structural diagram |
| Cause analysis, failure modes | fishbone / root-cause map |
| Tradeoff, before/after, pros/cons | comparison |
| Hierarchy, maturity model, dependency stack | pyramid / layers / tree |
| Many related concepts | mind map / matrix |
| Do and don't guidance | do-dont |
| Conversion, filtering, prioritization | funnel / quadrants |

Each visual brief must include:
- Purpose: what reader confusion it resolves
- Source sections: which source files support it
- Structure: chosen visual type and why
- Content: nodes, labels, steps, or comparison dimensions
- Constraints: language, aspect ratio, where it will appear, and whether it needs dark-mode or print-friendly output

If `/design` is installed and the user asks for final visuals, hand the brief to `/design`. Otherwise keep it as `assets/visual-brief.md`.

## Phase 4: Fill In

Work through the outline section by section. If a section is hard to write, the mental model is still weak there: return to Phase 2 for that sub-topic. The outline may change, and that is fine.

When filling in learning-oriented output, do not only explain the topic. Also show the reader how to learn the topic better:
- Separate what must be memorized, what must be understood, what must be practiced, and what must be reflected on.
- Name the tacit knowledge hidden in the material and describe what kind of experience or feedback is needed to acquire it.
- Convert high-level advice into operational exercises, checklists, experiments, or reflection prompts.
- Make cognitive progression explicit: what a beginner sees, what an intermediate practitioner starts to notice, and what an expert can diagnose or simplify.

Stall signals (any one means the mental model is incomplete for this section):
- You have rewritten the opening sentence three or more times without settling
- The section relies on a single source and you cannot cross-check the claim
- You need a new source that was not collected in Phase 1
- The paragraph makes a claim you could not explain to someone out loud

When stalled: return to Phase 2 for that sub-topic, not for the whole article.

## Phase 5: Refine

Pass the draft with a specific brief:
- Remove redundant and verbose passages without changing meaning or voice
- Flag places where the argument does not flow
- Identify gaps: concepts used before they are explained, claims needing sources

Do not summarize sections the user has not written. Do not draft new sections from scratch. Edits only.

Then strip AI patterns from the draft. If `/write` is installed, invoke it. If not, do it manually: scan for filler phrases, binary contrasts, dramatic fragmentation, and overused adverbs. Cut them without changing meaning.

If the output language differs from the source language, invoke `/write` Translation Mode before final prose polish. Use:
- quick only for short informal notes
- normal for articles and references
- refined for publication-quality output

If the target is Article, Canonical Reference, WeChat HTML, or Publish Package, invoke `/write` Markdown Formatting Mode before Phase 6. Keep the formatted output as `final.md` unless the user requests another filename.

## Phase 6: Self-review and Publish Readiness

The user reads the entire article linearly before publishing. Not with AI. Mark everything that feels off, fix it, read again. Two passes minimum.

When it reads clean from start to finish, the draft is ready for the user to publish.

For publish-oriented targets:
- **WeChat HTML** -- after `final.md` is stable, use `/markdown-html` to create `publish/article.html`. Enable citation mode only when the user asks for bottom references or WeChat-friendly external links.
- **Publish Package** -- include `sources/`, `notes/`, `outline.md`, `draft.md`, `final.md`, `assets/`, and `publish/README.md` explaining what each file is.
- **Images** -- if images are included and `/image-tools` is installed, compress copies into `publish/images/`; keep originals in `assets/`.
- **Visuals** -- include visual briefs or generated visual files under `assets/`; do not block publish readiness on image generation unless visuals are required by the target.

**After the user confirms the article is ready to publish, stop.** Do not upload, post, distribute, or perform any publish action unless explicitly asked.

## Gotchas

| What happened | Rule |
|---------------|------|
| Collected 30 secondary explainers instead of primary sources | Phase 1 targets papers, official blogs, and repos by builders. Summaries are not sources. |
| Used `WebFetch` or `curl` on URLs while `/read` was installed | Phase 1 fetch is not optional. `/read` owns the proxy cascade, paywall detection, and platform routing. Bypassing it silently loses coverage on paywalled, JS-heavy, or Chinese-platform pages. |
| Scraped a YouTube watch page when the useful material was captions or chapters | Route YouTube transcript, subtitles, metadata, and cover needs to `/youtube`. |
| Treated a convincing explainer as ground truth | Ask: does this appear in at least two different contexts from the same source? |
| Phase 2 wrote summaries instead of teaching the concept | Digest means building the mental model. Summarizing is not digesting. |
| Generated a pretty visual that is not grounded in sources | Visual briefs must name the source sections and the confusion they resolve before any final design work. |
| Converted to HTML before the draft was stable | Markdown is the source of truth. Only run `/markdown-html` after `final.md` is stable. |
| AI offered to upload the article to a blog or social platform after the user said it was ready | Stop at confirmation. Publishing is the user's action, not yours. |
