# CLAUDE.md

Rules for AI agents working in this repository. Read this file and `README.md` at the start of every session and follow them for all work in this project. If a rule conflicts with a request, say so and ask before proceeding.

## Project layout

- `data/raw/` original data, read-only
- `data/metadata/` data sources, dates, licenses, dictionaries
- `data/processed/` generated data
- `src/` reusable code
- `workflows/` ordered pipelines from raw data to figures
- `configs/` parameters, seeds, thresholds, paths
- `results/` tables and statistics
- `figures/` plots
- `reports/` written summaries
- `tests/` checks
- `environment/` package and version records

## Data

- Never modify, rename, move or delete anything in `data/raw/`.
- When new raw data is added, document it in `data/metadata/` (source, date obtained, license, description).
- Write all derived data to `data/processed/`. It must be regenerable from code.

## Code and parameters

- Put all analysis code in `src/` or `workflows/`. Do not do analysis in one-off cells that are not saved to the repository.
- Keep workflows as ordered, named steps. Running them in order must reproduce every output.
- Put every parameter (thresholds, cutoffs, file paths, seeds) in `configs/`. Do not hard-code them.
- Do not change a parameter between runs without recording the change and the reason.
- Use a seed from `configs/` for every stochastic step and record it with the output.

## Environment

- Prefer several small environments matched to analysis steps over one large environment.
- After each run, record the exact package and language versions in `environment/`.

## Outputs

- Save outputs in a subfolder named for the analysis or run, for example `results/scrna-immunotherapy/`.
- Never overwrite earlier results. Use a new run folder or a new commit.
- Verify outputs before reporting them: check shapes, counts, missing values and that figures match the tables.
- Add or run checks in `tests/` when code or data changes.

## Honesty and evidence

- Do not invent data, values, citations or results. If something cannot be determined, say so.
- Record every decision you make (filters, thresholds, methods, exclusions) and the reason, in the report or a decisions section.
- Keep measured results separate from interpretation. Label interpretation clearly as interpretation.
- State uncertainty and limitations.

## Safety

- Work only inside the granted repository folder.
- Do not delete files outside `results/`, `figures/` and `data/processed/`, and never run destructive commands without explicit approval.
- Do not access other machines or networks unless asked.

## Git

- Propose a commit message after each meaningful step and wait for confirmation before committing.
- Do not push, force-push, rebase or rewrite history unless asked.
- Record the starting commit hash in every report.

## End of every task

Finish with a short summary that lists:

1. Which rules from this file you applied.
2. The seeds used.
3. The environment and package versions.
4. The files created or changed.
5. The Git commit the work started from.
