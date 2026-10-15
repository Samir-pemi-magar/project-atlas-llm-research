# Literature Review and Prior Art

> Status: initial source triage on 2026-10-14. The entries below are summaries of source pages/abstracts and are **not yet full-paper replications or independent verification of every result**. Treat authors' reported numbers as reported claims, not ATLAS measurements.

## Initial assessment

Two major paths must be separated:

1. **Weights / model residency:** reduce the bytes needed to store and move model parameters. Lossless compression can preserve exact stored values, but only yields runtime benefits when the compressed representation, decompressor, memory transfers, and kernels are integrated efficiently.
2. **Context / KV cache:** reduce memory required to retain past tokens. Some approaches are approximate (quantization, eviction, sparse attention); others offload or reorganize data. Results for long-context serving do not automatically solve model-weight storage.

This literature already includes work directly on lossless weight compression and bit-plane data layouts. ATLAS should not claim those ideas as novel. The promising next step is to identify a specific under-tested constraint (for example, practical software-only integration on a consumer GPU, model-format coverage, decompression overhead, or a measured portability limitation), after inspecting papers and available code.

## Source ledger

### 1. Approaching Shannon Bound with Lossless LLM Weight Compression
- **Citation:** Hongshi Tan, Yao Chen, Gustavo Alonso, Weng-Fai Wong, Bingsheng He. “Approaching Shannon Bound with Lossless LLM Weight Compression.”
- **URL / DOI:** https://arxiv.org/abs/2606.15789
- **Publication date / version:** Submitted 2026-06-14; arXiv page says accepted to ISCA 2026.
- **Source type:** Research paper.
- **Problem addressed:** Storage and memory-capacity pressure from LLM weights.
- **Core mechanism:** Entropy analysis plus tile-level, on-the-fly lossless decompression using Asymmetric Numeral Systems aligned to GPU GEMM tiling.
- **Reported benefits:** Abstract reports bit rates close to the Shannon limit, larger feasible batch sizes and throughput gains in an SGLang-integrated system.
- **Limitations / failure cases:** These are the authors' reported results; hardware/software setup, implementation availability, end-to-end costs, and relevance to a single RTX 4060 must be examined in the full paper. Compression ratio is not a universal constant across formats or models.
- **Code and license:** Not established in this initial review.
- **Relevance to ATLAS:** Directly overlaps with lossless weight representation and runtime decompression. Read first before proposing a similar method.
- **Closest overlap with our hypotheses:** Lossless weight compression with decompression aligned to matrix multiplication.
- **Verification status:** Abstract/page reviewed; full paper and code not yet reviewed.

### 2. Reimagining Memory Access for LLM Inference: Compression-Aware Memory Controller Design
- **Citation:** Rui Xie, Asad Ul Haq, Linsen Ma, Yunhua Fang, Zirak Burzin Engineer, Liu Liu, Tong Zhang. “Reimagining Memory Access for LLM Inference: Compression-Aware Memory Controller Design.”
- **URL:** https://arxiv.org/abs/2503.18869
- **Publication date:** 2025-03-24.
- **Source type:** Research paper / hardware design.
- **Problem addressed:** Model-weight and KV-cache memory bandwidth and capacity.
- **Core mechanism:** Bit-plane disaggregation and cross-token KV-cache clustering/de-correlation to improve lossless compression; proposed hardware memory-controller integration.
- **Reported benefits:** The paper reports reductions in model-weight and KV-cache footprint, plus simulated latency and energy improvements.
- **Limitations / failure cases:** Central design assumes hardware/memory-controller mechanisms not available to ordinary software on a consumer GPU. Its results do not prove a drop-in software method will yield the same gains.
- **Code and license:** Not established in this initial review.
- **Relevance to ATLAS:** Strong prior art for bit-plane layouts and lossless compression; narrows potential software-only research questions.
- **Closest overlap with our hypotheses:** Reversible tensor/data-layout transformations to expose redundancy.
- **Verification status:** arXiv page and substantial text reviewed; implementation not yet checked.

### 3. HeadInfer: Memory-Efficient LLM Inference by Head-wise Offloading
- **Citation:** Cheng Luo et al. “HeadInfer: Memory-Efficient LLM Inference by Head-wise Offloading.”
- **URL:** https://arxiv.org/abs/2502.12574
- **Publication date:** 2025-02-18.
- **Source type:** Research paper.
- **Problem addressed:** GPU-memory growth from long-context KV cache.
- **Core mechanism:** Offloads KV cache to CPU RAM while retaining selected attention-head cache data on GPU and computing attention dynamically.
- **Reported benefits:** Abstract reports large KV-cache memory reduction on Llama 3 8B at million-token contexts.
- **Limitations / failure cases:** Reported extreme-context results use a 24 GB RTX 4090 and do not directly transfer to an 8 GB RTX 4060. CPU-GPU transfer costs and system RAM are important; our available RAM snapshot was about 10 GB.
- **Code and license:** Not established in this initial review.
- **Relevance to ATLAS:** Relevant if long context is selected as the first workload; not a direct solution to weight-file storage.
- **Verification status:** Abstract reviewed; full paper and code not yet reviewed.

### 4. RocketKV: Accelerating Long-Context LLM Inference via Two-Stage KV Cache Compression
- **Citation:** Payman Behnam et al. “RocketKV: Accelerating Long-Context LLM Inference via Two-Stage KV Cache Compression.” ICML 2025, PMLR 267.
- **URL:** https://proceedings.mlr.press/v267/behnam25a.html
- **Publication date:** ICML 2025.
- **Source type:** Peer-reviewed conference paper.
- **Problem addressed:** KV-cache memory and attention cost in long-context decoding.
- **Core mechanism:** Training-free coarse token eviction plus fine-grained top-k sparse attention.
- **Reported benefits:** The paper reports high compression ratios, decode speedups, and reduced peak memory on an NVIDIA A100 with negligible accuracy loss on tested tasks.
- **Limitations / failure cases:** Eviction and sparse attention are approximate; “negligible” loss is workload-dependent. A100 results are not evidence of equivalent gains on consumer hardware.
- **Code:** Paper page links source code at https://github.com/NVlabs/RocketKV
- **Relevance to ATLAS:** Strong baseline if we pursue context/KV optimization.
- **Verification status:** PMLR paper page reviewed; code not yet inspected.

### 5. Compressing KV Cache for Long-Context LLM Inference with Inter-Layer Attention Similarity (PoD)
- **Citation:** Da Ma et al. “Compressing KV Cache for Long-Context LLM Inference with Inter-Layer Attention Similarity.”
- **URL:** https://arxiv.org/abs/2412.02252
- **Publication date / version:** Submitted 2024-12-03; revised 2025-08-04.
- **Source type:** Research paper.
- **Problem addressed:** KV-cache growth for long contexts.
- **Core mechanism:** Retains full cache for proximal tokens and shares key states across layers for distant tokens, with post-training adaptation.
- **Reported benefits:** Abstract reports up to 35% KV-cache reduction without measured performance loss on its tested benchmarks.
- **Limitations / failure cases:** Results are benchmark- and model-dependent; the adaptation and implementation costs require review.
- **Relevance to ATLAS:** Another close prior-art reference for cross-layer redundancy and context memory.
- **Verification status:** arXiv abstract reviewed; full paper/code not yet reviewed.

## Comparison table

| Method | Primary resource | Mechanism | Fidelity class | Platform relevance | Main caution |
|---|---|---|---|---|---|
| Tan et al. (2026) | Weight storage / memory traffic | Entropy coding and tile-level on-the-fly decompression | Lossless weights | Integrated GPU serving system | Must inspect software and hardware requirements |
| Xie et al. (2025) | Weights and KV cache | Bit-plane layouts, clustering, lossless compression | Lossless representation; additional dynamic quantization is approximate | Proposed memory-controller design | Hardware mechanism may not be reproducible in software |
| HeadInfer (2025) | KV cache | Head-wise CPU offloading | Described as avoiding approximation in its offloading strategy | Long-context GPU inference | CPU-GPU transfers and RAM capacity |
| RocketKV (2025) | KV cache | Eviction plus sparse attention | Approximate | GPU inference | Accuracy depends on task and cache budget |
| PoD (2024/2025) | KV cache | Cross-layer key sharing | Adapted architecture/cache representation | Long-context inference | Requires adaptation; task-specific evaluation |

## Search protocol and history

- **Date:** 2026-10-14
- **Queries / scope:** Lossless LLM weight compression; compression-aware memory representation; KV-cache compression and offloading. Focused on primary arXiv and PMLR pages.
- **Useful finding:** Both lossless weight compression and bit-plane-based representation have direct prior art. KV-cache compression/offloading is a large, mature field with a mix of exact and approximate methods.
- **Coverage limitations:** This is an initial focused review, not an exhaustive survey. It has not yet reviewed patents, all related papers, code implementations, or the full details of the cited papers.

## Novelty assessment

No novelty claim is justified yet. Do not frame “losslessly compress weights,” “reorder weight bits,” or “compress KV cache” as new. Potentially meaningful questions must be narrower and supported by an implementation-aware comparison, such as:
- What software-only reversible transforms improve compression over strong baselines on real model formats, after accounting for metadata and decode time?
- Can a general-purpose consumer-GPU inference pipeline exploit compressed weights without needing a custom memory controller, and what is the break-even point?
- Which bottleneck actually limits the user's local workload: weight residency, transfer bandwidth, KV cache, or compute?

These are questions to investigate, not novelty claims.


## Targeted update — 2026-10-15

A new targeted scan found direct, active overlaps with H-001 beyond the initial triage. See [the detailed prior-art scan](research/PRIOR_ART_SCAN_2026-10-15.md).

### Newly identified direct overlaps

- **ZipServ:** https://github.com/QuiverDance/ZipServ_ASPLOS26 — tensor-core-aware bitmap encoding and fused decompression/GEMM; repository reports weight-size reduction and inference speedups.
- **Neural Weight Compression (NWC):** https://github.com/parda21/NWC — losslessly entropy-coded BF16 byte planes decoded inside CUDA matrix-vector kernels; reports tests on RTX 4070 and NVIDIA A16.
- **Split12 / weight-compression ledger:** https://github.com/brianbell-x/weight-compression — byte-plane/codebook weight compression, exact reconstruction checks, and an inference record that documents a benchmark comparison overturned by a better-matched serving baseline.
- **ZipNN:** https://github.com/zipnn/zipnn — tensor-aware lossless compression, relevant as a storage baseline.
- **z4ai:** https://github.com/z4ai/z4ai — lossless checkpoint codec with emphasis on tensor structure, wide containers, sparsity, and deltas across related checkpoints.
- **TurboQuant llama.cpp integrations:** https://github.com/Keyvanhardani/turboquant-ggml and https://github.com/TiredOfEverything/llama-cpp-turboquant — active KV-cache quantization implementations; repository claims need workload-specific quality and speed validation.
- **ATSInfer:** https://arxiv.org/abs/2607.10183 — tensor-granularity CPU/GPU scheduling for consumer devices. A public integration audit at https://github.com/lordnyx0/ik_llama-atsinfer reports no decode-throughput improvement from ATSInfer on its tested setup, underscoring that paper results must be tested against the target runtime and hardware.

### Updated interpretation

The generic idea of applying a reversible tensor-aware transform and a general-purpose compressor to model weights is not a defensible novelty claim. H-001 remains a replication/control question until full-paper and source-level comparison finds a narrow gap. Do not claim novelty based on a different wrapper or an untested combination of known methods.

Potential future directions include:
1. A controlled reproduction of an existing compressed-weight inference method on an RTX 4060-class GPU, if its code and toolchain are feasible.
2. A fixed-budget KV-cache quality/memory/latency study using the current llama.cpp stack.
3. A focused study of where offloading or compression stops helping due to data-transfer, decode-kernel, or memory-bandwidth overhead.
4. Checkpoint delta compression for related fine-tune/version sequences, if that storage lifecycle is within scope.

These are candidate directions, not novelty claims. The current baseline must be measured first, and each candidate requires a closer source audit and independent review.
