# CLAUDE.md: Project rules for Claude Science

This repo is a reproducible scRNA-seq analysis (Immunotherapy Tumor Response). Read this file and
`README.md` at the start of every session. Follow these rules.

## Notebook-style working
- Work in notebooks in `workflows/` (Quarto `.qmd`, R Markdown `.Rmd`, or Jupyter `.ipynb`).
- One small step per chunk. Before each chunk, write 1-2 sentences saying what it does and why.
- Every chunk must produce a visible output I can verify: a table, printed dimensions, or a plot.
- After each chunk or stage, state briefly what the output shows and flag anything unexpected.
- Do not skip ahead. Finish and show one stage before starting the next.
- Notebooks must run top to bottom on a clean session.

## Reproducibility
- Set one global random seed (from `configs/params.yaml`) at the top of every notebook.
- Put all thresholds and parameters in `configs/params.yaml`, not hard-coded in chunks.
- End every notebook with a session-info chunk (`sessionInfo()` or package versions).
- Use relative paths from the repo root. No absolute paths like `C:\Users\...`.
- Record every package install in `environment/` (renv snapshot or environment.yml).

## Data rules
- Never modify or overwrite anything in `data/raw/`.
- Write intermediates to `data/processed/`, tables to `results/`, plots to `figures/`.
- Document the source of every dataset in `data/metadata/DATA_SOURCES.md`.
- Do not commit large data files (see `.gitignore`).

## Git rules
- Do not commit or push unless I ask. When asked, use a clear message describing the stage
  (for example `Add QC step, filter mito >10%`).
- Never commit secrets, tokens, or `.env` files.
- Never rewrite history (no force-push) without asking.

## Reporting
- After completing a stage, add a 2-3 line summary to the Analysis log section in `README.md`
  (between the `ANALYSIS-LOG` markers).
- Be explicit about uncertainty. If a result looks off (odd cell counts, batch effects), say so
  rather than smoothing over it.

## Agents
Agent definitions live in `.claude/agents/`:
- `qc-reviewer`: checks QC thresholds and outputs before moving on.
- `methods-writer`: drafts methods and results text from the notebooks.
