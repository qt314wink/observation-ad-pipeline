# NOURISH THE SIGNAL

An execution-ready, provider-neutral OBSAD campaign package for Calcium+Company. The governed mechanism translates a visible biological signal into a recognizable human gesture: **SIGNAL → STORY → MOVEMENT**.

## Build order and status

1. **Observe:** `observations/evidence.yaml` separates sourced observations from creative inferences.
2. **Contract:** `creative-contract.json` governs the campaign; `tokens.json` is its controlled vocabulary.
3. **Compile:** `prompts/semantic.yaml` is compiled through provider adapters, never maintained as independent giant prompts.
4. **Stage:** keyframes precede motion isolates; isolates precede assembly; derivatives trace to the master.
5. **Evaluate:** ledgers retain selected and rejected candidates, with blocking safety and integrity gates.
6. **Archive:** lightweight manifests are committed. No generated media is represented as completed when no runtime was available.

## Reconstructable proof chain

`OBSERVATION → CREATIVE INFERENCE → CONTRACT → TOKENS → PROMPT → MODEL / WORKFLOW → CANDIDATES → EVALUATION → REJECTION / SELECTION → MOTION ASSEMBLY → CHANNEL ADAPTATION → FINAL`

Run `python -m obsad.cli campaign-validate campaigns/calcium-nourish-the-signal` and `python -m obsad.cli campaign-compile campaigns/calcium-nourish-the-signal --provider openai` from the repository root.

The campaign-specific package does not alter generic provider semantics. Model IDs are read from environment-named configuration fields and remain unresolved until execution.
