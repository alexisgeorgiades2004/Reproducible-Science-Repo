# Reproducible scRNA-seq: Immunotherapy Tumor Response Analysis

Course project (UCLA, Fall 2026, Week 1: Reproducible Science). This repo redoes the
"scRNA-seq Immunotherapy Tumor Response Analysis" example inside Claude Science, with every
step written as a notebook chunk whose output can be checked by a human.

## Goal
Reproduce the class scRNA-seq analysis end to end (QC, normalization, clustering, cell-type
annotation, responder vs. non-responder comparison) in a versioned, re-runnable project.

## How to read this project
This repo is written so that a reader can follow the analysis **without running it**. For every
numbered step in the Analysis log at the bottom of this file there is:

- **what was done** — the operation, in plain language;
- **the decision and why** — where a choice existed, which option was taken and on what grounds;
- **the output** — what was produced, and the numbers that characterise it;
- **what it means** — the interpretation, and where relevant what it does *not* show.

Each step stops for approval before the next begins, so the log is a record of decisions that
were agreed at the time, not a reconstruction written afterwards. Figures are explained in plain
language when they are shown, not merely captioned.

Intermediate outputs (matrices, QC tables, figures) are kept outside the repo unless there is a
reason to commit them; the repo holds the code, the parameters, and this record.

## Method: the 13-step scRNA-seq pipeline

The analysis *method* for this project is deliberately not defined in this file. It
lives in the `scrnaseq-pipeline` skill, vendored at `skills/scrnaseq-pipeline/`,
which defines the canonical 13-step sequence and what each step establishes, the
per-step approval gates and reporting conventions, the verification check at each step
boundary, and the dataset traps that cost real debugging time — GEO matrices with two
header rows and a trailing tab, matrices already log-transformed despite a `TPM`
filename, mitochondrial QC on the wrong MT gene set, dispersion binning that silently
selects noise, and receptor V(D)J genes that cluster T cells by clonotype rather than
cell state.

The split is the point. **This README and `CLAUDE.md` cover reproducible science in
general** — how work is recorded, verified, gated and reported here, whatever the
domain. **The method is domain-specific and belongs in a skill**, so a different assay
gets a different skill without rewriting the project's rules, and the scRNA-seq method
can be reused on a different dataset without dragging this project's history along.

Claude Science loads the skill on its own when the work is single-cell; to load it by
hand, `skill({skill: "scrnaseq-pipeline"})`. Step numbers in the Analysis log below
refer to that sequence, grouped into notebooks as follows.

| Steps | Notebook |
|---|---|
| 1–3 — acquisition, load/inspect, cohort | `workflows/01_acquire_inspect` |
| 4–6 — QC metrics, working matrix, filtering | `workflows/02_qc` |
| 7–9 — normalization, feature selection, PCA | `workflows/03_features_pca` |
| 10–11 — clustering, embedding | `workflows/04_cluster_embed` |
| 12 — cell-type annotation | `workflows/05_annotate` |
| 13 — comparative analysis | `workflows/06_compare` |

A step may legitimately be a no-op (step 7 was) or deferred (step 11 was, for want of
an embedding library) — the log says which and why.

## Repository map
| Path | Purpose |
|---|---|
| `README.md` | This file: overview, the 13-step sequence, how to reproduce, analysis log |
| `CLAUDE.md` | Rules Claude Science must follow in this repo |
| `skills/` | Domain method skills; vendored copy of `scrnaseq-pipeline` |
| `.claude/agents/` | Agent definition files (QC reviewer, methods writer) |
| `data/raw/` | Original data. Read-only, never edited, not committed if large |
| `data/metadata/` | Sample sheets, data source notes (`DATA_SOURCES.md`) |
| `data/processed/` | Intermediate objects (e.g., filtered/normalized), regenerable |
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
2. Restore the environment from `environment/` (see `configs/environments.yml` for which
   environment serves which step).
3. Download the raw data as described in `data/metadata/DATA_SOURCES.md` into `data/raw/`.
4. Run the notebooks in `workflows/` in numeric order.

## Analysis Log
At the end of every session, before finishing, write an analysis log entry in the
`Analysis Logs/` folder at the root of the repo (C:\Users\Alexi\repos\Reproducible-Science-Repo).
If the folder doesn't exist, create it.

Create one new Markdown file per session, named with the date and a short topic, for
example `2026-09-30_data-download.md`. Never overwrite or edit earlier log files.

Each entry must include:
1. Session goal: what I asked for, in one or two sentences.
2. What was done: a numbered list of the steps you actually ran, in order, with the
   files you created, changed, or downloaded (full repo-relative paths).
3. Why: the reason for each major decision, including parameters, thresholds, tools,
   and alternatives you considered and rejected.
4. Key outputs: the main results I can verify (cell and gene counts, files saved, figures
   produced), with the paths where they were saved.
5. Problems and deviations: errors, warnings, anything unexpected, workarounds, and
   anything you were unsure about. Do not omit failures.
6. Reproducibility info: random seed, package and software versions, dataset source
   and accession, and the parameters used (from configs/params.yaml).
7. Next steps: what remains to be done.

Only report what actually happened in the session. Do not invent results or claim
steps were completed if they were not. Do not commit or push the log file; leave
it for me to review and commit.

## Software versions
See `environment/` and the session-info chunk at the end of every notebook.
