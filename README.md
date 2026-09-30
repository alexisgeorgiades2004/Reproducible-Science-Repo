# Reproducible scRNA-seq: Immunotherapy Tumor Response Analysis

Course project (UCLA, Fall 2026, Week 1: Reproducible Science). This repo redoes the
"scRNA-seq Immunotherapy Tumor Response Analysis" example inside Claude Science, with every
step written as a notebook chunk whose output can be checked by a human.

## Goal
Reproduce the class scRNA-seq analysis end to end (QC, normalization, clustering, cell-type
annotation, responder vs. non-responder comparison) in a versioned, re-runnable project.

## Repository map
| Path | Purpose |
|---|---|
| `README.md` | This file: overview, structure, how to reproduce |
| `CLAUDE.md` | Rules Claude Science must follow in this repo |
| `.claude/agents/` | Agent definition files (QC reviewer, methods writer) |
| `data/raw/` | Original data. Read-only, never edited, not committed if large |
| `data/metadata/` | Sample sheets, data source notes (`DATA_SOURCES.md`) |
| `data/processed/` | Intermediate objects (e.g., filtered/normalized), regenerable |
| `src/` | Reusable functions and scripts |
| `workflows/` | Analysis notebooks (`.qmd`, `.Rmd`, or `.ipynb`), numbered by stage |
| `configs/` | Parameters: thresholds, seed, paths (`params.yaml`) |
| `environment/` | Locked package versions (`renv.lock`, `environment.yml`, etc.) |
| `results/` | Tables and other computed outputs |
| `figures/` | Saved plots |
| `reports/` | Rendered HTML/PDF reports |
| `tests/` | Small checks and test data |

## Workflow order
1. `workflows/00_setup`: load packages, print versions, confirm environment
2. `workflows/01_load_and_inspect`: load data, report dimensions and metadata
3. `workflows/02_qc_filtering`: QC metrics, filtering, cells removed
4. `workflows/03_normalization_pca`: normalization, variable features, PCA
5. `workflows/04_clustering_umap`: clustering and UMAP
6. `workflows/05_annotation`: marker genes and cell-type labels
7. `workflows/06_response_comparison`: responders vs. non-responders
8. `reports/`: final rendered report

## How to reproduce
1. Clone the repo: `git clone <repo-url>`
2. Restore the environment from `environment/` (see the file present there).
3. Download the raw data as described in `data/metadata/DATA_SOURCES.md` into `data/raw/`.
4. Run the notebooks in `workflows/` in numeric order.

## Analysis log
Claude Science appends short summaries of each completed stage below.

<!-- ANALYSIS-LOG-START -->
_No stages completed yet._
<!-- ANALYSIS-LOG-END -->

## Software versions
See `environment/` and the session-info chunk at the end of every notebook.
