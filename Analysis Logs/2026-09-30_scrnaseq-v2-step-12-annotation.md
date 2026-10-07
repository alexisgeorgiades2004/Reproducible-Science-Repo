# Analysis log: scRNA-seq v2, step 12 (cell-type annotation), GSE120575

Date: 2026-09-30 (local clock). Continues `2026-09-30_scrnaseq-v2-step-10-clustering.md` (not edited). Not committed; left for review. Step 11 (embedding) was deferred and not run.

## 1. Session goal
Annotate the clusters from step 10 using marker evidence, verify the annotation against what the CD45+ sort should and should not yield, and answer the open question from step 6: what cell types did the mitochondrial filter remove.

## 2. What was done
1. Took "proceed" as approval of the recommendation from step 10: annotate the sensitivity clustering (28 PCs, k = 13); defer step 11.
2. Computed per-cluster mean expression and detection fraction for all 45,686 genes; ranked one-vs-rest enrichment (mean log2 difference, genes detected in >= 25% of the cluster).
3. Scored a curated panel of 20 marker groups spanning T/NK, B, plasma, pDC, myeloid, and absent lineages (melanoma, stromal/epithelial, erythroid/platelet, mast, neutrophil); drilled into specific genes for the myeloid and T/NK clusters.
4. Checked composition in unsorted samples and in the sort-enriched fractions.
5. Projected the 243 cells removed in step 6 into the existing PC space using the stored scaling (mean, SD, clip at +/-10, re-centring constant, loadings), assigned them to clusters by nearest neighbours (k = 15, 28 PCs), and compared with the kept cells.
6. Wrote: `data/processed/cell_annotations.csv`, `results/step12_cluster_annotation.csv`, `results/step12_panel_group_scores.csv`, `results/step12_cluster_markers_top30.csv`, `results/step12_removed_cells_projected_assignment.csv`, `figures/step12_annotation.png`. Read back; per-cell file matches the cluster table (counts per cluster identical, cell order equals the filtered metadata).

No file was added to `src/`, `workflows/` or `environment/`; no package installed; `configs/params.yaml` unchanged. The original unfiltered matrix was read (not modified) for the projection.

## 3. Why
- Annotated from unbiased enrichment plus a curated panel, not from a reference-mapping package (none installed). Panel spans lineages expected absent so the sort can be checked.
- Used `CD4` only within T clusters: it is also expressed by pDC (mean 4.3) and cDC (3.1).
- Projected removed cells instead of re-running the pipeline with them, so the kept-cell results stay unchanged. Rejected re-clustering with the removed cells included (would alter step 10 labels).
- Pre-declared checks: no melanoma signal; composition T/NK-dominated in unsorted cells (a general expectation about sorted tumour-infiltrating immune cells, not a measurement); and a margin check on panel groups, which I did not use (see section 5).

## 4. Key outputs (measured this session)
- Annotation (cluster: type, n): C0 B cell IGHM+ 1,441; C1 pDC 264; C2 plasma cell 302; C3 proliferating T 812; C4 monocyte/macrophage 640; C5 exhausted CD8 T 2,328; C6 activated CD8 T (GZMK+ TIGIT+) 750; C7 CD4 T Treg-like 1,872; C8 NK/cytotoxic effector 922; C9 effector-memory CD8 T (GZMK+) 2,582; C10 activated T (CD8-biased) 1,806; C11 cDC 296; C12 naive/central-memory T (TCF7+) 2,033. Confidence notes per cluster are in `results/step12_cluster_annotation.csv`.
- Absent-lineage check: highest cluster mean `PMEL` 0.12 (C7, 2% of cells), `MLANA` 0.13 (C6, 2%), `TYR` 0.02, `SOX10` 0.04, `COL1A1` 0.16, `EPCAM` 0.05; passes. `MITF` (1.26) and `S100B` (1.42) in myeloid clusters are not melanoma-specific.
- Composition (lineage groups from the annotation): all cells T 75.9%, B/plasma 10.9%, myeloid (C4+C11) 5.8%, NK/cytotoxic 5.7%, pDC 1.6%; unsorted cells T + NK/cytotoxic 81.2%, myeloid 6.1%; unsorted pre-treatment baseline (5,827 cells) T 73.6%, B/plasma 10.7%, NK/cytotoxic 7.7%, myeloid 6.6%.
- Sort fractions: `T_enriched` cells (849 after QC filtering; 873 before, 24 removed in step 6) are 98.6% T/NK; the 117 `myeloid_enriched` cells are 64 B, 18 plasma, 14 NK, 13 cDC, 6 pDC, 2 T, and none in the monocyte/macrophage cluster.
- Removed cells: 104 of 243 (42.8%) project into C10 versus 11.3% of kept cells (expected 27.3; none of 20,000 Monte Carlo draws reached 104); 47 (19.3%) into monocyte/macrophage versus 4.0% (expected 9.7); chi-square 440, 12 df. `Pre_P8`: 24 of 45 removed cells are monocyte/macrophage (53%) versus 5% of its kept cells; 24 of its 35 monocyte/macrophages (69%) were removed. Baseline-wide, returning the removed cells would shift the C10 share from 8.5% to 9.0% and the monocyte/macrophage share from 5.2% to 5.7%.
- Projection validation: the same projection reproduces the stored PC scores of 300 kept cells (max difference 0.0); shifting the scaling mean by 0.05 SD changes them by up to 1.80 (the check can fail); nearest-neighbour assignment recovers the true cluster of 88% of those 300 cells (C10: 81%, n = 27).

## 5. Problems and deviations
- **My second pre-declared check was badly specified and I did not use it.** It required the top panel group to lead the second by >= 1.0, but groups overlap by design (T cell vs cytotoxic, monocyte/macrophage vs neutrophil), so low margins (C3, C4, C5, C10, C11) were not informative. Replaced by gene-level drill-down.
- **Neutrophil question (C4):** `FCGR3B` is detected in 60% of C4 cells but `CXCR2` in 3%, and `FCGR3B` does not co-vary with `CSF3R` (r = -0.09). I interpret C4 as monocytes/macrophages (`CD14` 8.7, `CD68` 9.0, `CD163` 5.6). My explanation that `FCGR3B` reads cross-map from `FCGR3A` (7.3 in the same cells) is a hypothesis; I did not test it.
- **Labels are interpretations of top genes, with varying confidence.** C10 (CD3E in 65%, CD4 in 27%, activation genes RGS1, DUSP4, TNFAIP3) is the least certain. C8 contains CD3-positive cytotoxic cells as well as NK (CD3E 61%, TRDC 39%, NCAM1 22%). C7 is CD4 with FOXP3 in only 46%, so it mixes Treg-like and other activated CD4 cells. C12 is mixed CD4/CD8 (34% each). C6 is partly cycling (STMN1 54%).
- **Unexpected sort result:** the `myeloid_enriched` fraction (117 cells, Post_P17 and Post_P19) is not myeloid. The sort gate is not available in the data; I cannot say why. Both samples are post-treatment, so they are outside the baseline contrast.
- **Projected removed cells lie somewhat farther from their neighbours** than kept cells (median 15th-neighbour distance 9.2 versus 7.5; p95 13.8 versus 12.8), so assignments for them are less certain than the 88% validation on kept cells suggests.
- One validation control (dropping the re-centring constant) moved scores by only 0.01 because clipping alters so few entries; it is a weak control and I relied on the mean-shift control.
- **I printed a per-cell responder versus non-responder breakdown of cell types in the baseline.** Cells from one sample are not independent, and nothing should be inferred from it; step 13 must use the sample as the unit.
- Step 11 (embedding) remains undone: no 2-D cluster map exists.
- Unchanged from the earlier logs: erratum unchecked; scratch scripts not in `src/`.

## 6. Reproducibility info
- Dataset: GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018); checksums in `data/metadata/DATA_SOURCES.md`.
- Random seed: 42 (`configs/params.yaml`); used for the 300 validation cells and the 20,000-draw Monte Carlo. Enrichment, scoring and kNN assignment are deterministic.
- Software: Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; `scrnaseq-pipeline` skill and `figure-style`. No packages installed.
- Inputs: `data/processed/cluster_labels.csv` (column `cluster_sens_k13_28pcs`), `pca_scores.csv`, `pca_loadings.csv`, `hvg_genes.txt`, the filtered and unfiltered sparse matrices. Parameters unchanged from earlier logs; the enrichment detection floor (25%) and projection k (15) are fixed in session code, not in `params.yaml`.

## 7. Next steps
1. **Step 13 (comparative analysis).** Proposed design: restrict to the 19 unsorted pre-treatment samples (9 responder, 10 non-responder; one sample per patient); use the sample as the unit; compare per-cell-type proportions with an exact Mann-Whitney test, Benjamini-Hochberg across cell types, Cliff's delta as effect size; state the smallest attainable p at this n and that proportions are compositional.
2. Decisions for the user at step 13: whether to merge or drop the low-confidence cluster C10 and the two small clusters; whether to run a sensitivity analysis with the removed `Pre_P8` cells (their projected assignments are in `results/step12_removed_cells_projected_assignment.csv`); how to treat the therapy imbalance (anti-PD1 alone is 9 responder versus 26 non-responder samples overall; this is not adjusted for).
3. Do not use patient-level response labels (P1, P4, P5, P28 carry both labels).
4. Open items: step 11 (needs `umap-learn` or scikit-learn: install approval and network); 2019 erratum check; whether to add scripts to `src/` and the fixed parameters to `params.yaml`; `README.md` still points at notebooks that do not exist.
