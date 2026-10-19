# Solutions

One sub-folder per problem, already created for you, each with a README template that lists the tasks and deliverables
of that problem. Work inside the folder of the problem you are solving.

```
solutions/NN_problem_name/
├── README.md              # template: status checklist, key results, sources and AI-tool usage
├── NN_main.ipynb          # main notebook (you create it)
├── report.md | report.pdf # written report (you create it)
├── memo.md                # memo deliverable (D6)
├── figures/               # all figures used in the report
└── src/                   # optional: modules you reuse across notebooks
```

## Rules of the house

1. **Fixed seeds, stated units.** The first cell of every notebook states the unit system (Hz or rad/s, normalised or not) and sets the random seed.
2. **Validate before you trust.** Every notebook has a section "Validation" that reproduces an analytic result or a self-check target.
3. **No cherry-picking.** Show error bars, false-alarm rates and failure cases, not only the best run.
4. **Clear outputs.** Before committing, run *Restart kernel and run all* so the notebook reproduces its own figures.
   Keep notebooks under about 5 MB (clear huge outputs).
5. **No big data in git.** Raw datasets go in `data/raw/` (git-ignored); describe how to download them.
6. **Cite everything,** including AI tools and code snippets, in the README of the problem. You must be able to explain
   every line you submit.

## Helper commands

```bash
python tools/check_submission.py 07     # does solutions/07_* contain notebook, report, memo, figures?
python tools/update_progress.py         # refresh PROGRESS.md from what is in solutions/
```
