# Personal Agent Skills

This repository is the single source of truth for my reusable Agent Skills. Skills are
collected under `skills/` and indexed by `skills.json`.

## Management Model

- `skills/` contains enabled skills that may be discovered by an agent harness.
- `drafts/` contains unfinished skills and is never linked into a harness.
- `archive/` contains retired or replaced skills.
- `skills.json` is the only registry for category, lifecycle, invocation mode, and
  enablement.
- `skills/_shared/` contains repository-level references reused by multiple skills.

The repository does not maintain bundles. Every skill with `enabled: true` in
`skills.json` is part of the active personal collection.

## Skill Catalog

### Career Development

| Skill | Invocation | Solves |
| --- | --- | --- |
| [`career-assets`](skills/career-assets/SKILL.md) | Model | Builds a reusable career record through interviews and derives role-specific résumés. |

### User Story and Modeling Workflow

| Skill | Invocation | Solves |
| --- | --- | --- |
| [`user-story-modeling-workflow`](skills/user-story-modeling-workflow/SKILL.md) | User | Orchestrates Epic stories, detailed stories, TQA refinement, modeling, and validation. |
| [`user-story-tqa-refinement`](skills/user-story-tqa-refinement/SKILL.md) | Model | Refines and splits user stories through a Think → Question → Answer loop. |
| [`tqa-acceptance-criteria-writer`](skills/tqa-acceptance-criteria-writer/SKILL.md) | Model | Clarifies missing business context and writes Given/When/Then scenarios. |
| [`story-model-validation`](skills/story-model-validation/SKILL.md) | Model | Validates domain models against detailed stories and acceptance criteria. |

### Fulfillment Modeling

| Skill | Invocation | Solves |
| --- | --- | --- |
| [`modeling`](skills/modeling/SKILL.md) | Model | Creates and validates Fulfillment Modeling YAML graphs. |
| [`fm-database-design`](skills/fm-database-design/SKILL.md) | Model | Maps FM graphs into append-only database schemas and SQL DDL. |

### Agent Architecture

| Skill | Invocation | Solves |
| --- | --- | --- |
| [`agent-selection-review`](skills/agent-selection-review/SKILL.md) | Model | Selects and reviews Agent, Workflow, and Multi-agent architectures. |
| [`agent-harness-reverse-five-step`](skills/agent-harness-reverse-five-step/SKILL.md) | Model | Reverse engineers Agent Harness repositories from source evidence. |

### Research and Citation Management

| Skill | Invocation | Solves |
| --- | --- | --- |
| [`zotero`](skills/zotero/SKILL.md) | Model | Operates a local Zotero library, citations, exports, and imports. |

## Add or Retire a Skill

To add a skill:

1. Develop it under `drafts/<skill-name>/`.
2. Give it a `SKILL.md` and `agents/openai.yaml`.
3. Add realistic evaluations when its output can be checked.
4. Move it to `skills/<skill-name>/` when it is ready.
5. Register it in `skills.json` and add it to the catalog above.

To retire a skill, move it from `skills/` to `archive/`, remove it from `skills.json`,
and update this catalog.

## Invocation Modes

Each registered skill declares one invocation mode:

- `user`: only the user starts it. Its `SKILL.md` sets
  `disable-model-invocation: true`, and `agents/openai.yaml` sets
  `policy.allow_implicit_invocation: false`.
- `model`: the user or model may start it. Its description should clearly describe both
  what it does and when it should trigger.

Use user invocation for high-level workflow entry points. Use model invocation for
reusable capabilities that an agent or another skill should be able to reach.

## Skill-specific Validation

When editing the Fulfillment Modeling skill or a generated FM YAML model, run:

```bash
python3 skills/modeling/scripts/self_check_fm_yaml.py fm-model/
```

For a raw JSON graph payload:

```bash
python3 skills/modeling/scripts/fm_graph_validation.py /tmp/fm-graph.json
```

For modeling evaluations:

```bash
python3 skills/modeling/evals/run_modeling_evals.py --clean --prepare-only
python3 skills/modeling/evals/run_modeling_evals.py --grade-only
```
