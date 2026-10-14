# Experiments

Store experiment code, configuration files, scripts, and concise notes
here.

## Suggested layout

Create a separate directory for each experiment once its scope is
defined:

``` text
experiments/
  EXP-YYYYMMDD-001-baseline/
    README.md
    config.yaml
    run.sh
    results.csv
    logs/
```

Guidelines:

-   Keep commands and configs sufficient to reproduce the run.
-   Avoid committing credentials, private data, large model files, or
    generated artifacts that should live in external storage.
-   Link each experiment to a hypothesis ID in `HYPOTHESES.md` and
    record its result in `EXPERIMENT_LOG.md`.
-   Include dependency versions and hardware/software details.
