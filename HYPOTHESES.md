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
- **Closest prior art:** Tan et al., “Approaching Shannon Bound with Lossless LLM Weight Compression” (arXiv:2606.15789); Xie et al., “Reimagining Memory Access for LLM Inference” (arXiv:2503.18869). These directly overlap with entropy-aware compression and bit-plane/data-layout transformations.
- **What may be new:** Unknown. The hypothesis is initially a reproducibility/feasibility question, not a novelty claim. Any contribution must be distinct from the cited systems and their code.
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
- **Next decision:** Complete prior-art and implementation review, then either refine a clearly distinct transformation or replace this hypothesis with a better-supported research question.

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
