# Analysis log: scRNA-seq v2, final summary figure (step 11 skipped), GSE120575

Date: 2026-09-30 (local clock). Continues `2026-09-30_scrnaseq-v2-step-13-comparison.md` (not edited). Not committed; left for review.

## 1. Session goal
Skip step 11 (embedding) as instructed and build one final multi-panel figure that carries the project's result: baseline immune composition separates responders from non-responders, with the limits of that result shown.

## 2. What was done
1. Recorded the decision: step 11 is **skipped by the user's instruction**, not deferred. No embedding library was installed and no 2-D cluster map exists in this project.
2. Loaded the `figure-composer` guidance. Wrote the claim and a six-panel outline (a hook, b claim, c-d evidence, e-f bounds).
3. Built the figure from saved repo tables only: `data/processed/cell_metadata_filtered.csv`, `data/processed/cell_annotations.csv`, `results/step13_composition_tests.csv`, `results/step13_tcf7_in_cd8_by_sample.csv`, `results/step12_removed_cells_projected_assignment.csv`. Recomputed the robustness p-values (panel f) from those tables with the same exact permutation test used in step 13.
4. Iterated three renders (layout defects listed in section 5), then checked geometry and viewed a crop of every row.
5. Wrote `figures/final_baseline_t_cell_states.png` (300 dpi, 2,346 x 2,488 px) and `figures/final_baseline_t_cell_states.pdf` (vector).

No file was added to `src/`, `workflows/` or `environment/`; no package installed; `configs/params.yaml` unchanged.

## 3. Why
- **Claim:** before treatment, responders carry more naive/central-memory T cells and fewer proliferating T cells; the result is bounded by therapy and technical confounds.
- **Panels:** a shows every tumour (the data); b the two significant types per tumour; c all 13 types with the multiple-testing result; d the independent `TCF7` check; e how therapy overlaps response; f how each p-value changes across robustness analyses. e and f are included because a figure showing only the significant result would overstate it.
- **Colour:** response keeps the blue/orange used in earlier figures; the two focal cell types get purple and green (distinct from blue/orange and from each other); all other cell groups are greys. Therapy is shown by marker shape, not colour.
- **Layout:** explicit axes positions in inches, because a grid layout could not give panel c's labels room and caused collisions.
- **Deviation from the skill:** I composed the figure directly in one script instead of fanning out one sub-agent per panel, and did not run the adversarial reviewer loop. Reason: the inputs are small saved tables and one author kept the grid consistent. The look-before-review pass on crops was done.

## 4. Key outputs (measured; every number is from the saved tables)
- Panel b/c: naive/central-memory T 28.8% (responders) vs 7.8% (non-responders), Cliff's delta +0.78, q = 0.019; proliferating T 1.1% vs 5.9%, delta -0.78, q = 0.019.
- Panel d: among CD8A+ T cells, share TCF7-detected, exact p = 0.0006.
- Panel f, exact two-sided p (naive/central-memory T | proliferating T | TCF7 share in CD8 T): primary [0.003, 0.003, 0.0006]; leave-one-out worst [0.0062, 0.0062, 0.0014]; CLR [0.0006, 0.0021, nan]; removed cells returned [0.003, 0.0021, nan]; activated-T cluster dropped [0.0057, 0.0006, nan]; adjusted for median genes [0.0076, 0.0279, 0.003]; adjusted for median mito [0.0653, 0.0279, 0.0133]; anti-PD1-only [0.2141, 0.0727, 0.0162].
- The TCF7 leave-one-out worst case (p = 0.0014) is new in this figure; earlier logs did not report it.
- Panel e therapy counts (non-responders | responders): anti-PD1 8 | 4; anti-CTLA4 + PD1 1 | 4; anti-CTLA4 1 | 1.

## 5. Problems and deviations
- First render had real defects: clipped legend in panel a, a legend and long y labels colliding with neighbouring panels, a cue text sitting on a lollipop, count labels overlapping tick labels, and the panel f legend covering data. Fixed by rebuilding with explicit positions, shortened labels and counts moved into tick labels.
- An automated check kept flagging panel letter `a` as outside the figure. The saved PNG shows it inside (dark pixels at x 32-49, y 41-57); the flag came from measuring at preview dpi (200) while the file is saved at 300 dpi. I judged by the saved file.
- Panel f shows that both key results weaken: naive/central-memory T is above p = 0.05 after adjusting for median mito (0.065) and in anti-PD1-only samples (0.214); proliferating T is above 0.05 in anti-PD1-only samples (0.073). The figure title says so.
- Therapy is not separable from response (panel e). The figure shows this; it does not resolve it.
- No 2-D embedding exists; the figure uses composition plots instead.
- The plotting code lives in the Claude Science session only (captured in the figure's artifact lineage), not in the repo, because new repo files need your approval. The data-loading part is also saved as a workspace file `final_figure_data.py`.
- Still open from earlier logs: the 2019 erratum is unchecked; what "pre-treatment" means for Pre_P1 and Pre_P6 (anti-CTLA4 labelled) is not established; the findings are an association in 19 patients.

## 6. Reproducibility info
- Dataset: GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018); checksums in `data/metadata/DATA_SOURCES.md`.
- Random seed: 42 (`configs/params.yaml`), used only for point jitter; the statistics are exact enumerations.
- Software: Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; skills `figure-style` and `figure-composer`. No packages installed.
- Inputs: the repo tables listed in section 2; parameters unchanged from earlier logs.

## 7. Next steps
1. Review the figure and the six logs in `Analysis Logs/`; commit what you want to keep (nothing was committed).
2. If you want the project reproducible from the repo alone, approve adding the analysis code to `src/` and the fixed parameters to `configs/params.yaml`.
3. Check the 2019 erratum; establish the Pre_P1 and Pre_P6 treatment history; consider an independent cohort for the therapy and technical confounds.
4. Optional: draft methods and results text from the logs with the methods-writer agent.
