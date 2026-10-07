# Analysis log: scRNA-seq v2, step 9 (PCA), GSE120575

Date: 2026-09-30 (local clock). Continues `2026-09-30_scrnaseq-v2-steps-1-8.md` (not edited). Not committed; left for review.

## 1. Session goal
Run step 9 (dimensionality reduction) on the 3,000 highly variable genes approved at step 8, with z-scoring and clipping, verify the decomposition, and test whether the components carry lineage and T-cell state structure before clustering.

## 2. What was done
1. Loaded the filtered matrix and the HVG list `data/processed/hvg_genes.txt`; built a 16,048 cells x 3,000 genes matrix of log2(TPM+1) values (no non-finite entries).
2. Z-scored each gene across cells, clipped at +/-10, re-centred columns, and computed the covariance matrix (3000 x 3000).
3. Exact eigendecomposition (`numpy.linalg.eigh`, 36 s); kept 30 PCs (`dimensionality_reduction.n_pcs` in `configs/params.yaml`).
4. Structural checks, including an independent `scipy.sparse.linalg.svds` run on the same matrix.
5. Correlated PCs with lineage marker scores, genes detected per cell, mito fraction, timepoint, response and sort fraction; computed the share of each PC's variance explained by sample identity (eta squared).
6. Tested T-cell state resolution within T cells (memory versus exhaustion axis, with an additional held-out-gene version and a version with genes detected regressed out).
7. Wrote: `data/processed/pca_scores.csv`, `data/processed/pca_loadings.csv`, `results/step09_pca_summary.csv`, `results/step09_pca_variance_top50.csv`, `figures/step09_pca.png`. Read all back; loadings from the saved file reproduce the saved scores (max difference 1.2e-05, within 5-decimal rounding).

No file in `src/`, `workflows/` or `environment/` was added; no package was installed; `configs/params.yaml` was not changed.

## 3. Why
- **Z-score and clip at +/-10** (approved): without scaling, a few highly expressed genes dominate the components. The clip altered 2,551 of 48,144,000 entries (0.0053%) and reduced total variance from 3,000 to 2,990.08. Columns were re-centred after clipping so the covariance is exact. Rejected: no clipping (a few extreme entries, max |z| 37.2, would bend individual PCs).
- **Exact eigendecomposition** instead of an approximate solver: at 3,000 genes it is cheap and has no randomness parameter.
- **30 PCs** as set in `params.yaml`. The spectrum has no elbow (eigenvalue ratios about 1.03 at PC10/PC11 and PC30/PC31; 253 PCs are needed for 25% of variance), so 30 is a convention, not a measured optimum.
- **Marker scores from the full filtered matrix** (not only the HVGs) to interpret PCs. Lineage = highest of three z-scored panel scores (T/NK: CD3D CD3E CD2 TRAC NKG7; B/plasma: MS4A1 CD79A CD79B CD19 MZB1; myeloid: LYZ CD14 CD68 CSF1R AIF1 FCER1G). T cells = T/NK-labelled with mean(CD3D, CD3E, CD2, TRAC) >= 4.0 (9,873 cells).
- **Held-out test version:** because `IL7R`, `PDCD1`, `HAVCR2`, `CCR7`, `SELL`, `LEF1`, `CTLA4` are HVGs and so shaped the PCs, I repeated the test using only genes that were not HVGs (`TCF7` for memory; `LAG3`, `TIGIT`, `TOX`, `ENTPD1` for exhaustion).

## 4. Key outputs (measured this session)
- Eigenvalues all positive (minimum 0.0204); loadings orthonormal (4.0e-15); score variance equals eigenvalue (1.5e-14); independent `svds` top-5 eigenvalues agree to 3.5e-15.
- Variance explained: PC1 3.53%, PC2 1.68%, PC3 1.07%, PC4 0.47%; 30 PCs together 11.3%.
- Lineage axes recovered: myeloid score vs PC1 r = 0.86; B/plasma vs PC3 r = 0.78; T/NK vs PC2 r = 0.66.
- T-cell state test: memory-minus-exhaustion axis vs PC4 r = -0.65 (held-out genes -0.49) and vs PC8 r = +0.51 (+0.42); unchanged after regressing out genes detected (PC4 -0.66 / -0.49).
- PC1 vs log genes detected: r = 0.79 overall; 0.91 (T/NK), 0.92 (myeloid), 0.81 (B/plasma) within lineage.
- Sample identity explains 47.5% of PC1, 53.2% of PC5, 36.9% of PC13 (chance about 0.3%). `Post_P28` is +4.0 SD on PC1.
- PC5 loadings: heat-shock and immediate-early genes positive (DNAJA1, HSPH1, HSP90AB1, NR4A1, CREM); XIST, MT-RNR2, CISH negative; no lineage correlation (|r| <= 0.07).
- No PC has |r| > 0.3 with timepoint or response. PC1 vs response r = -0.21.

## 5. Problems and deviations
- **PC1 is confounded with library complexity** (see section 4). Myeloid cells also sit on a higher PC1 curve at equal complexity, so PC1 carries both effects and cannot be read as lineage alone. Not corrected; carried into clustering.
- **Sample effects are large:** PC5 (stress program) and PC13 are strongly sample-driven. A stress program can be a tissue-dissociation artefact; this was not tested. Not removed.
- **Lineage labels are crude.** Highest-of-three z-scored scores forces a balance (T/NK 62.4%, myeloid 20.7%, B/plasma 16.9%); these shares are not composition estimates and should not be compared with other runs.
- **Held-out memory score has one gene** (`TCF7`), so that confirmation is coarse.
- **The T-cell threshold (T-core >= 4.0) was chosen after looking at the score distribution**, not before.
- **Comparison with the first run's record** (quoted from the earlier README, not re-measured): PC1 3.31%, 30 PCs 11.8%, PC1 vs genes detected +0.61. Mine: 3.53%, 11.3%, +0.79. Different HVG sets (3,000 at 5% floor versus 2,000 at 1% floor) make a difference expected; the entry was not edited.
- All declared checks passed. The memory/exhaustion test could have failed (no PC reaching |r| >= 0.3) and did not.

## 6. Reproducibility info
- Dataset: GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018); checksums in `data/metadata/DATA_SOURCES.md`.
- Random seed: 42 in `configs/params.yaml`; step 9 has no stochastic procedure (exact PCA, deterministic sign convention).
- Software: Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; `scrnaseq-pipeline` helpers and `figure-style`. No packages installed.
- Parameters used (`configs/params.yaml`): n_pcs 30; normalization.n_variable_features 3000, hvg_min_cell_fraction 0.05, hvg_exclude_vdj true. Clip value (+/-10) is hard-coded in the session code, not in `params.yaml`.

## 7. Next steps
1. **Step 10 clustering** on the 30 PCs: build a kNN graph (k = 15 default), cluster by Ward linkage (Leiden unavailable), choose k by an explicit modularity-plateau rule over a wide range, confirm a single connected component. Watch for clusters driven by `Post_P28`, by the PC5 stress program, or by PC1 complexity.
2. Decision for the user before step 10: whether to leave PC1 and the stress PC (PC5) in, or to test sensitivity by also clustering without them.
3. Step 11 embedding still needs `umap-learn` or scikit-learn (install approval and working network).
4. Open items carried over from the earlier log: erratum check, `Pre_P8` cell-type composition, adding scratch scripts to `src/`, and clip value not yet in `params.yaml` (needs approval to add).
