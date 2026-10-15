# Baseline Harness — EXP-20261014-001

**Status: Draft harness. Not yet executed. No formal benchmark measurements have been collected.**

## Purpose

Collect reproducible single-request inference timing and resource telemetry for the cached Qwen3-1.7B Q4_K_M model on the isolated llama.cpp server. This is a runtime baseline only; it does not test a new compression method.

## Current diagnostic evidence

The user ran an isolated server on host port 3002 using local image ID:

`sha256:b0baccbe2e00b5d74e63f85f9f023c93d61d0f329475269e1e7002e87eb875ea`

The verbose startup log explicitly reported:
- `offloaded 29/29 layers to GPU`
- CUDA model buffer: 1050.43 MiB
- CUDA KV buffer: 448.00 MiB
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU, 8187 MiB reported

The server identified itself as llama.cpp `0.6.0-dev (build 11610, commit 091b6a7fc)`. A chat-completion request with `chat_template_kwargs.enable_thinking=false` returned a coherent answer. These are diagnostic checks, not formal benchmark measurements.

The `/completion` endpoint produced poor raw-completion text in a smoke request. The harness therefore uses `/v1/chat/completions` with thinking disabled and records the exact returned settings and text.

## Files

- `prompts_v1.json`: 20 fixed, public-safe single-turn prompts.
- `run_benchmark.py`: Python standard-library-only harness.
- `results/raw/<run-id>/requests.jsonl`: raw request/response records.
- `results/raw/<run-id>/telemetry.jsonl`: sampled GPU and WSL RAM telemetry.
- `results/raw/<run-id>/summary.json`: descriptive statistics and run status.
- `results/raw/<run-id>/measured_requests.csv`: flattened per-request summary.

Raw output text is preserved for later manual quality review; the script does not claim that coherent or repeatable outputs are correct.

## Locked candidate configuration

- Endpoint: `/v1/chat/completions`
- Chat template: `chat_template_kwargs: {"enable_thinking": false}`
- Temperature: 0
- Top-k: 1
- Top-p: 1
- Min-p: 0
- Seed: 42
- Maximum output tokens: 96
- Prompt cache: explicitly request `cache_prompt: false`
- Context: 4096
- Model revision: `daeb8e2d528a760970442092f6bf1e55c3b659eb`
- Model SHA-256: `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`

The script validates the effective sampling settings returned by this verbose server. It refuses to begin measured requests unless those settings match, warm-up outputs are nonempty and untruncated, and the server reports `cache_n=0` for all three warm-ups. If the build ignores a setting or the cache policy cannot be verified, the run aborts before formal measurements. The exact behavior must be verified against the running build; request parameters alone are not proof that a setting took effect.

## Workload and measurement plan

1. Check server health.
2. Run three global warm-up requests using P01, P10, and P20.
3. Validate effective sampling settings, output validity, and disabled prompt caching.
4. Run 3 measured passes over all 20 prompts (60 measured requests). Each pass uses a deterministic rotation of the prompt order.
5. Record client wall-clock latency, server prompt/decode timings, token counts, finish reason, output text, errors, and effective generation settings.
6. Poll GPU memory/utilization/temperature/power and WSL VM RAM every 0.5 seconds while the run is active.
7. Report median, Q1, Q3, and IQR. Retain every raw record.

TTFT is not measured by this non-streaming harness. The 0.5-second telemetry poll can miss short-lived peaks, and WSL `/proc/meminfo` measures WSL VM RAM rather than Windows process-level RAM. Energy per token is not claimed from sampled power alone.

## Validation before a formal run

In WSL, from the repository root:

```bash
python3 experiments/EXP-20261014-001-baseline/run_benchmark.py --plan-only
```

This checks the fixed prompt count and prints the planned workload without contacting the server or generating tokens. Inspect the script and prompt set; run a syntax check and review with Claude before any live validation.

A live harness validation or formal run must be separately authorized. Do not start the 63-request workload until the methodology review is complete and the user approves it.

## Interpretation and stop conditions

- This is a single-model, single-runtime, single-GPU reference.
- A successful run is not evidence of general model quality or novelty.
- Stop if health checks fail, effective sampling settings differ, prompt caching is nonzero or unknown, outputs are empty/truncated, model identity differs, or the isolated container is unavailable.
- Do not stop, restart, or reconfigure DocPilot services on ports 3000 and 5433.
