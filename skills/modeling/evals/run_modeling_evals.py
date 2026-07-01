#!/usr/bin/env python3
"""Local eval runner for the modeling skill.

This runner cannot create an AI subagent by itself. It provides the local harness
around the eval prompts:

1. Prepare an isolated workspace for each eval.
2. Optionally execute a user-provided command template to produce outputs.
3. Grade the produced fm-model/ with the FM YAML self-check plus heuristic
   eval-specific assertions.
4. Write grading.json, results.json, and benchmark.md.

Example:
  python3 skills/modeling/evals/run_modeling_evals.py --clean --prepare-only

  # After manually running an agent into each outputs/ directory:
  python3 skills/modeling/evals/run_modeling_evals.py --grade-only

  # Or use an external command template:
  python3 skills/modeling/evals/run_modeling_evals.py --clean \
    --command-template 'your-agent --skill {skill_dir} --prompt-file {prompt_file} --input-dir {input_dir} --output-dir {output_dir}'
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment issue
    yaml = None  # type: ignore[assignment]


EVAL_NAME_BY_ID = {
    0: "vip-membership-agreement",
    1: "payment-channel-variation",
    2: "precontract-channel-contexts",
    3: "internal-kpi-agreement",
    4: "missing-confirmation-repair",
}

IMPLEMENTATION_DETAIL_TERMS = [
    "API",
    "SDK",
    "Endpoint",
    "Controller",
    "Database",
    "DataTable",
    "MessageQueue",
    "Kafka",
    "RabbitMQ",
    "UI",
    "登录页面",
    "页面交互",
    "App交互",
    "APP交互",
    "播放器实现",
    "推荐算法",
    "接口",
    "数据库",
    "数据表",
    "消息队列",
    "队列",
    "部署",
]


@dataclass
class Expectation:
    text: str
    passed: bool
    evidence: str

    def to_json(self) -> dict[str, Any]:
        return {"text": self.text, "passed": self.passed, "evidence": self.evidence}


@dataclass
class ModelData:
    model_dir: Path | None
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    docs_text: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def eval_name(eval_item: dict[str, Any]) -> str:
    raw_id = eval_item.get("id")
    try:
        numeric_id = int(raw_id)
    except (TypeError, ValueError):
        numeric_id = -1
    return str(eval_item.get("name") or EVAL_NAME_BY_ID.get(numeric_id) or f"eval-{raw_id}")


def eval_dir(workspace: Path, eval_item: dict[str, Any]) -> Path:
    return workspace / f"eval-{eval_item['id']}-{eval_name(eval_item)}"


def selected_evals(evals: list[dict[str, Any]], only: str | None) -> list[dict[str, Any]]:
    if not only:
        return evals
    wanted = {part.strip() for part in only.split(",") if part.strip()}
    return [item for item in evals if str(item.get("id")) in wanted or eval_name(item) in wanted]


def copy_inputs(eval_item: dict[str, Any], destination: Path, root: Path) -> list[str]:
    copied: list[str] = []
    destination.mkdir(parents=True, exist_ok=True)
    for file_entry in eval_item.get("files", []):
        source = (root / file_entry).resolve()
        if not source.exists():
            raise FileNotFoundError(f"Eval input file does not exist: {file_entry}")
        target = destination / source.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        copied.append(str(target))
    return copied


def prepare_eval(
    eval_item: dict[str, Any], workspace: Path, configuration: str, root: Path, skill_dir: Path
) -> Path:
    base = eval_dir(workspace, eval_item)
    input_dir = base / "inputs"
    run_dir = base / configuration
    output_dir = run_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    copied_inputs = copy_inputs(eval_item, input_dir, root)
    (base / "prompt.md").write_text(eval_item["prompt"] + "\n", encoding="utf-8")
    (base / "expected_output.md").write_text(
        eval_item.get("expected_output", "") + "\n", encoding="utf-8"
    )
    metadata = {
        "eval_id": eval_item.get("id"),
        "eval_name": eval_name(eval_item),
        "prompt": eval_item.get("prompt"),
        "expected_output": eval_item.get("expected_output"),
        "input_files": copied_inputs,
        "skill_dir": str(skill_dir),
        "configuration": configuration,
        "output_dir": str(output_dir),
        "assertions": [],
    }
    write_json(base / "eval_metadata.json", metadata)
    (run_dir / "manual_run.md").write_text(
        "# Manual run instructions\n\n"
        "Run the modeling agent with this eval prompt and save the generated `fm-model/` "
        "under the outputs directory below.\n\n"
        f"- Skill path: `{skill_dir}`\n"
        f"- Prompt file: `{base / 'prompt.md'}`\n"
        f"- Input dir: `{input_dir}`\n"
        f"- Output dir: `{output_dir}`\n\n"
        "After outputs are present, run:\n\n"
        f"```bash\npython3 {Path(__file__).as_posix()} --workspace {workspace.as_posix()} --grade-only\n```\n",
        encoding="utf-8",
    )
    return base


def run_command_template(
    command_template: str,
    eval_item: dict[str, Any],
    workspace: Path,
    configuration: str,
    root: Path,
    skill_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    base = eval_dir(workspace, eval_item)
    run_dir = base / configuration
    output_dir = run_dir / "outputs"
    input_dir = base / "inputs"
    prompt_file = base / "prompt.md"
    values = {
        "repo_root": str(root),
        "skill_dir": str(skill_dir),
        "workspace": str(workspace),
        "eval_dir": str(base),
        "run_dir": str(run_dir),
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "prompt_file": str(prompt_file),
        "eval_id": str(eval_item.get("id")),
        "eval_name": eval_name(eval_item),
    }
    command = command_template.format(**values)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    started = time.time()
    completed = subprocess.run(
        command,
        shell=True,
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    duration = time.time() - started
    (run_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    timing = {
        "command": command,
        "returncode": completed.returncode,
        "duration_seconds": round(duration, 3),
        "started_at": utc_now(),
    }
    write_json(run_dir / "timing.json", timing)
    return timing


def find_model_dir(output_dir: Path) -> Path | None:
    candidates = [output_dir / "fm-model", output_dir]
    candidates.extend(path for path in output_dir.rglob("fm-model") if path.is_dir())
    candidates.extend(path.parent for path in output_dir.rglob("entities") if path.is_dir())
    for candidate in candidates:
        if (candidate / "entities").is_dir() and (candidate / "relationships").is_dir():
            return candidate
    return None


def read_yaml_file(path: Path) -> dict[str, Any] | None:
    if yaml is None:
        return None
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def load_model(output_dir: Path) -> ModelData:
    model_dir = find_model_dir(output_dir)
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    docs_text = ""
    if model_dir is None:
        return ModelData(None, entities, relationships, docs_text)

    for path in sorted((model_dir / "entities").glob("*.yaml")):
        doc = read_yaml_file(path)
        if doc:
            doc["_file"] = str(path)
            entities.append(doc)
    for path in sorted((model_dir / "relationships").glob("*.yaml")):
        doc = read_yaml_file(path)
        if doc:
            doc["_file"] = str(path)
            relationships.append(doc)
    md_parts: list[str] = []
    for path in sorted(model_dir.glob("*.md")):
        try:
            md_parts.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    docs_text = "\n".join(md_parts)
    return ModelData(model_dir, entities, relationships, docs_text)


def item_text(item: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("name", "label", "kind", "category", "notes"):
        value = item.get(key)
        if isinstance(value, str):
            parts.append(value)
    for attribute in item.get("attributes") or []:
        if isinstance(attribute, dict):
            for key in ("name", "label", "meaning", "calculationRule", "precondition"):
                value = attribute.get(key)
                if isinstance(value, str):
                    parts.append(value)
    return " ".join(parts)


def has_entity(
    model: ModelData,
    *,
    category: str | None = None,
    kind: str | None = None,
    pattern: str | None = None,
) -> bool:
    regex = re.compile(pattern, re.IGNORECASE) if pattern else None
    for entity in model.entities:
        if category and entity.get("category") != category:
            continue
        if kind and entity.get("kind") != kind:
            continue
        if regex and not regex.search(item_text(entity)):
            continue
        return True
    return False


def matching_entities(model: ModelData, *, kind: str | None = None, pattern: str | None = None) -> list[dict[str, Any]]:
    regex = re.compile(pattern, re.IGNORECASE) if pattern else None
    result: list[dict[str, Any]] = []
    for entity in model.entities:
        if kind and entity.get("kind") != kind:
            continue
        if regex and not regex.search(item_text(entity)):
            continue
        result.append(entity)
    return result


def has_doc(model: ModelData, filename: str) -> bool:
    return model.model_dir is not None and (model.model_dir / filename).exists()


def docs_or_model_contains(model: ModelData, pattern: str) -> bool:
    regex = re.compile(pattern, re.IGNORECASE)
    haystack = model.docs_text + "\n" + "\n".join(item_text(e) for e in model.entities)
    return bool(regex.search(haystack))


def run_self_check(skill_dir: Path, model_dir: Path | None) -> tuple[bool, str]:
    if model_dir is None:
        return False, "No fm-model directory found under outputs."
    script = skill_dir / "scripts" / "self_check_fm_yaml.py"
    completed = subprocess.run(
        [sys.executable, str(script), str(model_dir)],
        text=True,
        capture_output=True,
    )
    evidence = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, evidence


def add(expectations: list[Expectation], text: str, passed: bool, evidence: str) -> None:
    expectations.append(Expectation(text, bool(passed), evidence))


def general_expectations(model: ModelData, self_check_passed: bool, self_check_output: str) -> list[Expectation]:
    expectations: list[Expectation] = []
    add(
        expectations,
        "Output contains a discoverable fm-model directory with entities/ and relationships/.",
        model.model_dir is not None,
        str(model.model_dir) if model.model_dir else "No model directory found.",
    )
    add(
        expectations,
        "Model contains at least one entity YAML and one relationship YAML.",
        bool(model.entities) and bool(model.relationships),
        f"entities={len(model.entities)}, relationships={len(model.relationships)}",
    )
    add(
        expectations,
        "FM YAML self-check passes.",
        self_check_passed,
        self_check_output or "No self-check output.",
    )
    bad_entities = [
        entity.get("name", "<unnamed>")
        for entity in model.entities
        if any(term.lower() in item_text(entity).lower() for term in IMPLEMENTATION_DETAIL_TERMS)
    ]
    add(
        expectations,
        "Model does not introduce UI/API/database/queue/page/player/recommendation implementation entities.",
        not bad_entities,
        "No forbidden implementation-detail terms found." if not bad_entities else f"Found: {bad_entities}",
    )
    return expectations


def eval_specific_expectations(eval_id: int, model: ModelData) -> list[Expectation]:
    expectations: list[Expectation] = []

    if eval_id == 0:
        add(expectations, "VIP membership agreement is modeled as a Contract.", has_entity(model, kind="Contract", pattern=r"VIP|会员|协议|Agreement"), "Looked for Contract with VIP/会员/协议.")
        add(expectations, "Recharge flow has Fulfillment Request and Fulfillment Confirmation evidence.", has_entity(model, kind="Fulfillment Request", pattern=r"充值|购买|Recharge") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"充值|Recharge"), "Looked for recharge request/confirmation.")
        add(expectations, "Member entitlement activation is modeled as request/confirmation evidence.", has_entity(model, kind="Fulfillment Request", pattern=r"权益|开通|Entitlement|Activation") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"权益|开通|Entitlement|Activation"), "Looked for entitlement activation request/confirmation.")
        add(expectations, "Refund flow is modeled as request/confirmation evidence.", has_entity(model, kind="Fulfillment Request", pattern=r"退费|退款|Refund") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"退费|退款|Refund"), "Looked for refund request/confirmation.")
        add(expectations, "Member entitlement calculator is modeled as a Domain Role.", has_entity(model, kind="Domain Role", pattern=r"权益.*计算|计算.*权益|Entitlement.*Calculator|Calculator.*Entitlement"), "Looked for Domain Role containing entitlement/calculator.")
        add(expectations, "Video account and VIP card are modeled as business/domain objects, not implementation details.", has_entity(model, pattern=r"账号|Account") and has_entity(model, pattern=r"会员卡|VIP.*Card|Card"), "Looked for account and VIP card entities.")
        add(expectations, "Business patterns document is produced.", has_doc(model, "02-business-patterns.md"), "Checked for 02-business-patterns.md.")

    elif eval_id == 1:
        add(expectations, "Payment channel variability is represented by Evidence As Role or Context Role.", has_entity(model, kind="Evidence As Role", pattern=r"支付|付款|Payment|退费|退款|Refund") or has_entity(model, kind="Context Role", pattern=r"支付|付款|Payment|渠道|Channel|退费|退款|Refund"), "Looked for Evidence As Role / Context Role for payment/refund variation.")
        add(expectations, "Sales payment flow has request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"支付|付款|收款|Payment") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"支付|付款|收款|Payment"), "Looked for payment request/confirmation.")
        add(expectations, "Shipment flow has request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"发货|交付|Shipment|Delivery") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"发货|交付|Shipment|Delivery"), "Looked for shipment request/confirmation.")
        add(expectations, "Refund exception flow has request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"退费|退款|Refund") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"退费|退款|Refund"), "Looked for refund request/confirmation.")
        add(expectations, "Model explanation identifies payment/refund channel as variation point.", docs_or_model_contains(model, r"变化点.*(支付|付款|退费|退款|渠道)|(支付|付款|退费|退款|渠道).*变化点"), "Searched docs and model text for variation-point wording.")

    elif eval_id == 2:
        proposal_count = len(matching_entities(model, kind="Proposal"))
        rfp_count = len(matching_entities(model, kind="RFP"))
        add(expectations, "Pre-contract contexts include RFP evidence where traceable inquiry/tender exists.", rfp_count >= 1, f"RFP count={rfp_count}")
        add(expectations, "Pre-contract contexts include multiple Proposal evidence for package/tender paths.", proposal_count >= 3, f"Proposal count={proposal_count}")
        add(expectations, "Final decoration service contract is modeled.", has_entity(model, kind="Contract", pattern=r"装修|Decoration"), "Looked for decoration Contract.")
        add(expectations, "Start-work flow has request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"开工|Start") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"开工|Start"), "Looked for start-work request/confirmation.")
        add(expectations, "Acceptance flow has request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"验收|Acceptance") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"验收|Acceptance"), "Looked for acceptance request/confirmation.")
        add(expectations, "Model mentions channel/pre-contract separation.", docs_or_model_contains(model, r"渠道|合约前|签约来源|pre.?contract|channel"), "Searched docs and model text for channel/pre-contract wording.")

    elif eval_id == 3:
        add(expectations, "Performance agreement is modeled as a Contract.", has_entity(model, kind="Contract", pattern=r"绩效|Performance|KPI"), "Looked for performance/KPI Contract.")
        payment_like = [entity.get("name", "<unnamed>") for entity in model.entities if re.search(r"付款|支付|退款|收款|Payment|Refund", item_text(entity), re.IGNORECASE)]
        add(expectations, "No cash/payment flow is invented for this non-cash KPI scenario.", not payment_like, "No payment-like entities found." if not payment_like else f"Found: {payment_like}")
        add(expectations, "Contact records or KPI results are modeled as traceable evidence.", has_entity(model, pattern=r"联系记录|Contact.*Record|KPI|指标|进度|Progress|Result|结果"), "Looked for contact/KPI/progress evidence or object.")
        add(expectations, "Coaching improvement obligation is modeled as request and confirmation.", has_entity(model, kind="Fulfillment Request", pattern=r"辅导|改进|Coaching|Improvement") and has_entity(model, kind="Fulfillment Confirmation", pattern=r"辅导|改进|Coaching|Improvement"), "Looked for coaching/improvement request/confirmation.")
        add(expectations, "Manager and salesperson responsibilities are represented.", has_entity(model, pattern=r"主管|Manager") and has_entity(model, pattern=r"电话销售|销售|Salesperson"), "Looked for manager and salesperson entities/roles.")

    elif eval_id == 4:
        confirmations = matching_entities(model, kind="Fulfillment Confirmation", pattern=r"交付|验收|收货|Delivery|Acceptance|Receipt")
        add(expectations, "A delivery/acceptance Fulfillment Confirmation is added.", bool(confirmations), f"Matching confirmations={[c.get('name') for c in confirmations]}")
        confirmation_names = {str(entity.get("name")) for entity in confirmations}
        has_direct_link = any(
            rel.get("source") == "DeliveryInstruction" and rel.get("target") in confirmation_names
            for rel in model.relationships
        )
        add(expectations, "DeliveryInstruction points to the added delivery/acceptance confirmation.", has_direct_link, "Checked direct relationship source=DeliveryInstruction -> matching confirmation.")
        add(expectations, "Original Purchase contract remains present.", has_entity(model, kind="Contract", pattern=r"Purchase|采购"), "Looked for Purchase/采购 Contract.")

    return expectations


def grade_eval(eval_item: dict[str, Any], workspace: Path, configuration: str, skill_dir: Path) -> dict[str, Any]:
    base = eval_dir(workspace, eval_item)
    run_dir = base / configuration
    output_dir = run_dir / "outputs"
    model = load_model(output_dir)
    self_check_passed, self_check_output = run_self_check(skill_dir, model.model_dir)
    expectations = general_expectations(model, self_check_passed, self_check_output)
    expectations.extend(eval_specific_expectations(int(eval_item["id"]), model))
    passed = sum(1 for item in expectations if item.passed)
    total = len(expectations)
    result = {
        "run_id": f"eval-{eval_item['id']}-{configuration}",
        "eval_id": eval_item.get("id"),
        "eval_name": eval_name(eval_item),
        "configuration": configuration,
        "model_dir": str(model.model_dir) if model.model_dir else None,
        "expectations": [item.to_json() for item in expectations],
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "graded_at": utc_now(),
    }
    write_json(run_dir / "grading.json", result)
    return result


def write_benchmark(workspace: Path, skill_name: str, results: list[dict[str, Any]], configuration: str) -> None:
    total_passed = sum(item["passed"] for item in results)
    total_assertions = sum(item["total"] for item in results)
    evals_all_passed = sum(1 for item in results if item["passed"] == item["total"])
    summary = {
        "skill_name": skill_name,
        "configuration": configuration,
        "workspace": str(workspace),
        "generated_at": utc_now(),
        "summary": {
            "evals_passed": evals_all_passed,
            "evals_total": len(results),
            "assertions_passed": total_passed,
            "assertions_total": total_assertions,
            "assertion_pass_rate": round(total_passed / total_assertions, 4) if total_assertions else 0.0,
        },
        "eval_results": results,
    }
    write_json(workspace / "results.json", summary)
    write_json(workspace / "benchmark.json", summary)

    lines = [
        f"# {skill_name} eval benchmark",
        "",
        f"- Configuration: `{configuration}`",
        f"- Generated at: {summary['generated_at']}",
        f"- Eval pass rate: {evals_all_passed}/{len(results)}",
        f"- Assertion pass rate: {total_passed}/{total_assertions} ({summary['summary']['assertion_pass_rate']:.2%})",
        "",
        "| Eval | Name | Assertions | Pass rate | Model dir |",
        "|---:|---|---:|---:|---|",
    ]
    for item in results:
        model_dir = item.get("model_dir") or "-"
        lines.append(
            f"| {item['eval_id']} | {item['eval_name']} | {item['passed']}/{item['total']} | {item['pass_rate']:.2%} | `{model_dir}` |"
        )
    lines.extend(["", "## Failed expectations", ""])
    failures = False
    for item in results:
        failed = [exp for exp in item["expectations"] if not exp["passed"]]
        if not failed:
            continue
        failures = True
        lines.append(f"### Eval {item['eval_id']} · {item['eval_name']}")
        for exp in failed:
            evidence = str(exp.get("evidence", "")).replace("\n", " ")
            if len(evidence) > 240:
                evidence = evidence[:237] + "..."
            lines.append(f"- **{exp['text']}** — {evidence}")
        lines.append("")
    if not failures:
        lines.append("No failed expectations.")
    (workspace / "benchmark.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Run or grade modeling skill evals.")
    parser.add_argument("--evals", default=str(default_skill_dir() / "evals" / "evals.json"))
    parser.add_argument("--skill-dir", default=str(default_skill_dir()))
    parser.add_argument("--workspace", default=str(root / "modeling-workspace" / "iteration-1"))
    parser.add_argument("--configuration", default="with_skill")
    parser.add_argument("--only", help="Comma-separated eval ids or names to run/grade.")
    parser.add_argument("--clean", action="store_true", help="Delete workspace before preparing evals.")
    parser.add_argument("--prepare-only", action="store_true", help="Only create workspace prompts/inputs; do not run commands or grade.")
    parser.add_argument("--grade-only", action="store_true", help="Only grade existing outputs; do not prepare or run commands.")
    parser.add_argument("--command-template", help="Shell command template used to produce outputs for each eval.")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--fail-on-grade-failure", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if yaml is None:
        print("error: PyYAML is required for grading modeling evals.", file=sys.stderr)
        return 2

    root = repo_root()
    evals_path = Path(args.evals).resolve()
    skill_dir = Path(args.skill_dir).resolve()
    workspace = Path(args.workspace).resolve()
    eval_payload = load_json(evals_path)
    evals = selected_evals(eval_payload.get("evals", []), args.only)
    if not evals:
        print("No evals selected.", file=sys.stderr)
        return 2

    if args.clean and workspace.exists() and not args.grade_only:
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    if not args.grade_only:
        for item in evals:
            base = prepare_eval(item, workspace, args.configuration, root, skill_dir)
            print(f"prepared eval {item['id']} -> {base}")

    if args.prepare_only:
        print(f"Prepared {len(evals)} eval(s) under {workspace}")
        return 0

    if args.command_template and not args.grade_only:
        for item in evals:
            print(f"running eval {item['id']} with command template...")
            timing = run_command_template(
                args.command_template,
                item,
                workspace,
                args.configuration,
                root,
                skill_dir,
                args.timeout_seconds,
            )
            print(f"  returncode={timing['returncode']} duration={timing['duration_seconds']}s")

    results = []
    for item in evals:
        result = grade_eval(item, workspace, args.configuration, skill_dir)
        results.append(result)
        print(
            f"graded eval {item['id']} {result['eval_name']}: "
            f"{result['passed']}/{result['total']} ({result['pass_rate']:.2%})"
        )

    write_benchmark(workspace, eval_payload.get("skill_name", "modeling"), results, args.configuration)
    print(f"wrote {workspace / 'results.json'}")
    print(f"wrote {workspace / 'benchmark.md'}")

    if args.fail_on_grade_failure and any(item["passed"] != item["total"] for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
