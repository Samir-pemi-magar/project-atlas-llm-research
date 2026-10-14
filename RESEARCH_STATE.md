# Research State

> Update this file whenever a decision, target, blocker, or next action
> changes. This file is the concise source of truth for the project.

## Status

-   **Phase:** Setup / baseline planning
-   **Last updated:** YYYY-MM-DD
-   **Owner:** TODO
-   **Repository:** `project-atlas-llm-research`

## Research objective

Find and validate methods for improving the practical efficiency of LLM
inference on constrained hardware while measuring the trade-offs in
output quality, latency, memory, energy, and implementation complexity.

## Target environment

-   **Device / SoC:** TODO
-   **CPU / GPU / NPU:** TODO
-   **RAM / VRAM:** TODO
-   **Operating system:** TODO
-   **Runtime / inference engine:** TODO
-   **Power or thermal constraints:** TODO
-   **Primary workload:** TODO (e.g., interactive chat, summarization,
    offline batch)
-   **Connectivity constraints:** TODO (offline / intermittent / online)

## Baseline model

-   **Model name and source:** TODO
-   **Exact revision / commit:** TODO
-   **Tokenizer revision:** TODO
-   **License:** TODO
-   **Parameter count:** TODO
-   **Weight format / quantization:** TODO
-   **Context length tested:** TODO
-   **Evaluation dataset / tasks:** TODO

## Success criteria

Set measurable targets before optimizing.

  Metric                           Baseline   Target Measurement method
  ------------------------------ ---------- -------- --------------------
  Output quality                       TODO     TODO TODO
  Time to first token                  TODO     TODO TODO
  Decode throughput (tokens/s)         TODO     TODO TODO
  Peak memory                          TODO     TODO TODO
  Model storage                        TODO     TODO TODO
  Energy per token                     TODO     TODO TODO
  Implementation complexity            TODO     TODO 

## Current decisions

-   No method is considered novel without a documented prior-art search.
-   Establish a baseline before tuning.
-   Keep model weights and credentials out of this repository.
-   Record exact versions and configuration for each experiment.
-   Report failed and inconclusive runs, not just successful ones.

## Current bottleneck

**Unknown --- profile the baseline first.**

Potential bottlenecks to distinguish include memory capacity, memory
bandwidth, compute throughput, kernel launch overhead, prompt prefill,
decode, KV-cache growth, thermal throttling, and energy limits.

## Open questions

1.  Which device and memory budget are the primary target?
2.  Which model and workload are representative?
3.  Is the baseline primarily memory-, bandwidth-, compute-, or
    runtime-bound?
4.  What quality regression, if any, is acceptable for a meaningful
    efficiency gain?

## Next actions

-   [ ] Specify target device, RAM, workload, and primary goal.
-   [ ] Select a model that can run on the target device.
-   [ ] Record model and software revisions.
-   [ ] Run baseline measurements with repeated trials.
-   [ ] Add baseline results to `EXPERIMENT_LOG.md`.
-   [ ] Review the closest prior art before choosing an optimization.

## Decision log

  -----------------------------------------------------------------------
  Date              Decision          Reason            Evidence /
                                                        experiment
  ----------------- ----------------- ----------------- -----------------
  YYYY-MM-DD        Start with        Avoid optimizing  Pending
                    baseline          the wrong         
                    profiling         bottleneck        

  -----------------------------------------------------------------------
