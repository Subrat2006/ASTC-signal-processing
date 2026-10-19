# Submission guide

How to turn a solved problem into a clean, reviewable contribution.

## 1. Folder

Work in `solutions/NN_name/` (already created, with a README template). Minimum content:

```
NN_main.ipynb        reproducible notebook (restart kernel, run all, save with outputs)
report.md / .pdf     the written analysis requested in the problem
memo.md              deliverable D6
figures/             every figure used in the report
```

## 2. What a good notebook looks like

1. First cell: title, unit system (Hz or rad/s; normalised or not), random seed (`from sp_common.rng import get_rng`), package versions.
2. A section **Model** (equations with units, parameters from the Data and Simulation Specification table, one cell each).
3. A section **Validation**: the analytic results and the self-check targets of the problem statement, each with a pass/fail
   `assert` and a plot.
4. A section per Task, in the order of the problem statement, each ending with one sentence of interpretation.
5. A section **Uncertainties** (number of realisations, bootstrap intervals, Wilson intervals on rates, convergence with record length).
6. No dead code, no unexplained constants: every number is either in the parameter table or has a comment with its source.

## 3. What a good report looks like (2–6 pages)

* **Summary** (5–10 lines): what you built, how you validated it, 2–3 key numbers with uncertainties.
* **Results by task**: figure, caption with units and parameters, 2–4 sentences of interpretation.
* **Aerospace application link**: the engineering conclusion, in numbers.
* **Limitations**: what the model does *not* include, and which result you trust least.
* **Sources and AI-tool usage.**

## 4. Git workflow

```bash
git checkout -b solution/NN-short-name
git add solutions/NN_name
git commit -m "NN: <what you validated>, <headline number>"
git push -u origin solution/NN-short-name
```

Open a pull request into `main` using the template. Your mentor reviews it, leaves comments in the PR, and writes the score
into `PROGRESS.md`. Address comments with further commits to the same branch.

Commit messages that help future-you: `"12: window table matches Harris to 0.02 bins"` is better than `"update"`.

## 5. Before you push

```bash
python tools/check_submission.py NN
python tools/update_progress.py
pytest -q                           # the shared helpers still pass
```

Keep the repository light: do not commit raw data (`data/raw/` and common data extensions are git-ignored); regenerate synthetic
data from its seed and describe how to download real data.

## 6. Review criteria

The same five criteria as in every problem statement: conceptual depth, implementation quality, aerospace-application
integration, analysis and critical thinking, communication (20 marks each). A short oral defence of any submitted number is part
of the review: "where does this number come from?"
