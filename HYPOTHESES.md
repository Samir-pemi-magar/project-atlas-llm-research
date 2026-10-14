# Research Hypotheses

> A hypothesis is a testable claim, not a result. Give each hypothesis a
> stable ID and define a failure condition before running the
> experiment.

## Status definitions

-   **Proposed:** not yet reviewed
-   **Prior-art review:** checking related work
-   **Ready to test:** protocol and failure criteria are defined
-   **Running:** experiment in progress
-   **Supported:** evidence supports the stated claim under tested
    conditions
-   **Rejected:** evidence contradicts the claim
-   **Inconclusive:** test could not distinguish outcomes
-   **Superseded:** replaced by a better-defined hypothesis

## Hypothesis template

### H-000 --- Short title

-   **Status:** Proposed
-   **Claim:** Under \[conditions\], method X will change \[metric\] by
    \[threshold\] relative to \[baseline\], while keeping
    \[constraint\].
-   **Mechanism:** Why the effect is expected.
-   **Closest prior art:** TODO
-   **What may be new:** TODO --- do not assume novelty.
-   **Assumptions:** TODO
-   **Predictions:** What should be observed if the mechanism is
    correct.
-   **Primary metric:** TODO
-   **Guardrail metrics:** Quality, latency, memory, energy, and/or
    complexity as appropriate.
-   **Baseline:** TODO
-   **Experiment:** Smallest experiment that can distinguish the claim
    from the baseline.
-   **Failure criterion:** A specific result that would reject the
    hypothesis.
-   **Confounders:** TODO
-   **Required resources:** Hardware, model, dataset, runtime.
-   **Results / experiment IDs:** TODO
-   **Next decision:** TODO

## Candidate directions (not validated claims)

These are broad areas to investigate, not claims of novelty:

1.  Sensitivity-aware mixed precision under a fixed memory budget.
2.  Weight packing/layout choices that reduce actual memory traffic on a
    target backend.
3.  Adaptive allocation of computation based on measured token or layer
    difficulty.
4.  KV-cache policies matched to context length and device memory.
5.  Combining compression and runtime scheduling without hidden quality
    regressions.

## Active hypotheses

No hypothesis has been validated yet. Promote a candidate only after
defining its baseline, measurable prediction, and failure criterion.

  --------------------------------------------------------------------------
  ID             Short title    Status         Primary metric Next action
  -------------- -------------- -------------- -------------- --------------
  ---            No active      ---            ---            Define target
                 hypotheses yet                               device and
                                                              baseline

  --------------------------------------------------------------------------
