# Research State

> Update this file whenever a decision, target, blocker, or next action changes. This file is the concise source of truth for the project.

## Status
- **Phase:** Harness remediation after independent review; prior-art expansion
- **Last updated:** 2026-10-15
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
- **Operating system:** Windows 10 Home Single Language; reported build 26340; Ubuntu 26.04 LTS under WSL2
- **CPU:** Intel Core i9-14900HX (24 cores / 32 logical processors)
- **Driver / CUDA / runtime:** Windows NVIDIA driver 610.74; CUDA UMD 13.3; WSL2 kernel 6.18.33.2-microsoft-standard-WSL2; llama.cpp server image ID recorded below
- **Power or thermal constraints:** Not yet characterized
- **Primary workload:** Single-user local inference, batch size 1
- **Connectivity constraints:** Online currently; offline requirement not yet defined

These measurements describe one point in time, not guaranteed free capacity. Recheck before downloads and experiments.

## Baseline model
- **Model name and source:** Qwen3-1.7B-GGUF, published by ggml-org on Hugging Face
- **Exact revision / commit:** `daeb8e2d528a760970442092f6bf1e55c3b659eb`
- **Model file:** `Qwen3-1.7B-Q4_K_M.gguf`
- **Model file SHA-256:** `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`
- **License:** Verify against the model repository before public distribution or derivative use
- **Parameter count:** Approximately 2.03 billion, as reported by the running llama.cpp server
- **Weight format / quantization:** GGUF, Q4_K_M
- **Context length planned:** 4096 tokens; isolated diagnostic pilot succeeded; formal benchmark not run
- **Evaluation dataset / tasks:** Planned fixed set of 20 prompts; not yet created or evaluated
- **Runtime image ID:** `sha256:b0baccbe2e00b5d74e63f85f9f023c93d61d0f329475269e1e7002e87eb875ea`
- **Runtime alias in existing DocPilot service:** `docpilot-qwen3-1.7b`; ATLAS will use a separate disposable container/port
- **ATLAS diagnostic GPU offload:** Verified in the isolated verbose diagnostic container: 29/29 layers offloaded; CUDA model buffer 1050.43 MiB and KV buffer 448.00 MiB. This is diagnostic evidence, not a formal benchmark.

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

## Updated prior-art finding (2026-10-15)

The broad H-001 direction—reversible tensor-aware transformation plus a general-purpose compressor—is crowded and is not a defensible novelty claim as stated. Newly identified direct overlaps include ZipServ (hardware-aware lossless compression with fused GPU kernels), Neural Weight Compression (NWC; lossless compressed weights decoded inside CUDA matvec), Split12, and Tan et al. (ISCA 2026). See `research/PRIOR_ART_SCAN_2026-10-15.md` for source links and the limits of this first-pass review. Keep H-001 as a replication/control question pending source-level comparison; do not treat it as the intended contribution.

Additional active directions include KV-cache quantization/offloading and hybrid CPU/GPU tensor scheduling. These are also crowded areas; any new hypothesis needs a narrow, evidence-backed gap and task-level quality evaluation.

## Open questions
1. Which model and workload fit the available hardware and answer a meaningful question?
2. What are the actual CPU, OS build, driver, CUDA/runtime, and inference engine versions?
3. Is the main limitation capacity, bandwidth, compute, context/KV cache, or runtime overhead?
4. What quality regression, if any, is acceptable for a measurable efficiency gain?
5. Which concrete gap remains after reproducing the closest relevant prior art?

## Next actions
- [x] Record available CPU, OS, driver, GPU, and runtime details from user-provided inspection.
- [x] Select a cached candidate model and verify its resolved model-file SHA-256.
- [x] Write an isolated baseline pilot protocol at `experiments/EXP-20261014-001-baseline/README.md`.
- [x] Run an isolated diagnostic pilot on port 3001 and a verbose diagnostic on port 3002 without modifying DocPilot; verify actual GPU offload and capture smoke-test responses. These were diagnostic only.
- [x] Draft a fixed 20-prompt workload and standard-library measurement harness; files are on branch `research/baseline-harness-and-prior-art`. Not yet executed or independently reviewed.
- [x] Obtain independent Claude review of the protocol/harness. Verdict: READY AFTER FIXES; major blockers include model alias mismatch, unverified runtime provenance, incomplete cache/slot controls, likely truncation, and host-wide telemetry.
- [ ] Finish harness remediation: runtime identity/hash/launch verification, pinned cache/slot settings, request-level failure enforcement, provenance and telemetry improvements. The draft has not been syntax-checked after edits.
- [ ] Run syntax and plan-only checks in a local clone after remediation. These checks must not contact the server. Obtain authorization before any live validation or formal benchmark.
- [ ] Inspect DFloat11, NeuZip, Tan et al., ZipServ and NWC papers/source requirements; resolve the canonical ZipServ repository discrepancy; add native llama.cpp KV/offload baselines; verify model license before public distribution.
- [ ] Select the next hypothesis only after baseline profiling and a specific prior-art gap are documented.

## Decision log
| Date | Decision | Reason | Evidence / experiment |
|---|---|---|---|
| 2026-10-14 | Use the RTX 4060 Windows PC as the initial test environment | Concrete available hardware makes small reproducible experiments possible | User-provided system measurements; baseline not yet run |
| 2026-10-14 | Review lossless weight compression prior art before choosing a contribution | Closely related published work already exists | Initial source review in `LITERATURE_REVIEW.md` |
| 2026-10-14 | Use the cached Qwen3-1.7B Q4_K_M artifact as the first baseline candidate | Avoid an unnecessary model download and make the first experiment practical | Snapshot revision and SHA-256 verified inside existing container; ATLAS pilot still pending |
| 2026-10-14 | Isolate ATLAS inference in a separate disposable container on host port 3001 | Avoid affecting the existing DocPilot app and its PostgreSQL service | Diagnostic containers used ports 3001 and 3002; DocPilot services were left untouched |
| 2026-10-15 | Use the chat-completion endpoint with thinking disabled for the harness draft | Raw completion produced poor/repetitive text; chat endpoint returned a coherent answer with `enable_thinking=false` | User-provided diagnostic responses; not formal benchmark evidence |
| 2026-10-15 | Treat generic lossless weight compression as a crowded direction, not a novelty claim | Recent papers and active code directly overlap with H-001 | Targeted source triage in `research/PRIOR_ART_SCAN_2026-10-15.md`; full paper/source review remains incomplete |
| 2026-10-15 | Do not run the baseline until harness fixes are completed | Independent review found an alias mismatch, unverified runtime identity, incomplete cache/slot controls, likely output truncation, and telemetry attribution gaps | Claude independent review; no benchmark run or live validation authorized |
