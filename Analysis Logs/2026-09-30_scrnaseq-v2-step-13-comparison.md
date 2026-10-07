# Analysis log: scRNA-seq v2, step 13 (comparative analysis), GSE120575

Date: 2026-09-30 (local clock). Continues `2026-09-30_scrnaseq-v2-step-12-annotation.md` (not edited). Not committed; left for review. Step 11 (embedding) remains deferred.

## 1. Session goal
Test whether baseline (pre-treatment) immune cell-type composition differs between responders and non-responders, using the 13 annotated cell types from step 12, with the sample as the unit of analysis.

## 2. What was done
1. Kernel state had been reset; restored all inputs from disk (`data/processed/cell_annotations.csv`, `cell_metadata_filtered.csv`, `results/step12_removed_cells_projected_assignment.csv`, the filtered sparse matrix for four marker genes).
2. Selected the eligible samples (unsorted, pre-treatment) and checked invariants.
3. Computed each sample's proportion of cells per cell type; ran an exact two-sided rank-sum permutation test per type (all C(19,9) = 92,378 assignments), Benjamini-Hochberg across 13 tests, Cliff's delta, and a family-wise permutation p-value (smallest per-type p across types in each assignment).
4. Robustness: scipy asymptotic comparison, leave-one-sample-out, technical covariates by arm, rank-residual adjustment for median genes and median mito, centred log-ratio re-test, therapy subset, three sensitivity analyses, a cell-level test for contrast.
5. A targeted check on `TCF7`: per sample, the share of CD8A-detected T cells in which `TCF7` is detected (and the same for CD4-type T cells).
6. Wrote: `results/step13_composition_tests.csv`, `results/step13_sample_proportions_pct.csv`, `results/step13_sensitivity_tests.csv`, `results/step13_clr_tests.csv`, `results/step13_tcf7_in_cd8_by_sample.csv`, `figures/step13_baseline_composition.png`. Read back; headline p-values and deltas re-derived from the saved proportions file match the saved test table; proportions sum to 100 per sample (max deviation 0.002).

No file was added to `src/`, `workflows/` or `environment/`; no package installed; `configs/params.yaml` unchanged.

## 3. Why
- **Contrast:** baseline-only, because the question is whether pre-treatment composition associates with response. Pre-versus-post would ask about treatment effect, a different question.
- **Eligible samples:** unsorted pre-treatment samples. All sort-enriched samples are post-treatment, so the baseline set contains none; no sample was excluded for composition set by the experiment.
- **Unit:** the sample. Each of the 19 samples is from a distinct patient (checked), and cells within a sample are not independent. Rejected testing across cells: it gave p = 1.8e-113 for the main result against a valid 0.0030.
- **Test:** exact rank-sum permutation (non-parametric because proportions are bounded and skewed; exact because n is small and many proportions tie at zero). BH over all 13 types (no merging or dropping, my default for a decision the user left open); family-wise permutation p as an independent multiplicity check.
- **Rejected alternatives:** adjusting for therapy (19 samples, therapy strongly aligned with arm: it would remove most of the information); dropping small or low-confidence clusters from the primary family (run as a sensitivity instead).
- **The `TCF7` check** was chosen after seeing the cluster result, on the basis that `TCF7` is the gene the original study highlights. It is a single targeted test, outside the BH family.

## 4. Key outputs (measured this session)
- Design: 19 samples (9 responder, 10 non-responder), 5,827 cells, 163 to 450 cells per sample, 19 distinct patients, one response label per sample. Smallest attainable two-sided p = 2.17e-05.
- Two types pass q < 0.05: **naive/central-memory T (TCF7+)** higher in responders (28.8% vs 7.8% of a sample's cells; median 28.8% vs 6.7%; Cliff's delta +0.78; exact p 0.0030; q 0.019; family-wise p 0.036) and **proliferating T** lower (1.1% vs 5.9%; delta -0.78; p 0.0030; q 0.019; family-wise p 0.029).
- Suggestive only (q 0.055 to 0.099): B cell (+0.64), pDC (-0.64), activated CD8 T GZMK+ TIGIT+ (-0.56), monocyte/macrophage (-0.54), activated T CD8-biased (-0.53). Not significant: cDC, CD4 Treg-like, exhausted CD8, NK/cytotoxic, plasma, effector-memory CD8 (q >= 0.21).
- Scipy asymptotic p-values agree with the exact ones to within about 0.002. Leave-one-sample-out: both key results keep p <= 0.0062 and |delta| between 0.75 and 0.90. CLR re-test: naive T q 0.008, proliferating q 0.014, B cell q 0.025.
- Sensitivity: returning the removed cells (analysis A) and dropping C10 (analysis C) leave both key results intact (q 0.019 and 0.019 in A; q 0.008 and 0.034 in C). Collapsing to four lineages (B): nothing significant (smallest q 0.073).
- `TCF7` among CD8A+ T cells: median 51.3% of cells TCF7-detected in responder samples versus 20.9% in non-responders (delta +0.87, exact p 0.0006; at least 34 CD8A+ T cells per sample); CD4-type T cells 50.8% vs 30.3% (delta +0.58, p 0.035).

## 5. Problems and deviations
- **Technical imbalance between arms.** Median mito fraction of kept cells is higher in responder samples (3.1% vs 2.6%, exact p 0.022); median genes detected is lower (1,934 vs 2,178, p 0.095). After rank-residual adjustment for median genes the naive T effect holds (delta +0.71, p 0.0076) and the proliferating T effect holds (-0.60, p 0.028); adjusting for median mito, naive T weakens to delta +0.51, p 0.065 while proliferating T stays at p 0.028. B cell and pDC lose significance under either adjustment, so I do not treat them as findings. With 19 samples this adjustment is crude.
- **Therapy cannot be separated from response.** 4 of 9 responders and 1 of 10 non-responders are on anti-CTLA4+PD1; 8 of 10 non-responders and 4 of 9 responders are on anti-PD1 alone. Within anti-PD1-only samples (4 vs 8; smallest attainable p 0.004) the directions agree but are not significant for the clustered types (naive T delta +0.50, p 0.21; proliferating T -0.69, p 0.073); the `TCF7` check holds there (delta +0.88, p 0.016). Median naive T proportion is 28.8% in combination-therapy samples versus 8.7% in anti-PD1 alone. Not adjusted for.
- **Cell types are sparse in some samples.** Plasma cells: zero cells in 10 of 19 samples, 76% of all in one sample; cDC 40% in one sample; B cells 38%; activated T (C10) 37%. Results for these types are unreliable. The B-cell result in particular is strong within anti-PD1-only samples (delta +0.94, p 0.008) but vanishes after technical adjustment; exploratory.
- **Compositional coupling.** Naive T and proliferating T proportions correlate -0.42 across samples; part of each effect may mirror the other.
- **`TCF7` check limits.** It is detection-based (log2(TPM+1) > 0), single-gene, and was decided after seeing the clustering result; it is not corrected for multiplicity. Naive/central-memory cluster C12 mixes CD4 and CD8 cells, so the cluster result alone does not establish a CD8 effect; the `TCF7` check addresses that. Detection-based fractions could rise with depth, but responder samples are shallower, so depth would bias against the result (Spearman with median genes -0.18).
- **Comparison with the first run's record** (quoted from the first README, not re-measured): memory T 44.9% vs 14.9% (delta +0.93, q 0.003) and proliferating T 0.9% vs 5.1% (delta -0.80, q 0.020). Directions agree; magnitudes differ. Cell-type definitions, clustering, HVG set and PCs all differ between runs, so the numbers are not directly comparable. That the original study reported higher TCF7+ CD8 T-cell frequency in responders is quoted from earlier session notes and memory of the paper, not verified here.
- A formatting error in one print statement raised an exception after the files were saved; fixed and the checks re-run. No result affected.
- Still open from earlier logs: the 2019 erratum (Cell 2019;176(1-2):404, PMID 30633907) is unchecked, so any label or count change it made is unknown; `Pre_P1` and `Pre_P6` carry anti-CTLA4 labels while their post samples carry anti-PD1, and I have not established what "pre-treatment" means for those two patients.
- This is an association with a binary response label in 19 patients, not a survival analysis and not a causal claim.

## 6. Reproducibility info
- Dataset: GEO GSE120575 (Sade-Feldman et al., Cell 175(4):998-1013.e20, 2018); checksums in `data/metadata/DATA_SOURCES.md`.
- Random seed: 42 (`configs/params.yaml`); used only for plot jitter. The permutation tests enumerate all assignments and are deterministic.
- Software: Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1, matplotlib 3.11.2; `scrnaseq-pipeline` skill (`scrna_bh` agreed with my local Benjamini-Hochberg), `figure-style`. No packages installed.
- Inputs: step 12 annotations of the sensitivity clustering (28 PCs, k = 13); filtered metadata; parameters unchanged from earlier logs. The detection rule (value > 0), the 15-cell minimum per sample for the `TCF7` check, and the test design are fixed in session code, not in `params.yaml`.

## 7. Next steps
1. All 13 pipeline steps are now complete except step 11 (embedding), which needs `umap-learn` or scikit-learn: install approval and working network.
2. To address the therapy and technical confounds the data cannot settle: validate in an independent cohort, or check the erratum for label changes. Within this dataset the honest limit is stated in section 5.
3. Check the 2019 erratum; establish what Pre_P1 and Pre_P6 pre-treatment means.
4. Decide whether to add scripts to `src/` and move fixed parameters into `configs/params.yaml`; `README.md` still points at notebooks that do not exist.
5. Optional: draft methods and results text with the methods-writer agent from these logs; commit when ready.
