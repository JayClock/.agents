# Agents Skills

This repository now keeps only the User Story / Fulfillment Modeling / Agent Architecture skills and their supporting files.

## Retained Skills

### User Story and Modeling Workflow

| Skill | Solves |
|---|---|
| `user-story-modeling-workflow` | Orchestrates Epic stories, fine-grained stories, TQA refinement, domain modeling, and model validation. |
| `user-story-tqa-refinement` | Refines, splits, completes, or writes user stories through a Think → Question → Answer loop. |
| `tqa-acceptance-criteria-writer` | Writes Given/When/Then acceptance criteria after clarifying missing business context. |
| `story-model-validation` | Validates domain models against fine-grained stories and acceptance criteria. |
| `modeling` | Creates Fulfillment Modeling graphs from business/software requirements. |
| `fm-database-design` | Maps FM graphs into append-only microservice database table designs and SQL DDL. |

### Agent Architecture

| Skill | Solves |
|---|---|
| `agent-selection-review` | Reviews or selects Agent / Workflow / Multi-agent architectures for business requirements and PRDs. |
| `agent-harness-reverse-five-step` | Reverse engineers Agent Harness / coding-agent repositories from source evidence. |

## Supporting Content

- `skills/_shared/agent-double-axis-framework.md` is shared by the two Agent Architecture skills.
- `scripts/install-bundle.sh` installs retained bundles.
- `scripts/package-skill.py` packages skills that depend on shared references.
- `dist/*.skill` contains packaged artifacts for the retained Agent Architecture skills.

## Installation

Clone this repository as an `.agents` directory:

```bash
git clone https://github.com/JayClock/.agents.git ~/.agents
```

Install a retained bundle into an existing agents directory:

```bash
scripts/install-bundle.sh user-story-modeling ~/.agents/skills
scripts/install-bundle.sh agent-architecture ~/.agents/skills
```

List bundles:

```bash
scripts/install-bundle.sh --list
```

Update an installed bundle:

```bash
scripts/install-bundle.sh user-story-modeling ~/.agents/skills --force
```

## Bundles

| Bundle | Skills | Use When |
|---|---|---|
| `user-story-modeling` | `user-story-modeling-workflow`, `user-story-tqa-refinement`, `tqa-acceptance-criteria-writer`, `story-model-validation`, `modeling`, `fm-database-design` | Running an end-to-end requirements → stories → acceptance criteria → model → database design / validation workflow. |
| `agent-architecture` | `agent-selection-review`, `agent-harness-reverse-five-step` | Selecting, reviewing, or reverse engineering Agent architectures with the double-axis framework. |
| `all` | Every retained skill | Installing the complete reduced skill set. |

## Validation

When editing the Fulfillment Modeling skill, run:

```bash
python3 skills/modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

When updating an existing FM graph with a changes payload, run:

```bash
python3 skills/modeling/scripts/apply_fm_changes.py /tmp/base-fm-graph.json /tmp/fm-changes.json /tmp/merged-fm-graph.json
python3 skills/modeling/scripts/self_check_fm_graph.py /tmp/merged-fm-graph.json
```

For distributable standalone `.skill` archives that need shared references:

```bash
scripts/package-skill.py agent-selection-review dist
scripts/package-skill.py agent-harness-reverse-five-step dist
```
