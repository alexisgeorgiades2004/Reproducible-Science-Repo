# Reproducible Science Repo

Course project (UCLA, Fall 2026, Week 1: Reproducible Science). A working repository
for running an analysis inside Claude Science so that every step is recorded,
verifiable and re-runnable — and so a reader can follow what was done **without
running it**.

This file and `CLAUDE.md` describe how work is conducted here: how it is recorded,
verified, gated and reported. They say nothing about any particular assay or
analysis method. That is deliberate — see *The method lives in a skill* below.

## How to read this project

For every numbered step of an analysis there is:

- **what was done** — the operation, in plain language;
- **the decision and why** — where a choice existed, which option was taken and on
  what grounds, including the alternatives rejected;
- **the output** — what was produced, and the numbers that characterise it;
- **what it means** — the interpretation, and where relevant what it does *not* show.

Each step stops for approval before the next begins, so the record is a log of
decisions that were agreed at the time, not a reconstruction written afterwards.
Figures are explained in plain language where they are shown, not merely captioned.

Verification is visible rather than asserted: a check appears as the code that ran
and the output it produced, alongside a statement of what would have counted as a
failure. Numbers are labelled as measured in the session or quoted from a source.

Intermediate outputs (large matrices, interim objects) are kept out of version
control unless there is a reason to commit them; the repo holds the code, the
parameters, the figures and tables, and the record.

## The method lives in a skill

The *analysis method* is not defined in this file. Domain methods live in skills,
vendored under `skills/` and loadable by name in Claude Science. A skill carries the
step sequence for its assay, what each step establishes, the checks at each step
boundary, and the traps that cost real debugging time on that kind of data.

The split is the point. **This README and `CLAUDE.md` cover reproducible science in
general**, whatever the domain. **The method is domain-specific and belongs in a
skill**, so a different assay gets a different skill without rewriting the project's
rules, and a method can be reused on a different dataset without dragging this
project's history along with it.

| Skill | Covers |
|---|---|
| `skills/scrnaseq-pipeline/` | Single-cell RNA-seq, as a gated 13-step pipeline: acquisition through QC, feature selection, clustering, annotation and condition comparison. Also defines the step-to-notebook grouping and the outputs each step leaves behind. |
| `skills/figure-standards/` | Making graphs. Sourced data-presentation rules, each traceable to a published guideline or journal standard rather than to taste, plus this repo's own figure conventions. Load it with the platform's `figure-style`, which supplies the rendering helpers. |

Claude Science loads a skill on its own when the work matches it; to load one by
hand, `skill({skill: "<name>"})`. Step numbers used in the analysis logs
refer to the sequence in the relevant skill.

## Repository map

| Path | Purpose |
|---|---|
| `README.md` | This file: how the project works, repo map, how to reproduce |
| `CLAUDE.md` | Rules Claude Science must follow in this repo |
| `Analysis Logs/` | One Markdown file per session: what was run, why, and what came out |
| `skills/` | Vendored domain-method skills |
| `.claude/agents/` | Agent definition files (none defined at present) |
| `data/raw/` | Original data. Read-only, never edited, not committed if large |
| `data/metadata/` | Sample sheets and data provenance (`DATA_SOURCES.md`) |
| `data/processed/` | Intermediate objects, regenerable, not committed |
| `src/` | Reusable functions and scripts |
| `workflows/` | Analysis notebooks (`.qmd`, `.Rmd`, or `.ipynb`), numbered by step range |
| `configs/` | Parameters: thresholds, seed, paths (`params.yaml`) |
| `environment/` | Locked package versions (`renv.lock`, `environment.yml`, etc.) |
| `results/` | Tables and other computed outputs |
| `figures/` | Saved plots |
| `reports/` | Rendered HTML/PDF reports |
| `tests/` | Small checks and test data |

## How to reproduce

1. Clone the repo: `git clone <repo-url>`
2. Restore the environment from `environment/` (see `configs/environments.yml` for
   which environment serves which step).
3. Download the raw data as described in `data/metadata/DATA_SOURCES.md` into
   `data/raw/`, and verify the checksums recorded there.
4. Load the domain skill named above for the analysis in question.
5. Run the notebooks in `workflows/` in numeric order.

## Analysis Log

At the end of every session, before finishing, write an analysis log entry in the
`Analysis Logs/` folder at the root of the repo. If the folder doesn't exist, create
it.

Create one new Markdown file per session, named with the date and a short topic, for
example `2026-09-30_data-download.md`. Never overwrite or edit earlier log files.

Each entry must include:
1. Session goal: what I asked for, in one or two sentences.
2. What was done: a numbered list of the steps you actually ran, in order, with the
   files you created, changed, or downloaded (full repo-relative paths).
3. Why: the reason for each major decision, including parameters, thresholds, tools,
   and alternatives you considered and rejected.
4. Key outputs: the main results I can verify, with the paths where they were saved.
5. Problems and deviations: errors, warnings, anything unexpected, workarounds, and
   anything you were unsure about. Do not omit failures.
6. Reproducibility info: random seed, package and software versions, dataset source
   and accession, and the parameters used (from `configs/params.yaml`).
7. Next steps: what remains to be done.

Only report what actually happened in the session. Do not invent results or claim
steps were completed if they were not. Do not commit or push the log file; leave it
for me to review and commit.

## Software versions

See `environment/` and the session-info chunk at the end of every notebook.
