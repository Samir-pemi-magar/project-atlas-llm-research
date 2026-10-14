# Project ATLAS --- Small-Device LLM Research Lab

## Mission

Discover, implement, and experimentally validate methods that make capable large language models run better on resource-constrained devices without sacrificing more quality than necessary.

We optimize across a measured trade-off space:

- **Quality:** task performance and failure modes
- **Latency:** time to first token and generation throughput
- **Memory:** peak RAM/VRAM, model storage, and KV-cache use
- **Energy:** power and energy per generated token when measurable
- **Practicality:** implementation complexity, portability, and reproducibility

## Research principles

1. Measure before optimizing.
2. Establish strong, reproducible baselines.
3. Separate established prior art, hypotheses, implemented methods, and measured results.
4. Treat novelty as unproven until a targeted prior-art search supports it.
5. Prefer small experiments that can decisively falsify an idea.
6. Report negative and inconclusive results.
7. Never claim a result was measured unless the experiment was actually run.

## Shared instructions

- `ATLAS_INSTRUCTIONS.md` --- shared research standards for ChatGPT and Claude. Copy these instructions into both project settings; the repository file itself does not change those settings.

## Repository map

- `RESEARCH_STATE.md` --- current target, decisions, blockers, and next actions
- `LITERATURE_REVIEW.md` --- relevant prior art and source notes
- `HYPOTHESES.md` --- falsifiable research hypotheses
- `EXPERIMENT_LOG.md` --- experiment protocols and measured results
- `experiments/` --- experiment code, configs, and per-experiment notes
- `papers/` --- papers and reading notes; respect copyright and licenses

## Getting started

1. Read `ATLAS_INSTRUCTIONS.md` and `RESEARCH_STATE.md`.
2. Choose one open-weight model that can be evaluated on the target device.
3. Record the exact model revision, tokenizer, runtime, software versions, and license.
4. Run a baseline before changing quantization or inference behavior.
5. Record all measurements and commands in `EXPERIMENT_LOG.md`.
6. Search the literature and implementations before describing an approach as novel.

## Minimum baseline metrics

Where applicable, record:

- Model and exact revision
- Prompt/evaluation dataset and its version
- Runtime, backend, and relevant settings
- Hardware, operating system, drivers, and power mode
- Peak memory and model-file size
- Time to first token (TTFT)
- Decode throughput (tokens/second)
- Prompt-processing throughput
- Quality score and evaluation method
- Energy or power measurements, if available
- Warm-up policy, repetitions, summary statistic, and variability

## Research status

No experiments or performance results are recorded yet. The current focus is initial prior-art review and baseline planning.

See `RESEARCH_STATE.md` for the current state and next actions.

## Licensing

- **Code:** Licensed under the GNU General Public License v3.0 only (GPL-3.0-only). See [`LICENSE`](LICENSE).
- **Documentation and original research notes:** Licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). See [`LICENSE-DOCS`](LICENSE-DOCS).

These licenses apply only to material that the project contributors have the rights to license. Third-party papers, datasets, model weights, figures, code, and other materials remain subject to their respective licenses and rights. Do not assume this repository grants permission to redistribute third-party material.

Research results and ideas are not guaranteed to be novel or exclusive. Please cite relevant original publications when building on prior work.
