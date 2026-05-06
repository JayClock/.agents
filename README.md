# Agents Skills

This repository contains custom Codex skills.

## Skills

- `fm-domain-architect`: turns software or business requirements into Fulfillment Modeling domain diagram proposals, with bundled FM rules and a proposal self-check script.

## Install

Clone this repository as an `.agents` directory:

```bash
git clone https://github.com/JayClock/.agents.git ~/.agents
```

Or copy the skill folder into an existing agents skills directory:

```bash
cp -R skills/fm-domain-architect ~/.agents/skills/
```

## Structure

```text
skills/
└── fm-domain-architect/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/fm-modeling-rules.md
    └── scripts/self_check_fm_proposal.py
```

## Validation

When editing the FM skill, run the bundled checker with a proposal JSON file:

```bash
cd skills/fm-domain-architect
python3 scripts/self_check_fm_proposal.py /tmp/proposal.json
```
