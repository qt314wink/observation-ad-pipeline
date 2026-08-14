from __future__ import annotations
from pathlib import Path
from typing import Any
import csv, hashlib, json, os, shutil, subprocess, sys, time, uuid
import click, requests, yaml
from dotenv import load_dotenv
import fastjsonschema
from .campaign import compile_provider, validate_campaign

load_dotenv()
ROOT = Path(os.getenv("OBSAD_ROOT", ".")).expanduser().resolve()
SCHEMAS = ROOT / "schemas"
VALID_OPERATIONS = {"generate", "prompt", "motion_spec", "edit", "transform", "variation", "extend"}


def read_data(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.suffix.lower() in {".yaml", ".yml"} else json.loads(p.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def validate_with(schema_name: str, data: dict[str, Any]) -> list[str]:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    try:
        fastjsonschema.compile(schema)(data)
        return []
    except fastjsonschema.JsonSchemaException as exc:
        path = "/".join(str(part) for part in getattr(exc, "path", []) if part != "data") or "<root>"
        return [f"{path}: {exc.message}"]


def _dedupe(values: list[str]) -> list[str]:
    seen, out = set(), []
    for value in values:
        clean = " ".join(str(value).strip().split())
        key = clean.casefold()
        if clean and key not in seen:
            seen.add(key); out.append(clean)
    return out


def load_contract(task: dict[str, Any]) -> dict[str, Any]:
    path = task.get("contract")
    return read_data(path) if path else {}


def compile_prompt(task: dict[str, Any]) -> dict[str, Any]:
    p = task.get("prompt", {})
    contract = load_contract(task)
    preservation = contract.get("preservation", {})
    generation = contract.get("generation", {})

    locks = _dedupe(list(preservation.get("locks", [])) + list(p.get("locks", [])))
    motion = _dedupe(list(generation.get("actions", [])) + list(p.get("motion", [])))[:5]
    camera = _dedupe(list(generation.get("camera", [])) + list(p.get("camera", [])))[:3]
    style = _dedupe(list(generation.get("style", [])) + list(p.get("style", [])))[:6]
    avoid = _dedupe(list(preservation.get("prohibited_change", [])) + list(p.get("avoid", [])))[:18]
    event = p.get("event") or generation.get("event", "")
    final_state = p.get("final_state") or generation.get("final_state", "")

    sections = [p.get("task", "Create the requested visual output.")]
    if locks: sections.append("LOCK: preserve " + ", ".join(locks) + ".")
    if motion: sections.append("MOTION: " + "; ".join(motion) + ".")
    if camera: sections.append("CAMERA: " + "; ".join(camera) + ".")
    if event: sections.append("EVENT: " + str(event).rstrip(".") + ".")
    if final_state: sections.append("FINAL: " + str(final_state).rstrip(".") + ".")
    if style: sections.append("STYLE: " + ", ".join(style) + ".")

    positive = " ".join(sections)
    negative = ", ".join(avoid)
    budget = int(task.get("prompt_budget", {}).get("positive_chars", 1800))
    neg_budget = int(task.get("prompt_budget", {}).get("negative_chars", 900))
    if len(positive) > budget:
        raise ValueError(f"Compiled positive prompt is {len(positive)} chars; budget is {budget}.")
    if len(negative) > neg_budget:
        raise ValueError(f"Compiled negative prompt is {len(negative)} chars; budget is {neg_budget}.")
    return {"positive": positive, "negative": negative, "stats": {"positive_chars": len(positive), "negative_chars": len(negative), "locks": len(locks), "actions": len(motion), "styles": len(style)}}


def resolve(obj: dict[str, Any], dotted: str) -> Any:
    cur: Any = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur: cur = cur[part]
        else: raise KeyError(f"Cannot resolve '{dotted}' at '{part}'")
    return cur


def set_input(workflow: dict[str, Any], node: str, key: str, value: Any) -> None:
    node = str(node)
    if node not in workflow: raise KeyError(f"Workflow node {node} does not exist")
    if "inputs" not in workflow[node]: raise KeyError(f"Workflow node {node} has no inputs")
    workflow[node]["inputs"][key] = value


def reference_files(task: dict[str, Any]) -> list[Path]:
    ref = task.get("reference")
    if not ref: return []
    path = Path(ref["path"]).expanduser()
    if not path.is_absolute(): path = (ROOT / path).resolve()
    if ref["type"] == "folder":
        if not path.is_dir(): raise FileNotFoundError(path)
        files = sorted(p.resolve() for p in path.glob(ref.get("glob", "*")) if p.is_file())
        if not files: raise FileNotFoundError(f"No files matched {path}/{ref.get('glob','*')}")
        return files
    if not path.is_file(): raise FileNotFoundError(path)
    return [path.resolve()]


def upload_reference(base: str, path: Path, endpoint: str = "/upload/image") -> str:
    with path.open("rb") as fh:
        response = requests.post(base.rstrip("/") + endpoint, files={"image": (path.name, fh)}, data={"overwrite": "true"}, timeout=180)
    response.raise_for_status()
    payload = response.json()
    return payload.get("name") or payload.get("filename") or path.name


def append_ledger(row: dict[str, Any]) -> None:
    logdir = ROOT / "logs"; logdir.mkdir(parents=True, exist_ok=True)
    with (logdir / "runs.jsonl").open("a", encoding="utf-8") as fh: fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    fields = ["run_id","timestamp","task_id","operation","provider","workflow_sha256","references","positive","negative","outputs","status","error"]
    csv_path = logdir / "runs.csv"; fresh = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        if fresh: writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fields})
    with (logdir / "runs.txt").open("a", encoding="utf-8") as fh:
        fh.write(f"[{row['timestamp']}] {row['status'].upper()} {row['task_id']} {row['operation']} {row.get('outputs','')} {row.get('error','')}\n")


def healthcheck(url: str) -> tuple[bool, str]:
    try:
        r = requests.get(url.rstrip("/") + "/system_stats", timeout=15)
        return r.ok, f"HTTP {r.status_code}"
    except Exception as exc: return False, repr(exc)

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.2.1")
def main() -> None:
    """Observation-led image/video ad pipeline."""


@main.command("campaign-validate")
@click.argument("directory", type=click.Path(path_type=Path))
def campaign_validate(directory: Path) -> None:
    """Validate a governed campaign package and its cross-file invariants."""
    errors = validate_campaign(directory.resolve(), SCHEMAS / "campaign-contract.schema.json")
    if errors:
        raise click.ClickException("\n".join(errors))
    click.echo("valid")


@main.command("campaign-compile")
@click.argument("directory", type=click.Path(path_type=Path))
@click.option("--provider", type=click.Choice(["openai", "xai", "comfyui", "wan"]), required=True)
@click.option("--model", help="Execution-time model override; otherwise the configured environment variable is used.")
@click.option("--out", type=click.Path(path_type=Path))
def campaign_compile(directory: Path, provider: str, model: str | None, out: Path | None) -> None:
    """Compile the shared semantic contract through one provider adapter."""
    payload = compile_provider(directory.resolve(), provider, model=model)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
    click.echo(rendered, nl=False)

@main.command("doctor")
@click.option("--url", default=lambda: os.getenv("COMFY_URL", "http://127.0.0.1:8188"))
def doctor(url: str) -> None:
    checks = {
        "root": ROOT.exists(), "schemas": SCHEMAS.exists(), "python>=3.10": sys.version_info >= (3,10),
        "ffmpeg": shutil.which("ffmpeg") is not None, "git": shutil.which("git") is not None,
        "curl": shutil.which("curl") is not None, "jq": shutil.which("jq") is not None,
    }
    remote_ok, remote_msg = healthcheck(url)
    for key, value in checks.items(): click.echo(f"{'PASS' if value else 'FAIL'}  {key}")
    click.echo(f"{'PASS' if remote_ok else 'WARN'}  comfyui {url} ({remote_msg})")
    if not all(checks.values()): raise click.ClickException("Local environment has failed checks")

@main.command("validate")
@click.argument("taskfile")
def validate_task(taskfile: str) -> None:
    task = read_data(taskfile)
    errors = validate_with("task.schema.json", task)
    if task.get("contract"):
        errors += ["contract " + e for e in validate_with("master-contract.schema.json", load_contract(task))]
    if task.get("operation") in {"edit","transform","variation","extend"} and not task.get("reference"):
        errors.append("reference: required for this operation")
    if errors: raise click.ClickException("\n".join(errors))
    compile_prompt(task)
    click.echo("valid")

@main.command("compile")
@click.argument("taskfile")
@click.option("--out", type=click.Path())
def compile_command(taskfile: str, out: str | None) -> None:
    compiled = compile_prompt(read_data(taskfile))
    text = json.dumps(compiled, indent=2, ensure_ascii=False)
    if out: Path(out).write_text(text + "\n", encoding="utf-8")
    click.echo(text)

@main.command("run")
@click.argument("taskfile")
@click.option("--url", default=lambda: os.getenv("COMFY_URL", "http://127.0.0.1:8188"))
@click.option("--dry-run", is_flag=True)
def run_task(taskfile: str, url: str, dry_run: bool) -> None:
    task = read_data(taskfile); compiled = compile_prompt(task)
    run_id = str(uuid.uuid4()); stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    outputs: list[str] = []; status = "ok"; error = ""; wfhash = ""; refs: list[Path] = []
    provider = task.get("provider", "comfyui")
    try:
        validation = validate_with("task.schema.json", task)
        if validation: raise ValueError("; ".join(validation))
        refs = reference_files(task)
        if task["operation"] in {"prompt", "motion_spec"} or dry_run:
            click.echo(json.dumps(compiled, indent=2, ensure_ascii=False)); return
        if provider != "comfyui": raise ValueError("v2 runner currently executes provider=comfyui; other providers use adapter manifests only")
        wfpath = Path(task["workflow"]).expanduser()
        if not wfpath.is_absolute(): wfpath = (ROOT / wfpath).resolve()
        workflow = json.loads(wfpath.read_text(encoding="utf-8")); wfhash = hashlib.sha256(wfpath.read_bytes()).hexdigest()
        endpoint = task.get("reference_upload_endpoint", "/upload/image")
        uploaded = [upload_reference(url, p, endpoint) for p in refs]
        ctx = {"compiled": compiled, "parameters": task.get("parameters", {}), "reference": {"upload_name": uploaded[0] if uploaded else None, "upload_names": uploaded}, "task": task}
        for patch in task.get("workflow_patches", []): set_input(workflow, patch["node"], patch["input"], resolve(ctx, patch["value_from"]))
        patched_dir = ROOT / "logs" / "workflows"; patched_dir.mkdir(parents=True, exist_ok=True)
        write_json(patched_dir / f"{run_id}.json", workflow)
        response = requests.post(url.rstrip("/") + "/prompt", json={"prompt": workflow, "client_id": run_id}, timeout=60)
        response.raise_for_status(); prompt_id = response.json()["prompt_id"]
        deadline = time.time() + int(task.get("timeout_seconds", 3600)); history = None
        while time.time() < deadline:
            r = requests.get(url.rstrip("/") + f"/history/{prompt_id}", timeout=30); r.raise_for_status(); data = r.json()
            if prompt_id in data: history = data[prompt_id]; break
            time.sleep(2)
        if history is None: raise TimeoutError("ComfyUI job timed out")
        outdir = Path(task["output"]["directory"]).expanduser()
        if not outdir.is_absolute(): outdir = (ROOT / outdir).resolve()
        outdir.mkdir(parents=True, exist_ok=True)
        for node in history.get("outputs", {}).values():
            media = node.get("images", []) + node.get("gifs", []) + node.get("videos", [])
            for item in media:
                query = {k: item[k] for k in ("filename","subfolder","type") if k in item}
                blob = requests.get(url.rstrip("/") + "/view", params=query, timeout=300); blob.raise_for_status()
                destination = outdir / item["filename"]; destination.write_bytes(blob.content); outputs.append(str(destination))
        write_json(outdir / f"{run_id}.manifest.json", {"task": task, "compiled": compiled, "workflow_sha256": wfhash, "outputs": outputs})
        click.echo("\n".join(outputs) or json.dumps(history, indent=2))
    except Exception as exc:
        status = "error"; error = repr(exc); raise
    finally:
        append_ledger({"run_id": run_id, "timestamp": stamp, "task_id": task.get("id", ""), "operation": task.get("operation", ""), "provider": provider, "workflow_sha256": wfhash, "references": "|".join(map(str, refs)), "positive": compiled["positive"], "negative": compiled["negative"], "outputs": "|".join(outputs), "status": status, "error": error})

@main.command("new-task")
@click.argument("operation", type=click.Choice(sorted(VALID_OPERATIONS)))
@click.argument("task_id")
def new_task(operation: str, task_id: str) -> None:
    template = ROOT / "templates" / "tasks" / f"{operation}.yaml"
    if not template.exists(): template = ROOT / "templates" / "tasks" / "base.yaml"
    dest = ROOT / "tasks" / f"{task_id}.yaml"; dest.parent.mkdir(exist_ok=True)
    text = template.read_text(encoding="utf-8").replace("TASK_ID", task_id).replace("OPERATION", operation)
    dest.write_text(text, encoding="utf-8"); click.echo(str(dest))

if __name__ == "__main__": main()
