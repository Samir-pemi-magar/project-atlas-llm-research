# Prior-Art Scan — 2026-10-15

**Status:** Targeted first-pass scan; not exhaustive and not an independent reproduction.  
**Purpose:** Reassess ATLAS candidate directions against recent papers and publicly available implementations before selecting a novel contribution.

## Executive assessment

The original H-001—apply a reversible tensor-aware transformation and a general-purpose compressor to stored model weights—is **not currently a defensible novelty claim**. Multiple papers and active implementations now address lossless LLM-weight compression, entropy-aware representations, or decompression fused into GPU kernels. Keep the idea as a baseline/replication question only until source-level comparisons identify a narrower gap.

The initial baseline experiment remains necessary: a controlled local inference reference is useful regardless of which research direction is selected. It must remain separate from compression-method claims.

## Weight compression and compressed execution

### Tan et al. — Approaching Shannon Bound with Lossless LLM Weight Compression
- Paper: https://arxiv.org/abs/2606.15789
- Venue noted by arXiv: accepted to ISCA 2026.
- Mechanism: entropy analysis and tile-level, on-the-fly lossless decompression using Asymmetric Numeral Systems aligned to GPU GEMM tiling.
- Authors report improved feasible batch size and throughput when integrated with SGLang.
- Direct overlap: lossless compression of LLM weights plus decompression integrated into inference.
- To inspect next: full paper, exact formats and kernel requirements, source availability, memory overhead, and whether the method can be tested on an RTX 4060-class device.

### ZipServ — hardware-aware lossless compression
- Code: https://github.com/QuiverDance/ZipServ_ASPLOS26
- Paper is described in the repository as an ASPLOS 2026 paper.
- Mechanism: tensor-core-aware triple bitmap encoding and fused decompression/GEMM, designed for NVIDIA GPUs using GDDR memory.
- Repository reports up to 30% weight-size reduction, up to 2.21x kernel speedup, and 1.22x average end-to-end speedup over its vLLM baseline. These are authors' claims, not ATLAS measurements.
- Direct overlap: compressed weights decoded during computation, with the goal of reducing bytes moved without changing weight values.
- To inspect next: supported architectures, memory and model formats, build burden, baseline matching, and whether code runs on the RTX 4060 laptop GPU.

### Neural Weight Compression (NWC)
- Code: https://github.com/parda21/NWC
- Mechanism: losslessly entropy-coded BF16 byte planes decoded inside CUDA matrix-vector kernels; also documents a separate weight-only FP8 path where the FP8 values are stored losslessly after quantization.
- Repository reports bit-identical outputs for its BF16 path and throughput/memory results on RTX 4070 and NVIDIA A16 hardware. These results have not been reproduced by ATLAS.
- Direct overlap: lossless weight compression integrated into execution. The RTX 4070 results make Ada-generation consumer GPU compatibility particularly relevant.
- To inspect next: exact commit and environment, supported GPU architectures, installation/build requirements, numerical equivalence scope, and fair baselines.

### Split12 / weight-compression research ledger
- Code and experiment record: https://github.com/brianbell-x/weight-compression
- The repository reports bit-exact BF16 reconstruction across a large model scan and provides an inference/kernel results ledger, including a reported result where an initially favorable comparison was overturned by a better-matched serving baseline.
- Direct overlap: byte-plane and codebook approaches to lossless model weight representation.
- Methodological lesson: kernel microbenchmarks and end-to-end serving results are distinct; a baseline mismatch can reverse a performance conclusion.

### ZipNN
- Code: https://github.com/zipnn/zipnn
- General-purpose tensor-aware lossless compression library with data-type-specific preparation and compression.
- Relevant baseline for compressed checkpoint storage and CPU-side compression/decompression. Its storage ratios alone do not establish runtime VRAM or decode-speed benefits.

### z4ai
- Code: https://github.com/z4ai/z4ai
- A checkpoint codec emphasizing per-tensor random access, structured/repeated data, and cross-checkpoint deltas.
- The project itself states that dense floating-point checkpoint compression has a ceiling imposed by the near-random mantissa; large gains arise when there is additional structure such as wide containers for quantized values, sparsity, duplicate tensors, or related checkpoints.
- Potentially relevant if ATLAS studies checkpoint registries or sequences of related model versions rather than single-file runtime inference.

## KV-cache and long-context directions

### TurboQuant integrations
- llama.cpp integration example: https://github.com/Keyvanhardani/turboquant-ggml
- CUDA-focused fork: https://github.com/TiredOfEverything/llama-cpp-turboquant
- These public implementations report 3–5x-class KV-cache reductions depending on format, implementation, and workload. Reported quality/speed results vary by model; treat repository benchmark tables as claims until independently reproduced.
- Relevance: a practical route to studying context length under a fixed 8 GB VRAM budget. It is approximate quantization, so quality must be measured separately from memory and speed.

### HeadInfer
- Paper: https://arxiv.org/abs/2502.12574
- Mechanism: head-wise KV-cache offloading to CPU memory while keeping selected cache data on GPU.
- Relevance: capacity extension for long context; transfers, CPU work, and available system RAM may dominate on a laptop.

### RocketKV
- Paper: https://proceedings.mlr.press/v267/behnam25a.html
- Code: https://github.com/NVlabs/RocketKV
- Mechanism: token eviction plus sparse attention. It is approximate and should be compared using task-level quality metrics, not only cache compression ratio.

### ATSInfer — Automated Tensor Scheduling for Hybrid CPU-GPU LLM Inference
- Paper: https://arxiv.org/abs/2607.10183
- A public implementation/prototype reference: https://github.com/lordnyx0/ik_llama-atsinfer
- Mechanism: tensor-granularity placement and asynchronous CPU/GPU coordination for consumer devices.
- Important caution: a public integration audit reports that ATSInfer itself did not improve decode throughput on its tested hardware. This is a reminder to measure on our exact device and not infer gains from a paper's headline results.

## Initial opportunity map

| Direction | Prior-art saturation | ATLAS feasibility | Current disposition |
|---|---|---|---|
| Generic reversible transform + Zstandard on weights | High | High | Keep as a replication/control only; do not claim novelty |
| Port/reproduce fused lossless weight compression on RTX 4060 | High | Medium; CUDA toolchain and memory constraints need checking | Candidate for practical replication, not yet a novel contribution |
| KV-cache quantization on fixed 8 GB VRAM with quality-speed-memory trade-offs | High and active | Potentially high through existing llama.cpp stack | Candidate controlled evaluation; first verify exact runtime support and choose tasks |
| Hybrid CPU/GPU offload policies on laptop hardware | Active | Medium; system-RAM and PCIe constraints matter | Candidate only after profiling and source-level review |
| Cross-checkpoint delta compression for model/fine-tune registries | Less directly related to online token decode | High for storage-only tests | Possible alternative if ATLAS includes checkpoint lifecycle/storage workloads |
| Automated policy selection across model, context, and memory budget | Crowded at a high level; specific deployment gap unknown | Potentially high after a baseline matrix exists | Do not claim novelty until a concrete gap is established |

## Recommended decision sequence

1. Complete the local baseline harness validation and collect a defensible reference.
2. Inspect source code and paper details for NWC and ZipServ; determine whether a realistic RTX 4060 reproduction is possible without changing the current runtime or installing anything yet.
3. In parallel, document which KV-cache formats are supported by the current llama.cpp build and define a small task-level quality suite before running any comparison.
4. Use Claude for an independent prior-art and methodology critique of the concrete candidate, not for unverified claims or generic brainstorming.
5. Select the next research hypothesis only after the implementation requirements, closest baselines, failure modes, and testable gap are documented.

## Evidence boundary

This scan is based on publicly accessible paper abstracts, repository documentation, and reported project results. It is **not** a full-paper review of every cited work, source-code audit, independent replication, or novelty determination. No software was installed, no external repository was cloned, and no ATLAS benchmark was run for this scan.

## Independent review update — 2026-10-15

Claude's independent review identified gaps in this first-pass scan. This update records them as open verification tasks rather than treating the scan as exhaustive.

### Additional direct baselines to review

- **DFloat11:** https://arxiv.org/abs/2504.11651 and https://github.com/LeanModels/DFloat11. Directly relevant lossless BF16 compression and GPU decompression baseline; paper/source review is pending.
- **NeuZip:** https://arxiv.org/abs/2410.20650. Identified through related-work references; primary paper and implementation status still need direct verification.
- **TurboQuant:** https://arxiv.org/abs/2504.19874. Add the primary paper and its quality/memory claims to the KV-cache review; third-party llama.cpp forks are integrations, not substitutes for the paper.
- **Native llama.cpp baselines:** document supported KV-cache types and native offload flags at the exact pinned commit before evaluating a fork or external method.

### Repository discrepancy and evidence limits

The ZipServ paper's repository link appears to point to `HPMLL/ZipServ_ASPLOS26`, while this scan originally linked `QuiverDance/ZipServ_ASPLOS26`. Their relationship is **unresolved**; do not assume they are equivalent until the canonical link, repository history, and code provenance are checked.

The scan has not established whether DFloat11, NeuZip, ZipServ, NWC, or other closest methods support GGUF K-quants or integrate with the pinned llama.cpp build. No novelty claim follows from the absence of a feature in this preliminary scan. A systematic search across paper databases, GitHub code/issues/PRs, and Hugging Face remains outstanding.

### Candidate research directions after baseline

1. Entropy census of the already-cached Q4_K_M file, with a pre-registered kill threshold and comparison against the native quantization ladder at comparable bits per weight. This is a screening test, not a novelty claim.
2. Fixed-VRAM comparison of weight precision, native KV-cache precision, and context allocation, with task-level quality measured separately from speed and memory.

Both remain characterization or replication directions until closest prior art and implementations are reviewed.
