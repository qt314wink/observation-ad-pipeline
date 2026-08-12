# Architecture and control gates

G0 intake: operation and objective declared. G1 evidence: observations separated from inferences. G2 contract: locks/allowed/prohibited changes. G3 concept: distinct argument, proof, click/share reason. G4 distillation: bounded prompt. G5 model compatibility: checkpoint, VAE, text encoder, LoRA base family, hashes and license. G6 workflow validation: API-format JSON and node patches resolve. G7 execution: immutable run ID, seed and workflow hash. G8 QA: identity/product integrity, duration, dimensions, safe zones, no black tail, message match. G9 archive: source contract, compiled prompt, workflow, ledger and selected/rejected outputs.

ComfyUI receives workflow JSON at `/prompt`, not the narrative schema directly. This package deliberately maps semantic task fields into named node inputs. Reference files are uploaded first and the returned filename is patched into loader nodes. Folder references expand deterministically in sorted order.

Colab is a hosted notebook service, not itself an open-source VM. The inference engine and pipeline are open source; Colab merely supplies an ephemeral GPU. For stable production use, run the same ComfyUI server on a controlled GPU host and expose it through authenticated networking rather than a public temporary tunnel.


## Structured motion domain

Optional task `motion_system` data is schema-validated, cross-field validated, normalized, distilled to no more than five model-visible actions, and retained in the immutable compiled manifest. `src/obsad/motion.py` owns motion vocabulary, semantic validation, deterministic compilation, and field-level splice comparison; the CLI remains the orchestration boundary.

Audio bindings are `declared_editorial` or `external_markers` unless a `measured_analysis` binding names its analysis artifact. Exact cuts, captions, platform-native audio, and CTA timing remain deterministic post-production responsibilities.
