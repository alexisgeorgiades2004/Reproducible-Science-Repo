# Analysis log: scRNA-seq v2, step 10 (clustering), GSE120575

Date: 2026-09-30 (local clock). Continues `2026-09-30_scrnaseq-v2-step-9-pca.md` (not edited). Not committed; left for review.

## 1. Session goal
Cluster the 16,048 filtered cells on the PC space from step 9, with a sensitivity run that drops PC1 (library complexity) and PC5 (stress program), and test whether either clustering is driven by a single sample or by sequencing depth.

## 2. What was done
1. Built a symmetric kNN graph (k = 15) on the 30 PC scores (main) and on 28 PC scores without PC1 and PC5 (sensitivity); confirmed connectivity.
2. Ward hierarchical linkage on the PC scores for each version; swept k = 2 to 60 and computed graph modularity at each k; chose k by the plateau rule (smallest k within 1% of maximum modularity).
3. Compared the two clusterings (adjusted Rand index) and tabulated each cluster's composition: lineage label, largest-sample share, number of samples, median genes detected, Post_P28 share, timepoint and response shares.
4. Inspected the clusters flagged by the lineage-purity check using one-vs-rest mean expression difference (genes detected in >= 25% of the cluster) on the filtered matrix.
5. Wrote: `data/processed/cluster_labels.csv`, `data/processed/ward_linkage_main_30pcs.npy`, `data/processed/ward_linkage_sens_28pcs.npy`, `results/step10_modularity_sweep.csv`, `results/step10_cluster_composition_main_k16.csv`, `results/step10_cluster_composition_sens_k13.csv`, `figures/step10_clustering.png`. Read back; re-cutting the saved linkages reproduces the saved labels exactly.

Nothing was added to `src/`, `workflows/` or `environment/`; no package installed; `configs/params.yaml` unchanged.

## 3. Why
- **Ward on the PCs** because `leidenalg`, `python-igraph`, `scikit-learn` and `scanpy` are not installed. Ward is deterministic and runs on the same PC space; cluster boundaries will not match published Leiden results.
- **kNN graph k = 15** (skill default) for the modularity criterion, which is evaluated on the graph while Ward clusters the PCs themselves.
- **k chosen by rule**, not by eye: smallest k with modularity within 1% of the maximum, over a wide sweep (2-60) so a maximum at the edge would be visible.
- **Sensitivity run** (drop PC1 and PC5) because step 9 showed PC1 is mostly library complexity (r = 0.91 / 0.92 / 0.81 within lineage) and PC5 is a sample-driven stress program.
- **Lineage-purity check dropped as pass/fail** after inspection (see section 5).

## 4. Key outputs (measured this session)
- Both graphs: one connected component (main 183,916 undirected edges; sensitivity 185,963).
- Main (30 PCs): rule gives k = 16, modularity 0.6967; maximum 0.6981 at k = 17. Sensitivity (28 PCs): rule gives k = 13, modularity 0.6911; maximum 0.6936 at k = 16. Neither maximum is near the edge of the sweep. Shuffled labels of the same sizes give modularity 0.0003.
- ARI between the two clusterings: 0.507 (own k), 0.442 (matched k = 13), 0.521 (matched k = 16).
- Main cluster sizes 237 to 3,250; sensitivity 264 to 2,582.
- Main: cluster 0 (300 myeloid cells) is 83.0% Post_P28 with median 5,975 genes/cell; 6 of 16 clusters (2,084 cells) have median genes outside 0.67x-1.5x of the overall 2,157.
- Sensitivity: no cluster has > 50% of cells from one sample (largest 30.8%, cluster 2); 3 of 13 clusters (1,372 cells; clusters 1, 3, 11) are outside the complexity band.
- Sensitivity cluster 12 (2,033 cells) top genes: IL7R, CCR7, TCF7, ANXA1, LEF1 (memory/naive T pattern). Sensitivity cluster 8 (922) and main cluster 10 (857): GNLY, NKG7, KLRD1, FGFBP2, FCGR3A (NK/cytotoxic). Sensitivity cluster 10 (1,806): CCL5, CD8A, HAVCR2, DUSP4 (CD8 effector/exhausted-like). These are interpretations from top genes, not annotations; annotation is step 12.

## 5. Problems and deviations
- **Main clustering fails the sample-driven check** (cluster 0, 83% Post_P28) and the depth check (6 clusters).
- **Robustness borderline:** ARI 0.507 passes my 0.5 threshold only at each version's own k and falls to 0.442 at matched k, so PC1 and PC5 materially influence the grouping.
- **Lineage-purity check was a poor test.** It used the highest of three z-scored marker scores. 29.9% of cells have an ambiguous label (top two z-scores within 0.5), and the label cannot place NK cells (low CD3). The clusters it flagged (main 10, sensitivity 8, 10, 12) are coherent populations. I stopped treating it as pass/fail; the threshold (70%) was set by me without validation.
- **Complexity is not removed by dropping PC1.** Three sensitivity clusters (1, 3, 11) still have median 3,272-4,195 genes/cell; PC2 correlated 0.44 with genes detected. Myeloid cells do have somewhat higher counts on average (about 2,529 vs 2,238 for T/NK), so some of this may be biology.
- **Post_P28** (369 cells) is no longer a cluster of its own in the sensitivity run: 258 of its cells fall in sensitivity cluster 10 (14.3% of that cluster) and 64 in cluster 3.
- The sweep range (2-60), tolerance (1%) and k of the graph (15) are fixed in session code and not in `configs/params.yaml` (its `clustering.resolution: 0.5` is a Leiden parameter and unused).
- Complexity band (0.67x-1.5x median) and the 50% single-sample limit were chosen by me before running; they are conventions, not validated thresholds.

## 6. Reproducibility info
- Dataset: GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018); checksums in `data/metadata/DATA_SOURCES.md`.
- Random seed: 42 (`configs/params.yaml`); used only for the shuffled-label baseline. kNN (cKDTree) and Ward are deterministic.
- Software: Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; `scrnaseq-pipeline` helpers `scrna_knn_graph`, `scrna_modularity`, `scrna_choose_k`; `figure-style`. No packages installed.
- Parameters: kNN k = 15; Ward linkage; k sweep 2-60; plateau tolerance 0.01; inputs PCs from step 9 (n_pcs 30, minus PC1 and PC5 for the sensitivity run).

## 7. Next steps
1. **Decision needed from the user:** which clustering is the working one for annotation. Recommendation: the sensitivity clustering (28 PCs, k = 13), because it removes the sample-driven cluster, cuts cells in depth-stratified clusters from 2,084 to 1,372, keeps myeloid and B/plasma clusters pure (0.89-1.0), and recovers a memory/naive T cluster with TCF7, IL7R and CCR7. Costs: ARI with main is only about 0.5, and some depth effect remains.
2. Step 11 (embedding) is still blocked on installing umap-learn or scikit-learn (approval and working network needed).
3. Step 12 (annotation) on the chosen clustering: score a marker panel spanning all lineages including ones expected absent (melanoma markers `PMEL`, `MLANA`), test whether removed `Pre_P8` cells are a specific cell type, and check the depth-stratified clusters for sample effects.
4. Open items carried over: 2019 erratum check; adding scratch scripts to `src/`; clip value, sweep range and tolerance not yet in `params.yaml`.
