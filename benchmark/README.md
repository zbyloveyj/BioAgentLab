# Evaluation scope

The current regression suite is under `tests/` and covers contracts, known numerical examples, input rejection, citation IDs, synthetic evidence exclusion, context, study duplication, hypothesis revision, budget, paths, DAGs, model JSON, network response fixtures and an offline end-to-end run.

Run `python -m pytest -q`. Release counts are generated from JUnit results rather than hard-coded. See `docs/verification.json` for actual results.

This is not a benchmark of real biological discovery or clinical performance. Such evaluation requires independently curated tasks, appropriate baselines, expert assessment, cost controls and external validation, as discussed in chapters 18 and 31.
