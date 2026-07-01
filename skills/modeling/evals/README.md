# Modeling Skill Evals

These evals exercise the `modeling` skill after the 8X Flow / BOD optimization.

## What the eval set covers

| ID | Focus | Key risk being tested |
|---:|---|---|
| 0 | VIP membership agreement | Separates business logic from domain/implementation details; extracts business macro flow. |
| 1 | Multiple payment/refund channels | Uses Evidence As Role / Context Role for payment variation instead of coupling contracts. |
| 2 | Contract-before / channel contexts | Keeps RFP/Proposal/channel paths separate from contract fulfillment. |
| 3 | Internal KPI agreement | Uses target-actual/KPI anchors when no cash flow exists. |
| 4 | Existing invalid model repair | Detects and fixes Fulfillment Request without Fulfillment Confirmation. |

## Local eval runner

Use the local runner to prepare isolated workspaces, optionally call an external agent command, and grade produced `fm-model/` outputs.

Prepare prompts, copied inputs, and output directories:

```bash
python3 skills/modeling/evals/run_modeling_evals.py --clean --prepare-only
```

Then run each prompt manually with access to `skills/modeling/`, saving each generated `fm-model/` under the corresponding:

```text
modeling-workspace/iteration-1/eval-<id>-<name>/with_skill/outputs/
```

Grade existing outputs and generate reports:

```bash
python3 skills/modeling/evals/run_modeling_evals.py --grade-only
```

The runner writes:

```text
modeling-workspace/iteration-1/results.json
modeling-workspace/iteration-1/benchmark.json
modeling-workspace/iteration-1/benchmark.md
modeling-workspace/iteration-1/eval-*/with_skill/grading.json
```

If you have a CLI that can run an agent from a prompt file, provide it as a command template. Available placeholders include `{skill_dir}`, `{prompt_file}`, `{input_dir}`, `{output_dir}`, `{eval_id}`, `{eval_name}`, `{workspace}`, and `{repo_root}`.

```bash
python3 skills/modeling/evals/run_modeling_evals.py --clean \
  --command-template 'your-agent --skill {skill_dir} --prompt-file {prompt_file} --input-dir {input_dir} --output-dir {output_dir}'
```

## Manual run shape

For each eval prompt, invoke the agent with access to `skills/modeling/` and ask it to save outputs under an isolated workspace, for example:

```text
Execute this task:
- Skill path: skills/modeling
- Task: <eval prompt>
- Input files: <files from evals.json, if any>
- Save outputs to: modeling-workspace/iteration-1/eval-<id>-<name>/with_skill/outputs/
- Outputs to save: fm-model/ and final response
```

## Suggested grading checks

Common checks for every eval:

1. The output contains `entities/` and `relationships/` YAML files.
2. `self_check_fm_yaml.py` passes.
3. The model contains no UI/API/database/queue/page/player/recommendation implementation entities unless explicitly requested.
4. Contract entities trace to exactly two Participant Party entities.
5. Each Fulfillment Request traces back to a Contract and forward to at least one Fulfillment Confirmation.
6. Every RFP/Proposal/Fulfillment Request/Fulfillment Confirmation/Other Evidence traces to exactly one responsible Participant Party.
7. Derived attributes use machine-checkable `calculationRule` / `precondition` when applicable.

Eval-specific checks are described in each `expected_output` entry in `evals.json`.
