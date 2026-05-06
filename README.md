# Agents Skills

This repository contains custom Codex skills.

## Skills

- `fulfillment-modeling`: turns software or business requirements into contract-centered Fulfillment Modeling graph models, with bundled FM rules and a graph self-check script.

## Install

Clone this repository as an `.agents` directory:

```bash
git clone https://github.com/JayClock/.agents.git ~/.agents
```

Or copy the skill folder into an existing agents skills directory:

```bash
cp -R skills/fulfillment-modeling ~/.agents/skills/
```

## Structure

```text
skills/
└── fulfillment-modeling/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/fm-modeling-rules.md
    └── scripts/self_check_fm_graph.py
```

## Validation

When editing the FM skill, run the bundled checker with a graph JSON file:

```bash
cd skills/fulfillment-modeling
python3 scripts/self_check_fm_graph.py /tmp/fm-graph.json
```
