# Research State

> Update this file whenever a decision, target, blocker, or next action changes. This file is the concise source of truth for the project.

## Status
- **Phase:** Setup / prior-art review and baseline planning
- **Last updated:** 2026-10-14
- **Owner:** TODO
- **Repository:** `project-atlas-llm-research`

## Research objective
Investigate generalizable methods for making capable LLMs more accessible under constrained GPU memory, system RAM, storage, and context budgets. Explore weight representation, lossless and approximate compression, memory hierarchy, context/KV-cache efficiency, and execution strategy. Preserving capability and broad model/device applicability are goals to test, not guarantees.

## Target environment
User-provided Windows measurements (2026-10-14; snapshots may change):
- **GPU:** NVIDIA GeForce RTX 4060
- **Reported GPU memory:** 8,188 MiB
- **GPU memory occupied at measurement:** about 1,729 MiB
- **Installed system RAM:** 32,472 MB
- **Available system RAM at measurement:** 10,216 MB
- **C: drive:** 452.6 GB total; 115.3 GB free
- **Operating system:** Windows (exact version/build TODO)
- **CPU:** TODO
- **Driver / CUDA / runtime:** TODO
- **Power or thermal constraints:** TODO
- **Primary workload:** TODO (choose a reproducible first workload; likely single-user local inference)
- **Connectivity constraints:** Online for literature/downloads; offline requirement TODO

These measurements describe one point in time, not guaranteed free capacity. Recheck before downloads and experiments.

## Baseline model
- **Model name and source:** TODO
- **Exact revision / commit:** TODO
- **Tokenizer revision:** TODO
- **License:** TODO
- **Parameter count:** TODO
- **Weight format / quantization:** TODO
- **Context length tested:** TODO
- **Evaluation dataset / tasks:** TODO

## Success criteria
Set measurable targets before optimizing. Do not fill these with guessed values.

| Metric | Baseline | Target | Measurement method |
|---|---|---|---|
| Output quality | TODO | TODO | Fixed task set and metric |
| Time to first token | TODO | TODO | Repeated timed runs |
| Decode throughput (tokens/s) | TODO | TODO | Fixed prompt/output length |
| Peak GPU memory | TODO | TODO | Runtime telemetry |
| Peak system RAM | TODO | TODO | OS/runtime telemetry |
| Model storage | TODO | TODO | File sizes on disk |
| Load/decompression time | TODO | TODO | Separate cold/warm measurements |
| Energy per token | TODO | TODO | If reliable measurement is available |
| Implementation complexity | TODO | TODO | Document dependencies and code changes |

## Current decisions
- No method is considered novel without a documented prior-art search.
- Establish and record a baseline before tuning.
- Keep model weights, access tokens, and credentials out of this repository.
- Record exact versions, configuration, commands, and model revisions.
- Report failed and inconclusive runs, not just successful ones.
- Distinguish lossless reconstruction from unchanged task quality: they are different guarantees.
- Measure storage, memory capacity, memory traffic, latency, and quality separately.
- Do not assume a compressed on-disk format reduces runtime VRAM or improves speed; test the full path and decompression overhead.

## Current bottleneck
**Unknown — profile the baseline first.** Possible bottlenecks include GPU VRAM capacity, system RAM, memory bandwidth, compute throughput, load/decompression overhead, prompt prefill, decode, KV-cache growth, thermal throttling, and runtime/kernel limitations.

## Prior-art review: initial finding
Lossless weight compression and memory-aware representation are already active research areas. In particular, Tan et al., “Approaching Shannon Bound with Lossless LLM Weight Compression” (arXiv:2606.15789; accepted to ISCA 2026) describes entropy-aware tile-level lossless decompression aligned with GPU GEMM tiling. Xie et al., “Reimagining Memory Access for LLM Inference” (arXiv:2503.18869) describes bit-plane rearrangement and lossless compression-aware memory access. Therefore, “losslessly compress LLM weights” or “reorder weight bits to improve compression” is not a defensible novelty claim by itself. A possible research gap must be narrower and verified against these works, their implementations, and other related systems.

Long-context memory has extensive prior art too, including HeadInfer and RocketKV. Any ATLAS work on KV cache must compare against the closest methods and clearly separate exact offloading from approximate eviction/quantization.

## Open questions
1. Which model and workload fit the available hardware and answer a meaningful question?
2. What are the actual CPU, OS build, driver, CUDA/runtime, and inference engine versions?
3. Is the main limitation capacity, bandwidth, compute, context/KV cache, or runtime overhead?
4. What quality regression, if any, is acceptable for a measurable efficiency gain?
5. Which concrete gap remains after reproducing the closest relevant prior art?

## Next actions
- [ ] Record exact Windows build, CPU, GPU driver, and available inference runtimes.
- [ ] Choose one small open-weight model and record exact revision, tokenizer, license, and format.
- [ ] Choose a fixed, small evaluation workload and define quality/latency/memory measurements.
- [ ] Run an unmodified baseline with repeated trials.
- [ ] Expand the prior-art review, beginning with lossless weight compression and hardware-aware representations.
- [ ] Only then select a specific research hypothesis and failure criterion.

## Decision log
| Date | Decision | Reason | Evidence / experiment |
|---|---|---|---|
| 2026-10-14 | Use the RTX 4060 Windows PC as the initial test environment | Concrete available hardware makes small reproducible experiments possible | User-provided system measurements; baseline not yet run |
| 2026-10-14 | Review lossless weight compression prior art before choosing a contribution | Closely related published work already exists | Initial source review in `LITERATURE_REVIEW.md` |
