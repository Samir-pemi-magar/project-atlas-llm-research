# Independent Harness and Prior-Art Review — 2026-10-15

**Reviewer verdict:** READY AFTER FIXES  
**Reviewed branch/head reported by reviewer:** `research/baseline-harness-and-prior-art`, `bef9633`  
**Evidence boundary:** Reviewer reports reading the seven files on that branch, running `py_compile` and helper tests on the reviewed version, and auditing upstream source at `ggml-org/llama.cpp` commit `091b6a7fc`. They did not run the benchmark, contact the server, install software, or modify the repository. The build-11610 to commit mapping remains unverified.

This record summarizes the independent review. It is not a claim that the current edited draft has passed syntax checks; it has not yet been locally revalidated after remediation edits.

## Blocking findings

1. **Alias mismatch:** the original harness expected `atlas-qwen3-verbose-test`, while the documented pilot launch used `atlas-qwen3-1.7b`. A response model label is server-configured and does not establish model identity.
2. **Runtime provenance not verified:** expected model SHA-256, image ID, and server version were metadata labels rather than checks against `/props`, `/v1/models`, the host file, and Docker runtime configuration.
3. **Effective settings rely on verbose response metadata:** the exact request/launch mechanism to expose `__verbose` must be verified against the running build; server launch arguments were not documented consistently.
4. **Output truncation risk:** the 96-token cap could truncate longer answers, and excluding `finish_reason=length` samples would bias results. Truncation must be treated as a run failure, not a dropped observation.
5. **Cache and slot controls incomplete:** request `cache_prompt=false` does not by itself disable host-RAM slot save/load. The review recommends pinning `-np 1 --cache-ram 0 --no-cache-prompt` and verifying cache behavior.
6. **Measured request stop conditions:** configuration, cache, empty-output, truncation, and request errors must be enforced for every measured request.
7. **Telemetry is host-wide:** GPU counters include other GPU users; WSL memory is not process/container residency; missing numeric values must be null rather than sentinel `-1`. Laptop power/clock/throttle state and background GPU load remain confounders.
8. **Statistics and ordering:** with only three repeats, use per-prompt min/median/max as the primary descriptive view; pooled spread mixes prompt and repeat effects. Fixed rotations do not eliminate time/thermal drift.
9. **Provenance gaps:** preserve full response JSON and reasoning content, launch args/logs, per-request start timestamps, prompt hash, harness revision/dirty state, and runtime identity evidence.
10. **Scope:** the prompt workload is not a quality benchmark or fixed-length prefill/decode characterization. TTFT is not measured by a non-streaming client.

## Prior-art follow-ups

- Add DFloat11 (`https://arxiv.org/abs/2504.11651`, `https://github.com/LeanModels/DFloat11`) as a direct lossless-weight baseline.
- Verify NeuZip (`https://arxiv.org/abs/2410.20650`) directly; prior review only identified it through references.
- Add the TurboQuant primary paper (`https://arxiv.org/abs/2504.19874`) to the KV-cache review, not only integration forks.
- Record native llama.cpp KV-cache types and native offload flags at the pinned commit.
- Resolve the ZipServ paper/repository discrepancy: paper link reportedly points to `HPMLL/ZipServ_ASPLOS26`, while the first-pass scan cited `QuiverDance/ZipServ_ASPLOS26`. Relationship is unresolved.
- H-001 remains a replication/control question. The review found no basis for a generic lossless weight-compression novelty claim.

## Remediation status

- [x] Correct the harness's expected alias to the documented pilot alias; the port-3002 running diagnostic's actual alias must still be checked before live use.
- [x] Increase the output cap from 96 to 256 while retaining truncation as an error.
- [x] Record the review and its prior-art follow-ups.
- [ ] Complete runtime identity, image, model-hash, and launch-argument verification.
- [ ] Pin slot count and host-RAM cache behavior in a documented isolated-server launch.
- [ ] Verify verbose response metadata and all effective generation settings on the exact running image.
- [ ] Finish request-level failure enforcement, telemetry null handling, and raw provenance capture.
- [ ] Run local syntax and plan-only checks after edits. These checks must not contact the server.
- [ ] Obtain explicit authorization before live validation or formal benchmarking.

No formal benchmark results are present in this review or established by these actions.
