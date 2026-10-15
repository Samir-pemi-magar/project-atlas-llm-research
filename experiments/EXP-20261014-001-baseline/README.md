# EXP-20261014-001 — Qwen3-1.7B local inference baseline

**Status: Harness drafted; not yet executed. Diagnostic pilot succeeded. No formal benchmark measurements have been collected.**

## Research question

Establish a reproducible reference point for single-request local inference before evaluating any ATLAS optimization. This experiment measures the existing quantized model and runtime; it does not test or establish a compression contribution.

## Fixed candidate and environment

- Model repository: `ggml-org/Qwen3-1.7B-GGUF`
- Model variant: `Qwen3-1.7B-Q4_K_M.gguf`
- Snapshot revision: `daeb8e2d528a760970442092f6bf1e55c3b659eb`
- Model SHA-256: `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`
- llama.cpp image ID: `sha256:b0baccbe2e00b5d74e63f85f9f023c93d61d0f329475269e1e7002e87eb875ea`
- Context: 4096 tokens
- GPU offload request: `-ngl 99`; actual offload was verified in the isolated verbose diagnostic log (29/29 layers). Reconfirm runtime/model identity before the formal run.
- Hardware snapshot: NVIDIA GeForce RTX 4060, 8,188 MiB reported VRAM; 1,729 MiB occupied at one earlier idle snapshot. Recheck immediately before testing.
- Existing DocPilot services: must not be stopped, restarted, reconfigured, or benchmarked through.

The model path is a Hugging Face snapshot symlink resolving to the cache blob above. The cache is mounted read-only in the ATLAS container. The launch uses a local image ID and `--pull=never` to avoid an image pull; the intended model file is already cached. Do not run if Docker reports the local image is unavailable.



## Diagnostic outcome (2026-10-15)

The isolated diagnostic on port 3002 completed successfully. The verbose startup log confirmed 29/29 model layers offloaded to GPU, with a 1050.43 MiB CUDA model buffer and 448.00 MiB CUDA KV buffer. The server reported llama.cpp `0.6.0-dev (build 11610, commit 091b6a7fc)`.

A raw `/completion` smoke request returned repetitive text. A `/v1/chat/completions` request initially used all 128 tokens for reasoning and returned empty assistant content. Adding `chat_template_kwargs: {"enable_thinking": false}` produced a coherent two-sentence answer. The response showed default `top_k=40` and `min_p=0.05` when those settings were not explicitly requested. These are diagnostic observations only, not benchmark results.

The harness draft now uses the chat endpoint with thinking disabled, explicitly requests `temperature=0`, `top_k=1`, `top_p=1`, `min_p=0`, `seed=42`, `max_tokens=96`, and `cache_prompt=false`. It validates the server-reported effective settings and cache behavior before starting measured requests. See [HARNESS.md](HARNESS.md), [prompts_v1.json](prompts_v1.json), and [run_benchmark.py](run_benchmark.py).

## Isolated pilot launch (historical launch procedure)

Run in the Ubuntu WSL terminal, not in the DocPilot container. This starts a separate disposable container named `atlas-qwen3-pilot` on host port 3001; it does not modify DocPilot or PostgreSQL. Stop the pilot with Ctrl+C in its terminal; `--rm` removes the container after it stops.

```bash
docker run --pull=never --rm --name atlas-qwen3-pilot \
  --gpus all \
  -p 3001:8080 \
  -v /home/acer/projects/docpilot/data/models/llama.cpp:/root/.cache:ro \
  sha256:b0baccbe2e00b5d74e63f85f9f023c93d61d0f329475269e1e7002e87eb875ea \
  -m /root/.cache/huggingface/hub/models--ggml-org--Qwen3-1.7B-GGUF/snapshots/daeb8e2d528a760970442092f6bf1e55c3b659eb/Qwen3-1.7B-Q4_K_M.gguf \
  --host 0.0.0.0 --port 8080 --alias atlas-qwen3-1.7b -c 4096 -ngl 99
```

If startup fails because the cache path is not accessible from the Ubuntu Docker context, stop and report the exact error; do not pull or download another model as a workaround.

## Pilot checks

From a second terminal, verify readiness:

```bash
curl -fsS --max-time 10 http://localhost:3001/health
```

Check startup output for CUDA initialization and GPU-layer offload messages. If GPU offload is not explicit, record it as unverified rather than assuming it happened.

Make one deterministic smoke-test request (this is a pilot, not a performance result):

```bash
curl -fsS --max-time 120 http://localhost:3001/completion \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain why controlled experiments need a baseline in two concise sentences.",
    "n_predict": 64,
    "temperature": 0,
    "top_k": 1,
    "top_p": 1,
    "min_p": 0,
    "seed": 42,
    "cache_prompt": false,
    "stream": false
  }'
```

Save the full JSON response and startup log outside the repository initially. Confirm that response timing fields are present before implementing the measurement harness. The server's timing fields and exact API behavior are version-dependent and must be inspected, not assumed.

## Full baseline protocol (only after the pilot succeeds)

- Use a fixed, versioned set of 20 prompts with no private data.
- Fix context (4096), prompt text, generation cap (96), seed (42), sampling settings (temperature 0, top-k 1, top-p 1, min-p 0), thinking mode (disabled), and cache policy (`cache_prompt=false`) across all runs; verify effective settings from server responses.
- Run 3 warm-up generations, then 3 measured repetitions per prompt (60 measured requests); randomize or interleave method order in later comparisons to reduce time/order bias.
- Capture prompt processing rate, decode throughput, prompt/output token counts, client wall-clock latency, errors, finish reason, effective generation settings, and output text. TTFT is unavailable in the current non-streaming harness and must not be reported as measured.
- Capture sampled GPU memory/utilization/temperature/power and WSL VM RAM via the harness. The 0.5-second poll can miss short peaks; WSL RAM is not Windows process-level RAM.
- Report median and spread (at least IQR) rather than only the best run. Record temperature, power mode, background GPU usage, runtime/image ID, exact model checksum, command, and logs.
- Keep baseline generation deterministic where supported. Validate whether `temperature: 0` plus `top_k: 1` behaves greedily in this llama.cpp build.
- Evaluate output quality separately from speed. Exact token-for-token repeatability is a runtime check, not proof of general model quality.

## Interpretation and stop conditions

This baseline measures this model/runtime/hardware combination only. It does not establish that Q4_K_M is equivalent to full precision, nor that any ATLAS method is novel.

Stop and investigate if the model checksum differs, the read-only mount fails, the runtime tries to download a model, the isolated server binds the wrong port, GPU use is unclear, or DocPilot is affected. Do not proceed to a long run until the pilot and logging path are verified.
