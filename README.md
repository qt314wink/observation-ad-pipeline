# Observation-Led Ad Pipeline v0.3.0

Termux compatibility release. Replaces the native Rust-backed `jsonschema/rpds-py` dependency with pure-Python `fastjsonschema`, and removes unused Pydantic/WebSocket dependencies.

# Observation-Led Ad Pipeline v2

A Termux control plane and ComfyUI remote-GPU runner for evidence-led image/video generation, reference editing, transformation, variation, extension, prompt compilation, and motion specification.

## Install on Android

```bash
termux-setup-storage
mkdir -p ~/Projects
cp ~/storage/downloads/observation-ad-pipeline-v2.zip ~/Projects/
cd ~/Projects
unzip observation-ad-pipeline-v2.zip
cd observation-ad-pipeline-v2
bash setup-termux.sh "$HOME/Projects/observation-ad-pipeline-v2"
source .venv/bin/activate
obsad doctor
```

## Commands

```bash
obsad doctor
obsad new-task edit product-edit-01
obsad validate tasks/product-edit-01.yaml
obsad compile tasks/product-edit-01.yaml
obsad run tasks/product-edit-01.yaml --dry-run
obsad run tasks/product-edit-01.yaml --url "$COMFY_URL"
```

Put local references under `input/images`, `input/videos`, or any folder named in a task. Generated media and immutable run manifests are saved under the task's `output.directory`. Every execution is recorded in `logs/runs.csv`, `logs/runs.jsonl`, and `logs/runs.txt`.

The full master contract remains the source of truth. The compiler reduces it to: TASK → LOCK → MOTION → CAMERA → EVENT → FINAL → STYLE → NEGATIVE. Text overlays and exact ad timing belong in deterministic post-production.


## Recursive mandala motion

Tasks may declare an optional `motion_system` for center lock, symmetry, addressable layers, recursive transforms, editorial audio bindings, splice continuity, and QA tolerances. `obsad compile` emits a deterministic `motion_manifest` only for opted-in tasks, so legacy tasks keep their prior compiled shape.

```bash
obsad validate examples/tasks/recursive-mandala-motion.yaml
obsad compile examples/tasks/recursive-mandala-motion.yaml
obsad splice-check exit-state.yaml entry-state.yaml
```

The four initial mandala videos are registered as external governed evidence fixtures; their binaries and hashes are intentionally absent pending governed ingestion.
