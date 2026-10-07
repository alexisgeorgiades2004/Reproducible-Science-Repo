# Helpers for the scrnaseq-pipeline skill. Genes are ROWS, cells are COLUMNS.
import gzip
import re

import numpy as np
import pandas as pd

MT13 = ("MT-ND1", "MT-ND2", "MT-CO1", "MT-CO2", "MT-ATP8", "MT-ATP6", "MT-CO3",
        "MT-ND3", "MT-ND4L", "MT-ND4", "MT-ND5", "MT-ND6", "MT-CYB")
VDJ_PATTERN = r"^(TR[ABGD][VDJ]\d|IG[HKL][VDJ]\d)"


def scrna_diagnose_matrix_layout(path, n_probe=6):
    """Trap 1: reconcile header vs data field counts; return the read parameters.

    A silent column shift is the most common way a matrix load goes wrong. Counts
    fields in the first `n_probe` lines, infers how many leading lines are headers,
    and reads the header-vs-data delta to name the layout. Run this BEFORE writing
    any read call, and cross-check `n_value_columns` against the metadata file.
    """
    opener = gzip.open if str(path).endswith(".gz") else open
    rows = []
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i >= n_probe:
                break
            rows.append(line.rstrip("\n").split("\t"))
    counts = [len(r) for r in rows]
    tail = counts[1:] or counts
    data_w = max(set(tail), key=tail.count)
    n_head = 0
    for r, c in zip(rows, counts):
        if c != data_w or (r and r[0].strip() == ""):
            n_head += 1
        else:
            break
    head_w = counts[n_head - 1] if n_head else data_w
    body = rows[n_head:] or rows
    trailing_blank = bool(body) and all(r[-1] == "" for r in body)
    idcols = 0
    for f in body[0][:4]:
        try:
            float(f)
            break
        except ValueError:
            idcols += 1
    delta = data_w - head_w
    n_values = data_w - idcols - (1 if trailing_blank else 0)
    offset = head_w - n_values
    if delta == 1 and trailing_blank:
        note = "trailing tab on every data row - drop the last column"
    elif delta == 1:
        note = "header omits the index column - header names shifted by one"
    elif delta == 2:
        note = "two id columns, or trailing tab plus omitted index - inspect first fields"
    elif delta == 0:
        note = "header width matches data - index column named or placeheld"
    elif delta < 0:
        note = "header padded wider than data - truncate header to the data width"
    else:
        note = "unexpected delta - inspect the probe rows before reading"
    return {"field_counts": counts, "n_header_rows": n_head, "header_width": head_w,
            "data_width": data_w, "delta": delta, "trailing_blank_field": trailing_blank,
            "n_id_columns": idcols, "n_value_columns": n_values,
            "header_label_offset": offset, "diagnosis": note,
            "read_params": {"skiprows": n_head, "index_col": 0,
                            "drop_last_column": trailing_blank},
            "header_labels": [r[offset:offset + n_values] for r in rows[:n_head]],
            "probe_first_fields": [r[:3] for r in rows]}


def scrna_parse_geo_sample_sheet(path, header_first_field="Sample name"):
    """Extract the per-cell table from a filled-in GEO submission spreadsheet.

    The sheet is padded to a fixed width with blank and duplicate column names,
    and the real header sits well below the top. Returns (DataFrame, report).
    """
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    hidx = next(i for i, l in enumerate(lines)
                if l.split("\t")[0].strip() == header_first_field)
    raw = [h.strip() for h in lines[hidx].split("\t")]
    width = max(j for j, h in enumerate(raw) if h) + 1
    header, seen = [], {}
    for j, h in enumerate(raw[:width]):
        name = h or "unnamed_{0}".format(j)
        seen[name] = seen.get(name, 0) + 1
        header.append(name if seen[name] == 1 else "{0}.{1}".format(name, seen[name] - 1))
    keep = [l.split("\t")[:width] for l in lines[hidx + 1:]
            if l.split("\t")[0].strip() and not l.lstrip().startswith("#")
            and len([x for x in l.split("\t")[:width] if x.strip()]) > 2]
    df = pd.DataFrame([(r + [""] * width)[:width] for r in keep], columns=header)
    return df, {"header_line": hidx, "n_rows": len(df), "n_columns": width,
                "total_lines": len(lines)}


def scrna_check_log_scale(mat):
    """Trap 3: identify the value scale by testing TPM's 1e6 column-sum invariant.

    Un-logs with 2**x - 1 and checks where per-cell sums land. A filename is not
    evidence; this is.
    """
    import scipy.sparse as sp
    m = mat.tocsr() if sp.issparse(mat) else sp.csr_matrix(np.asarray(mat))
    lin = np.expm1(m.data.astype(np.float64) * np.log(2.0))
    t = sp.csr_matrix((lin, m.indices.copy(), m.indptr.copy()), shape=m.shape)
    cs = np.asarray(t.sum(axis=0)).ravel()
    raw = np.asarray(m.sum(axis=0)).ravel()
    near = float(np.mean(np.abs(cs - 1e6) / 1e6 < 0.01))
    out = {"median_unlogged_colsum": float(np.median(cs)),
           "frac_within_1pct_of_1e6": near,
           "median_raw_colsum": float(np.median(raw)), "verdict": "unknown"}
    if near > 0.8:
        out["verdict"] = "log2(TPM+1) - do NOT log again"
    elif abs(np.median(cs) * 10.0 - 1e6) / 1e6 < 0.05:
        out["verdict"] = "log2(TPM/10+1) - do NOT log again"
    elif abs(np.median(raw) - 1e6) / 1e6 < 0.05:
        out["verdict"] = "linear TPM - log1p before use"
    return out


def scrna_mito_fraction(mat, genes, is_log2p1=True):
    """Trap 4: mitochondrial fraction on the 13 PROTEIN-CODING MT genes.

    The bare 'MT-' prefix also matches 2 rRNA and 22 tRNA genes; mt-rRNA is
    often the most abundant transcript in the dataset, which inflates the
    fraction several-fold and fails most cells against a 10% cutoff.
    """
    import scipy.sparse as sp
    g = np.asarray([str(x) for x in genes])
    m = mat.tocsr() if sp.issparse(mat) else sp.csr_matrix(np.asarray(mat))
    if is_log2p1:
        lin = np.expm1(m.data.astype(np.float64) * np.log(2.0))
        m = sp.csr_matrix((lin, m.indices.copy(), m.indptr.copy()), shape=m.shape)
    idx = np.where(np.isin(g, np.asarray(MT13)))[0]
    total = np.asarray(m.sum(axis=0)).ravel()
    mito = np.asarray(m[idx].sum(axis=0)).ravel() if len(idx) else np.zeros_like(total)
    pct = 100.0 * np.divide(mito, total, out=np.zeros_like(total), where=total > 0)
    return {"pct": pct, "n_mt_genes_found": int(len(idx)),
            "n_mt_prefix_genes": int(np.char.startswith(g, "MT-").sum()),
            "median_pct": float(np.median(pct))}


def scrna_vdj_mask(genes):
    """Trap 6: boolean mask of receptor V/D/J SEGMENTS, keeping constant regions."""
    rx = re.compile(VDJ_PATTERN)
    return np.asarray([bool(rx.match(str(g))) for g in genes])


def scrna_select_hvg(mat, n_top=2000, min_cells=None, n_bins=20, exclude_mask=None):
    """Trap 5: HVGs by normalised dispersion on UN-LOGGED values, equal-FREQUENCY bins.

    Equal-width bins let one bin hold most genes and normalise nothing; log-space
    dispersion selects sporadically-detected noise. `min_cells` defaults to 1% of
    cells. Returns (mask, diagnostics) - always inspect the chosen genes.
    """
    import scipy.sparse as sp
    m = mat.tocsr() if sp.issparse(mat) else sp.csr_matrix(np.asarray(mat))
    ncell = m.shape[1]
    if min_cells is None:
        min_cells = max(3, int(round(0.01 * ncell)))
    lin = np.expm1(m.data.astype(np.float64) * np.log(2.0))
    t = sp.csr_matrix((lin, m.indices.copy(), m.indptr.copy()), shape=m.shape)
    s1 = np.asarray(t.sum(axis=1)).ravel()
    s2 = np.asarray(t.multiply(t).sum(axis=1)).ravel()
    mean = s1 / ncell
    var = (s2 - ncell * mean ** 2) / (ncell - 1)
    det = m.getnnz(axis=1)
    cand = (mean > 0) & (var > 0) & (det >= min_cells)
    if exclude_mask is not None:
        cand = cand & (~np.asarray(exclude_mask, dtype=bool))
    lm = np.log1p(mean[cand])
    ld = np.log(var[cand] / mean[cand])
    bins = pd.qcut(lm, n_bins, labels=False, duplicates="drop")
    nd = np.full(len(mean), -np.inf)
    buf = np.full(int(cand.sum()), -np.inf)
    for b in np.unique(bins):
        sel = bins == b
        d = ld[sel]
        sd = d.std()
        buf[sel] = (d - d.mean()) / (sd if sd > 0 else 1.0)
    nd[cand] = buf
    top = np.argsort(nd)[::-1][:n_top]
    mask = np.zeros(len(mean), dtype=bool)
    mask[top] = True
    return mask, {"n_candidates": int(cand.sum()), "min_cells": int(min_cells),
                  "median_detection_of_selected": int(np.median(det[mask])),
                  "normalised_dispersion": nd}


def scrna_knn_graph(pcs, k=15):
    """Symmetric binary kNN graph on PC scores (cells x components)."""
    import scipy.sparse as sp
    from scipy.spatial import cKDTree
    x = np.asarray(pcs)
    n = x.shape[0]
    idx = cKDTree(x).query(x, k=k + 1, workers=-1)[1][:, 1:]
    rows = np.repeat(np.arange(n), k)
    a = sp.coo_matrix((np.ones(rows.size), (rows, idx.ravel())), shape=(n, n)).tocsr()
    a = a.maximum(a.T)
    a.setdiag(0)
    a.eliminate_zeros()
    return a


def scrna_modularity(adjacency, labels):
    """Newman modularity of `labels` on an undirected graph. ~0 means no structure."""
    a = adjacency.tocoo()
    lab = np.asarray(labels)
    nl = int(lab.max()) + 1
    deg = np.asarray(adjacency.sum(axis=1)).ravel()
    m2 = deg.sum()
    same = lab[a.row] == lab[a.col]
    lc = np.bincount(lab[a.row][same], weights=a.data[same], minlength=nl) / 2.0
    dc = np.bincount(lab, weights=deg, minlength=nl)
    return float((lc / (m2 / 2.0) - (dc / m2) ** 2).sum())


def scrna_choose_k(linkage_matrix, adjacency, k_min=4, k_max=40, tol=0.01):
    """Pick cluster count by the modularity-plateau rule: smallest k within
    `tol` of the maximum. Sweep widely - a maximum at the edge of the range is
    an artifact of where you stopped searching, not an optimum.
    """
    from scipy.cluster.hierarchy import fcluster
    ks, qs = [], []
    for k in range(k_min, k_max + 1):
        lab = fcluster(linkage_matrix, t=k, criterion="maxclust") - 1
        ks.append(k)
        qs.append(scrna_modularity(adjacency, lab))
    ks = np.asarray(ks)
    qs = np.asarray(qs)
    ksel = int(ks[np.argmax(qs >= (1.0 - tol) * qs.max())])
    return {"k": ksel, "ks": ks, "modularity": qs,
            "k_at_max": int(ks[qs.argmax()]), "q_max": float(qs.max()),
            "still_rising_at_k_max": bool(qs[-1] >= qs[-5]) if len(qs) >= 5 else True}


def scrna_bh(pvalues):
    """Benjamini-Hochberg step-up adjusted p-values (q-values)."""
    p = np.asarray(pvalues, dtype=float)
    n = p.size
    order = np.argsort(p)
    adj = np.empty(n)
    run = 1.0
    for i in range(n - 1, -1, -1):
        run = min(run, p[order[i]] * n / (i + 1))
        adj[order[i]] = run
    return np.minimum(adj, 1.0)
