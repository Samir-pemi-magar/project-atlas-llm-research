# Literature Review and Prior Art

> Purpose: map the existing landscape before making novelty claims. Add
> sources as they are verified.

## Search protocol

For each research question:

1.  Search papers, technical reports, patents when relevant, and public
    implementations.
2.  Record search terms, date, and scope.
3.  Read the original paper or implementation documentation where
    possible.
4.  Identify the closest method, assumptions, hardware, and evaluation
    setup.
5.  Compare methods on the mechanism---not just on names or reported
    headline metrics.
6.  Update this file when new evidence changes the assessment.

## Topics to investigate

-   Weight-only and weight-activation quantization
-   Mixed-precision allocation and sensitivity estimation
-   Outlier handling and quantization-aware training
-   Low-rank methods and structured compression
-   Memory bandwidth and data movement
-   KV-cache compression, paging, and attention efficiency
-   Speculative decoding and early-exit methods
-   Sparse or conditional computation
-   CPU/GPU/NPU heterogeneous execution
-   Kernel fusion, packing, and hardware-aware layouts
-   On-device benchmarking, power, and thermal behavior

## Source ledger

Use one entry per important source. Distinguish source claims from our
own interpretation.

### Source template

-   **Citation:**
-   **URL / DOI:**
-   **Publication date / version:**
-   **Source type:** paper / technical report / documentation / code /
    patent
-   **Problem addressed:**
-   **Core mechanism:**
-   **Assumptions and hardware:**
-   **Evaluation and baselines:**
-   **Reported benefits:**
-   **Limitations / failure cases:**
-   **Code and license:**
-   **Relevance to ATLAS:**
-   **Closest overlap with our hypotheses:**
-   **Verification status:** not read / skimmed / read / independently
    checked

## Comparison table

  ------------------------------------------------------------------------
  Method /    Mechanism   Hardware /  Main metric Key          Relevance
  source                  workload                limitation   
  ----------- ----------- ----------- ----------- ------------ -----------
  TODO        TODO        TODO        TODO        TODO         TODO

  ------------------------------------------------------------------------

## Novelty assessment

Do not use "novel" as a synonym for "new to us." For each candidate
idea, document:

-   The closest known methods
-   What is genuinely different in mechanism or objective
-   Whether the difference has practical significance
-   Search terms and databases checked
-   Remaining uncertainty

## Search history

  Date         Search terms / venue   Scope   Useful findings
  ------------ ---------------------- ------- -----------------
  YYYY-MM-DD   TODO                   TODO    TODO
