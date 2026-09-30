---
name: scrnaseq-pipeline
description: "Run single-cell RNA-seq analysis as a gated 13-step pipeline: acquisition, QC, normalisation, feature selection, PCA, clustering, embedding, cell-type annotation and condition comparison. Use whenever the user mentions scRNA-seq, single-cell or single-nucleus RNA-seq, a GEO expression matrix, QC filtering of cells, highly variable genes, clustering cells, UMAP, marker genes, cell-type annotation, or comparing cell-type composition between conditions or treatment arms - even when they name only one stage, e.g. run QC on this matrix, or cluster these cells. Covers plate-based Smart-seq2 and droplet 10x data and reanalysis of published datasets. Carries traps that cost real debugging time: GEO matrices with two header rows and a trailing tab, matrices already log-transformed despite a TPM filename, mitochondrial QC on the wrong MT gene set, dispersion binning that silently selects noise, and receptor V(D)J genes that split T cells by clonotype rather than cell state."
---

# scRNA-seq analysis pipeline

A 13-step sequence for taking a single-cell expression matrix from raw file to a
biological comparison. The numbering is the contract: it is what the user, the
notebooks, the environment registry and the analysis log all refer to.

Each step is small enough to verify and large enough to be worth a stop. The
value of the sequence is not the step list - anyone can write that - but the
checks at each boundary and the traps documented at the end, which are the
places real datasets break silently.

## How to work through this

**Stop after every numbered step and wait for approval before the next.** Do not
chain steps, even when the next is quick. Steps 7, 8 and 9 are three stops.
The reason is that most scRNA-seq errors are *silent*: a bad threshold or a bad
feature set produces plausible-looking clusters, and by step 12 the mistake is
expensive to unwind. A stop is a cheap place to catch it.

**End each step by naming the next one**, what it needs, and any decision that
blocks it. If a step needs an unplanned sub-step, that is another stop.

**Make verification visible.** Show the code and its real output, not a claim
that a check passed. State what would have counted as failure - a check that
cannot fail is not a check. Prefer testing an *invariant the data must satisfy*
over restating what the code did: "TPM columns must sum to 1e6" is a real test;
"the matrix loaded successfully" is not.

**Label every number as measured or quoted.** A figure from a paper, a database
page, or recall is not a measurement. Say which it is. When a published result
and your own measurement agree, that agreement is the strongest end-to-end check
available - say so explicitly.

**Explain every figure in plain language** beside it: what is on each axis, where
to look, what the pattern means, and what it does *not* mean. Expand jargon on
first use. Assume the reader knows the biology but not this pipeline's
conventions. A figure the reader must ask you to interpret is not finished.

**Ask before installing anything** - packages, environments - and before adding
new machinery (scripts, config blocks, helper modules) to a repo. Prefer doing
the step in-session and writing files only once the result is agreed.

**Correct yourself in place.** When a check fails or an earlier claim turns out
wrong, say so plainly in the same response and fix the record. Half the value of
this pipeline is that it caught its own mistakes; hiding them destroys that.

## The 13 steps

| Step | Name | Establishes |
|---|---|---|
| 1 | Data acquisition | Files obtained, checksummed, provenance recorded |
| 2 | Load and inspect | Dimensions, metadata columns, file quirks |
| 3 | Cohort characterisation | Sample/condition structure and confounds |
| 4 | QC metrics | Per-cell and per-gene metrics; **value scale identified** |
| 5 | Build working matrix | One sparse matrix saved; raw file never read again |
| 6 | QC filtering | Cell and gene filters applied |
| 7 | Normalization | Library-size and log handling settled |
| 8 | Feature selection | Highly variable genes chosen |
| 9 | Dimensionality reduction | PCA; component count fixed |
| 10 | Clustering | Cells grouped by expression similarity |
| 11 | Embedding | 2-D layout for visualisation only |
| 12 | Cell-type annotation | Clusters given biological labels |
| 13 | Comparative analysis | The condition contrast |

Steps 1-3 describe, 4-6 control quality, 7-9 build the feature space, 10-12
decide what the cells are, 13 answers the question. A step may legitimately be a
**no-op** - step 7 often is - but say why rather than skipping silently.

### 1. Data acquisition
Confirm the accession before downloading, list what files exist and how large
they are, and check whether the raw data is actually there - many GEO series
hold processed values only, with raw reads in dbGaP under controlled access.
Record accession, URL, date, sizes and SHA-256 in a provenance file. Downloading
two files by hand is often the right answer; do not build a framework for it.

### 2. Load and inspect
Print dimensions, metadata columns and dtypes. Do not modify raw files. Assume
the file layout is wrong until you have looked at the first three lines and the
field counts - see Traps 1 and 2.

### 3. Cohort characterisation
Tabulate samples, conditions, timepoints and batches **before** any modelling.
Ask: how many biological samples, how many patients, are there paired
timepoints, were any samples sorted or enriched? This is where you discover the
confound that would otherwise invalidate step 13.

### 4. QC metrics and value-scale identification
Compute genes detected per cell, cells detected per gene, and mitochondrial
fraction. **Identify the value scale by testing an invariant** - see Trap 3 -
rather than trusting the filename. Compute mitochondrial fraction on the 13
protein-coding MT genes (Trap 4).

### 5. Build the working matrix
Stream the file once into a sparse matrix and save it. scRNA-seq matrices are
typically 90-96% zeros, so sparse storage is an order of magnitude smaller than
dense and usually removes any memory problem outright - check the sparse
footprint before concluding you must filter genes to fit in RAM. Cross-check
gene count and non-zero count against step 4; two independent passes agreeing to
the single non-zero is a real check.

### 6. QC filtering
Apply thresholds and report cells and genes removed. **Check that filtering did
not bias the groups you intend to compare** - equal removal rates across arms.
A filter correlated with the outcome silently corrupts step 13. Inherited
thresholds usually need revisiting: droplet defaults do not transfer to
plate-based data, where one cell per well makes doublet caps largely moot.

### 7. Normalization
If the matrix is already normalised and logged (TPM/CPM + log), this step is a
no-op and applying the usual pipeline would double-transform it. Say so. The
remaining choice is whether to z-score genes before PCA.

### 8. Feature selection
Select ~2,000 highly variable genes by binned normalised dispersion. **Then look
at which genes you got** - see Trap 5. Selection that returns lncRNAs, miRNAs,
mitochondrial tRNAs, or genes detected in a handful of cells is broken, not
subtle. Consider excluding receptor V(D)J segments up front (Trap 6).

### 9. Dimensionality reduction
PCA on scaled HVGs. At a few thousand genes, exact eigendecomposition of the
gene covariance matrix is cheap and avoids a randomness parameter. Verify
eigenvalues are non-negative and loadings orthonormal. Interpret the top
components from their loadings, and **confirm the direction** by correlating each
PC against a summed marker score rather than assuming the sign. Check whether
PC1 correlates with genes detected per cell - if it does, it mixes biology with
library complexity and everything downstream inherits that.

### 10. Clustering
Build a kNN graph on the PCs (k=15 is a reasonable default) and cluster. Leiden
is the field standard; where it is unavailable, Ward linkage on the PCs is
deterministic and defensible, but **say that cluster boundaries will not match
published Leiden results**. Choose the cluster count by an explicit rule, not by
eye - the smallest k whose graph modularity is within 1% of the maximum works
well. Sweep a wide k range: a modularity maximum at the edge of your search
range is an artifact of where you stopped, not an optimum. Confirm the graph is
a single connected component.

### 11. Embedding
UMAP or t-SNE, for looking only. No inference depends on it. Distances and
cluster shapes in an embedding are not quantitatively meaningful; if the
embedding and the clustering disagree, trust the clustering.

### 12. Cell-type annotation
Compute per-cluster mean expression and detection fraction, rank one-vs-rest
enrichment, and score a curated marker panel spanning every lineage you might
plausibly see - including the ones you expect to be absent. Verify with a
population that *should not* be there: if cells were sorted for a surface
marker, the excluded lineage should be absent, and finding it means a sort or
parsing failure. Check that overall lineage composition matches what the
protocol should yield. Beware markers that are not lineage-exclusive - CD4 is
expressed by monocytes, macrophages and dendritic cells, not only T cells.

### 13. Comparative analysis
Decide four things explicitly and state them:

1. **Which contrast** answers the question - baseline-only predicts response;
   pre-vs-post measures treatment effect. They are different questions.
2. **Which samples are eligible** - exclude any whose composition was set by
   the experiment (sorted or enriched fractions) rather than by biology.
3. **The unit of analysis.** Cells from one sample are not independent
   replicates. Use the sample, or the patient; verify one sample per patient if
   you are treating samples as independent. Testing across cells inflates
   significance by orders of magnitude and is the most common serious error in
   this kind of analysis.
4. **The test.** Non-parametric (Mann-Whitney, exact at small n) with
   Benjamini-Hochberg across cell types, reporting an effect size such as
   Cliff's delta alongside p and q.

Then state the limits: the smallest attainable p at your sample size, and the
fact that **proportions are compositional** - they sum to 100%, so a large gain
in one cell type mechanically forces losses elsewhere. Correlate the affected
types before presenting a depletion as independent biology.

## Traps that cost real debugging time

**1. Two header rows.** GEO supplementary matrices often carry a second header
row (sample or batch label per cell) beneath the cell identifiers, both offset
by a leading empty field. Reading with `header=0` silently turns the second row
into a gene called `""`. Read the first three lines and compare field counts.

**2. Trailing tab.** Data rows may end with a tab, so they split into one *more*
field than the header rows. A dtype map applied positionally then shifts every
value by one column. Confirm the extra column parses as all-NaN.

**3. The filename lies about the value scale.** A file named `..._TPM_...` may
contain log2(TPM+1). Test it: un-log with `2**x - 1` and check the per-cell sums
land on 1e6. If they do, it was log2(TPM+1); if they land near 1e7, it was
log2(TPM/10+1); if the un-logged values are astronomical, it was linear all
along. Getting this wrong means either double-logging the data or reporting
"mitochondrial percentages" that are ratios of summed logarithms - a quantity
with no meaning.

**4. `MT-` matches more than you want.** In a full annotation the `MT-` prefix
matches all 37 mitochondrial genes: 13 protein-coding, 2 rRNA, 22 tRNA. Because
mitochondrial rRNA is often the single most abundant transcript in the dataset,
the 37-gene definition can put the median "mitochondrial fraction" above the
conventional 10% cutoff and fail most of your cells. The threshold is defined on
the 13 protein-coding genes. Use `scrna_mito_fraction`.

**5. Dispersion binning fails silently.** Variance/mean dispersion must be
normalised within expression bins, and it must be computed on *un-logged*
values. Two ways this breaks: computing dispersion on log values, and using
equal-*width* bins, where one bin can hold 60%+ of genes and normalise nothing.
Use equal-*frequency* bins and impose a detection floor (genes in >=1% of
cells). The check is to look at the selected genes: a median detection of a
dozen cells means you selected noise.

**6. Receptor V(D)J genes cluster by clonotype, not cell state.** In immune
data, TCR and BCR variable segments are among the most variable genes, and
clustering on them splits T cells by which receptor they carry - patient-
specific clones masquerading as cell types. Exclude the V, D and J *segments*
but **keep the constant regions** (`IGHM`, `IGHD`, `IGKC`, `IGHG1`, `TRAC`,
`TRBC2`): constant regions encode isotype and lineage and are what separates a
plasma cell from a naive B cell. High immunoglobulin in plasma and B cells is
correct biology, not an artifact - the distinction is segments vs constant.

## Helper functions

Loading this skill defines these in the python kernel:

- `scrna_read_matrix_headers(path)` - the two header rows and field counts.
- `scrna_parse_geo_sample_sheet(path, header_first_field)` - pull the per-cell
  table out of a filled-in GEO submission spreadsheet.
- `scrna_check_log_scale(values_or_matrix)` - the Trap 3 invariant test.
- `scrna_mito_fraction(matrix, genes, is_log2p1)` - Trap 4, 13 protein-coding.
- `scrna_select_hvg(matrix, n_top, min_cells, n_bins, exclude_mask)` - Trap 5,
  equal-frequency bins on un-logged dispersion.
- `scrna_vdj_mask(genes)` - Trap 6, V/D/J segments only.
- `scrna_knn_graph(pcs, k)` and `scrna_modularity(adjacency, labels)`.
- `scrna_choose_k(linkage_matrix, adjacency, k_min, k_max, tol)` - plateau rule.
- `scrna_bh(pvalues)` - Benjamini-Hochberg step-up.

Read their docstrings for signatures. They assume genes are rows and cells are
columns in a `scipy.sparse` CSR matrix.
