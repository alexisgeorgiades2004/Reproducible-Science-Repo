# Analysis log: scRNA-seq v2, steps 1-8 (GSE120575)

Date: 2026-09-30 (local clock). Not committed; left for review.

## 1. Session goal
Re-run the Sade-Feldman et al. (Cell 2018) melanoma checkpoint-immunotherapy analysis from the already-present, checksum-verified GEO files, making independent decisions from `CLAUDE.md` and the `scrnaseq-pipeline` skill (not retracing the first run), stopping for approval after each numbered step. Reached step 8 (feature selection); stopped there awaiting approval of step 9.

## 2. What was done
1. **Step 1 (closing).** Re-hashed both raw files (SHA-256, 8 MiB blocks) against the supplied digests; both size and digest matched. Filled in `data/metadata/DATA_SOURCES.md` (citation, accession, URL, download date, file table with checksums, dbGaP note, file quirks); re-parsed its table and re-compared against fresh digests.
2. **Step 2.** Read matrix headers and the annotation sheet without modifying them. Result 55,737 genes x 16,291 cells. Wrote `data/processed/cell_metadata.csv` (16,291 x 9) and `data/processed/gene_order.txt` (55,737 lines).
3. **Step 3.** Cohort characterisation from `cell_metadata.csv`. Wrote `results/step03_cohort_samples.csv` and `figures/step03_cohort_structure.png`.
4. **Step 4.** One streaming pass over the gzip (1,000-gene blocks, 1,397 s) computing per-cell genes detected, un-logged totals, mito fraction (13 protein-coding and all 37 `MT-` genes) and per-gene detection. Wrote `results/step04_qc_cells.csv`, `results/step04_qc_by_seq_unit.csv`, `data/processed/step04_qc_genes.csv`, `figures/step04_qc_metrics.png`.
5. **Step 5.** Second streaming pass (604 s) building one sparse matrix. Wrote `data/processed/expr_log2tpm1_genes_x_cells.npz`.
6. **Step 6.** Applied QC filters read from `configs/params.yaml`. Wrote `data/processed/expr_filtered_log2tpm1_genes_x_cells.npz`, `data/processed/cell_metadata_filtered.csv`, `data/processed/gene_order_filtered.txt`, `results/step06_removed_cells.csv`, `results/step06_filter_by_sample.csv`, `figures/step06_qc_filtering.png`.
7. **Step 7.** Normalization: documented no-op, with tests. Wrote `results/step07_library_size_after_filter.csv`.
8. **Step 8.** HVG selection with V/D/J segments excluded. Ran default settings, found two pre-declared checks failing, ran a sensitivity sweep (8 settings), got approval for the recommended setting, re-ran it. Wrote `results/step08_hvg_candidates_default.csv`, `results/step08_hvg_sensitivity.csv`, `results/step08_hvg_selected.csv`, `data/processed/hvg_genes.txt`, `figures/step08_hvg_selection.png`. **Edited `configs/params.yaml`** (see section 6).

Scratch code (`step04_pass.py`, the step 5 build, the step 6-8 analysis cells) ran in the Claude Science workspace only. Nothing was added to `src/`, `workflows/` or `environment/` because `CLAUDE.md` requires approval first. `step04_pass.py` is saved as a session artifact.

## 3. Why (decisions, parameters, rejected alternatives)
- **Sample unit (step 3).** The annotation's `patient_sample` (48 levels) is the sample; the matrix's second header row (`seq_unit`, 57 levels) only adds a sort-fraction suffix. Rejected: using the patient ID, because response is not constant within a patient ID.
- **Value scale (step 4).** Tested an invariant instead of trusting the filename: three scales predict different per-cell sums; only log2(TPM+1) fits.
- **All genes kept in the sparse matrix (step 5).** Rejected dropping the 5,224 all-zero genes: it saves nothing in sparse form and breaks row alignment with `gene_order.txt`.
- **Filters (step 6)** from `params.yaml`: mito <= 10% on the 13 protein-coding genes, >= 200 genes/cell, >= 3 cells/gene, `max_genes_per_cell` not applied (droplet doublet heuristic; this is plate-based, one cell per well). Rejected the all-37-gene mito definition (fails 75.04% of cells).
- **No normalization (step 7).** Data are already TPM and log2(TPM+1); the standard step would process them twice (counterfactual on 600 cells: value range 0-18.86 became 0-3.18, 5.5% of variance survived). Rejected re-scaling the 36 cells that lost >0.5% of TPM to the gene filter: shift would be median 0.008 log2 units (max 0.257 for one cell) against a median HVG SD of 3.66.
- **V/D/J excluded up front (step 8)**, constant regions kept, per the skill (trap 6).
- **3,000 genes, 5% detection floor (step 8).** Default (1%, 2,000) selected only 2/20 T-cell state genes and 29.3% clone-named/small-RNA/mito genes. Chosen from the sweep: 9.4% noisy, 9/20 T-cell state genes. Rejected: keep default (leaves T-cell structure unresolved); 10% floor (risks excluding minority-lineage genes such as `LYZ`, `CD14`); adding a hand-picked marker panel (circular: biases clustering toward expected types).
- **Not applicable:** Leiden/UMAP packages are not installed; step 11 and clustering method are future decisions.

## 4. Key outputs (all measured this session; read back from the saved files)
- **Raw files:** 126,721,504 B (sha256 43fa3d50...48e3f) and 83,035 B (sha256 6a228029...5df73f); both verified.
- **Matrix:** 55,737 genes x 16,291 cells; 39,238,221 non-zeros (4.32%); annotation 16,291 x 11 after trimming 3 footer rows.
- **Cohort:** 48 samples, 57 sequencing units, 32 patient IDs; 19 pre-treatment samples (5,928 cells, 19 distinct patients, all unsorted), 29 post-treatment (10,363 cells); 17 responder / 31 non-responder samples; 991 cells in sort-enriched fractions of 9 post-treatment samples.
- **QC:** un-logged per-cell sums median 994,726 (94.68% within 1% of 1e6); median genes/cell 2,151; median mito 2.90% (13 genes) vs 12.72% (37 genes).
- **Filtering:** 16,291 -> 16,048 cells (243 removed, all by mito); 55,737 -> 45,686 genes; 98.85% of non-zeros retained; arms balanced (1.64% vs 1.42%, Fisher p=0.276).
- **HVGs:** 3,000 genes from 10,540 candidates; median detection 1,421 cells; 0 V/D/J segments, 14 constant-region genes; 9/20 T-cell state genes; 9.4% clone-named/small-RNA/mito.
- **Figures:** `figures/step03_cohort_structure.png`, `figures/step04_qc_metrics.png`, `figures/step06_qc_filtering.png`, `figures/step08_hvg_selection.png`.
- **Tables:** all `results/step03*` to `results/step08*` files listed in section 2.

## 5. Problems and deviations
- **Annotation parser:** `scrna_parse_geo_sample_sheet` returned 16,294 rows (3 trailing GEO footer rows, not cells). Trimmed by requiring `title` to be a matrix cell ID.
- **Step 3 slip, corrected in-session:** my first `sorted_any` flag counted the `_2` replicate suffix as a sort fraction; corrected before saving.
- **Label inconsistency found (step 3):** response is constant within each of the 48 samples but not within a patient ID. P1, P4, P5, P28 carry both labels (P1 and P5 have two post-treatment samples with opposite labels). P1 and P6 change therapy between timepoints, and both anti-CTLA4 samples are their pre-treatment biopsies. Not resolved; only the sample supports a single outcome.
- **Erratum unchecked:** Cell 2019;176(1-2):404 (PMID 30633907, quoted from an earlier session's record, not verified). One fetch was attempted and stopped at a contact-email prompt that was dismissed; not retried. Whether it changed patient or response labels is unknown.
- **Step 4 error found in step 5 and fixed:** the `mean_log2tpm1` column of `data/processed/step04_qc_genes.csv` was wrong by up to 6.3e-05 in 1,158 genes (float32 mean over a non-contiguous block; reproduced exactly for `MT-CO2`). Rewritten from the float64 matrix mean. Detections, per-cell sums and the numbers quoted in the step 4 summary were unaffected.
- **Per-cell sums sit slightly below 1e6** (median 0.53% short; only 53 cells above 1e6). Cause not established; consistent with genes removed after TPM was computed. Guess, not measured.
- **Uneven removal (step 6):** removal is heterogeneous across samples (chi-square p ~ 3e-136). `Pre_P8` (responder) lost 16.85% and `Pre_P3` (non-responder) 10.20%; the arm-level test cannot see this because they offset. All 19 baseline samples keep >= 163 cells. Whether the removed `Pre_P8` cells are a particular cell type is untested.
- **`Post_P28`:** holds 124 of the 164 cells above 6,000 genes (median 5,500 genes/cell) while its second sample `Post_P28_2` has median 2,817. Left unfiltered; may form its own cluster.
- **Step 7:** gene filter removed rare, very high-TPM genes (`RNU6-*` pseudogenes and other short RNAs) from a few cells; the worst, `B4_P6_M11` (`Pre_P1`, 7,033 genes), lost 61,983 TPM.
- **Step 8 failures:** at the skill default two of four pre-declared checks failed (T-cell state genes absent; 29.3% > 25% noisy picks). At the chosen setting `CD3E`, `CD3D` and `TCF7` are still not HVGs, and the pre-declared "all seven core markers present" check still fails (`CD3E` missing). `TCF7` is the gene the original paper reports as discriminating response.
- **Misstatement corrected:** I said `CD3E` and `CD8A` were missing at every setting. That was inferred from a `core7_all=False` column without checking which gene; at 5%/3,000 `CD8A` is selected. Other settings were not rechecked.
- **Skill helper gap:** `scrna_vdj_mask` misses 29 roman-numeral V pseudogenes (e.g. `IGHVIII-67-3`, `TRGVA`). All are detected in <= 76 cells, below every floor used, so selection was unaffected.
- **Unresolved difference from the first run:** its README entry said 153 receptor segments in the top 2,000; I measure 138 segments + 16 constant-region genes = 154 with no exclusion. Candidate counts agree (17,685). Likely counted constants; unverified. The earlier entry was not edited.
- **Crude heuristic:** the "pseudogene-like" class used to describe HVGs (names ending in `P<digit>`) also matches some real genes; it was used for description only, not for any filter.
- **Environment:** `pyyaml` is not installed; I read `params.yaml` with a small inline parser instead of asking for an install. `params.yaml` has mixed line endings (CRLF in the normalization block), so `edit_file` could not match; the edit was done at byte level and verified with a diff.
- **Figure checks:** several automated text-overlap flags were bounding-box artifacts (leader lines, axis labels) and were judged by viewing the render; two real label collisions were fixed.
- **Machine:** the Python build reports `Windows-10-10.0.26200-SP0 AMD64`; the restart prompt says ARM64.

## 6. Reproducibility info
- **Dataset:** NCBI GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018; doi 10.1016/j.cell.2018.10.038), files from `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE120nnn/GSE120575/suppl/`, downloaded 2026-09-29 (file mtimes). Checksums in `data/metadata/DATA_SOURCES.md`.
- **Random seed:** 42 (`configs/params.yaml`). Used for the 20 random gene rows in the step 5 raw-file check, the 600-cell subsample in step 7, and plot jitter. Steps 1-8 contain no other stochastic procedure.
- **Software:** Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; `scrnaseq-pipeline` skill helpers (`scrna_read_matrix_headers`, `scrna_parse_geo_sample_sheet`, `scrna_select_hvg`, `scrna_vdj_mask`) and `figure-style`. No packages installed this session. scanpy, scikit-learn, igraph, leidenalg and umap-learn are not available.
- **Parameters (`configs/params.yaml`, as left by this session):** seed 42; qc: min_genes_per_cell 200, max_genes_per_cell 6000 (not applied), max_percent_mito 10, mito_gene_set protein_coding_13, min_cells_per_gene 3, apply_max_genes_per_cell false; normalization: n_variable_features **3000** (was 2000), hvg_min_cell_fraction **0.05** (new), hvg_exclude_vdj **true** (new); dimensionality_reduction: n_pcs 30; clustering: resolution 0.5 (a Leiden parameter, unused so far).
- **Repo files edited:** `configs/params.yaml` (the three normalization keys above), `data/metadata/DATA_SOURCES.md` (rewritten from stub). No raw file was modified.

## 7. Next steps
1. **Step 9 (PCA)** on the 3,000 HVGs: z-score genes and clip (decision to confirm), 30 PCs by exact eigendecomposition. Test whether T-cell memory/exhausted states are resolved despite `TCF7`/`CD3E`/`CD3D` not being HVGs; check PC1 against genes detected per cell.
2. Step 10 clustering: Ward on the PCs is the available route (no Leiden); watch for a `Post_P28`-driven cluster; choose k by an explicit modularity rule.
3. Step 11 embedding is blocked on installing `umap-learn` or scikit-learn, which needs your approval and working network access.
4. Step 12 annotation; also test whether the removed `Pre_P8` cells are a specific cell type.
5. Step 13: restrict to the 19 unsorted pre-treatment samples (one per patient); use the sample as the unit; do not use patient-level response labels.
6. Open items: check the 2019 erratum; decide whether to add the scratch scripts to `src/`; `README.md` still points at `workflows/` notebooks that do not exist; commit nothing until you review.
