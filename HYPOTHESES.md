# Research Hypotheses

> Hypotheses are testable claims, not results. Status remains proposed until an experiment is run and logged.

## Status definitions
- **Proposed:** not yet reviewed sufficiently
- **Prior-art review:** checking related work
- **Ready to test:** protocol and failure criteria are defined
- **Running:** experiment in progress
- **Supported / Rejected / Inconclusive:** assigned only after reviewing measured results
- **Superseded:** replaced by a better-defined hypothesis

## H-001 — Software-only reversible transforms and lossless model-file compression
- **Status:** Prior-art review
- **Claim:** For at least one selected open-weight model and stored numeric format, a reversible tensor-aware transformation followed by a general-purpose compressor may reduce total model-file size beyond direct compression of the original tensor bytes, while exactly reconstructing every tested tensor value.
- **Mechanism:** A reversible change in data layout may expose statistical redundancy that byte-level compression does not exploit in the original layout.
- **Closest prior art:** Tan et al., “Approaching Shannon Bound with Lossless LLM Weight Compression” (arXiv:2606.15789); Xie et al. (arXiv:2503.18869); ZipServ (https://github.com/QuiverDance/ZipServ_ASPLOS26); Neural Weight Compression (https://github.com/parda21/NWC); Split12 (https://github.com/brianbell-x/weight-compression); plus ZipNN (https://github.com/zipnn/zipnn) and z4ai (https://github.com/z4ai/z4ai) for tensor/checkpoint codecs. These overlap with entropy coding, byte/bit-plane layouts, and/or decompression integrated into GPU computation. See `research/PRIOR_ART_SCAN_2026-10-15.md`.
- **What may be new:** Unknown. The broad mechanism is crowded. Keep this as a replication/control question only; do not pursue it as a novelty claim unless full-paper and source-code comparison identifies a concrete, meaningful gap.
- **Assumptions:** The exact model weights can be legally downloaded and locally processed; the tensor format and metadata can be handled without altering tensor values.
- **Predictions:** (1) Lossless round-trip checksums/bytes match exactly. (2) Any file-size gain remains after metadata and container overhead. (3) The transformation and decompression costs can be measured separately.
- **Primary metric:** Total compressed bytes divided by original bytes, including metadata.
- **Guardrail metrics:** Exact reconstruction; compression time; decompression time; peak RAM; load time; implementation complexity.
- **Baseline:** Original model file size and direct Zstandard compression of identical tensor bytes, with version and compression level recorded.
- **Experiment:** First choose one small model and one tensor/file format. Compare uncompressed, direct Zstandard, and one reversible transform plus Zstandard on a representative subset before processing the full model. Validate exact byte-for-byte reconstruction.
- **Failure criterion:** Reject this specific transform candidate if it does not improve compressed size beyond baseline after overhead, if any tensor value fails exact reconstruction, or if resource use makes the test impractical.
- **Confounders:** File container overhead; tensor ordering; alignment; compression level; different file formats; duplicate/shared tensors; file metadata; decompression implementation.
- **Required resources:** Windows PC with RTX 4060, CPU/RAM/storage; exact model files; compressor library; small reproducible script.
- **Results / experiment IDs:** None yet.
- **Next decision:** Inspect NWC and ZipServ implementation requirements and evaluate whether a controlled RTX 4060 replication is feasible. Then either define a narrow research gap supported by the comparison or mark H-001 superseded in favor of a better-supported hypothesis.

## Candidate directions (not validated claims)
1. Sensitivity-aware mixed precision under a fixed memory budget.
2. Weight packing/layout choices that reduce actual memory traffic on a target backend.
3. Adaptive allocation of computation based on measured token or layer difficulty.
4. KV-cache policies matched to context length and device memory.
5. Combining compression and runtime scheduling without hidden quality regressions.

## Active hypothesis summary

| ID | Short title | Status | Primary metric | Next action |
|---|---|---|---|---|
| H-001 | Software-only reversible transforms and lossless model-file compression | Prior-art review | Compressed size including overhead | Inspect closest papers and implementations; choose a small test format |

No hypotheses have been validated, and no experiments have been run in this repository yet.
