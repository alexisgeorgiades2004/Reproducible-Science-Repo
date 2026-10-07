---
name: figure-standards
description: "Sourced rules for scientific graphs, each traceable to a published guideline rather than to taste. Load before making any graph that will be shown, saved or published - alongside `figure-style`, which supplies the matplotlib helpers and the render-then-verify loop. Covers when a bar chart of continuous data is the wrong chart and what replaces it, how to define error bars and state n, how to pick the unit of replication in nested designs so cells are not treated as independent replicates, which visual channels people decode accurately, colour-vision-deficiency-safe palettes and why nothing may be encoded by colour alone, perceptually uniform colour maps and the distortion rainbow/jet introduces, and why venue specifications are looked up rather than recalled. Ships okabe_ito() for the colour-universal-design palette and cvd_check() to simulate dichromacy and flag confusable pairs before a figure ships."
---

# Figure standards: the rules, and whose rules they are

This skill answers "what rule, and who says so". `figure-style` answers "how do I
render it" - it carries `apply_figure_style()`, the plotting helpers and the §9
render-then-verify loop. **Load both when producing a figure that ships.** Where
they overlap they agree; where this skill adds a constraint, it is because a
cited source is more specific than a general legibility rule.

Every rule below names its source. A rule you cannot trace is a preference, and
preferences do not survive a reviewer who disagrees.

## A. Show the data, not a summary of it

**A1. A bar chart of a continuous outcome hides the distribution.** Bar-and-line
graphs of continuous data are compatible with many different underlying
distributions - the same two bars can be produced by well-separated groups, by
heavily overlapping groups, or by one outlier. For small n, show every data
point; for larger n use a box, violin, or dot plot. Reserve bars for counts and
proportions, where the bar length is the quantity. *(Weissgerber 2015; Nature
Methods editorial 2014; Streit & Gehlenborg 2014.)*

**A2. An error bar is meaningless until you say what it is.** SD, SEM and 95% CI
differ by large factors and answer different questions - SD describes the
spread of the data, SEM and CI describe uncertainty in the mean. State which one
is drawn, and state n, in the figure or its caption. Never compare two SEM bars
by eye and conclude significance. *(Cumming, Fidler & Vaux 2007.)*

**A3. Decide the unit of replication before plotting, and show both levels.**
When measurements nest inside biological samples - cells within a patient, wells
within an animal - the sample is the replicate, not the measurement. Plotting
thousands of cells as independent points inflates significance by orders of
magnitude. Show the per-sample summary as the analysed unit, optionally over the
raw measurements. *(Lord et al. 2020, "SuperPlots".)*

> This is the rule most likely to bite in this repo. The scRNA-seq pipeline's
> step 13 is explicit about it for the same reason.

## B. Encode quantities in channels people decode accurately

**B1. Position beats length beats angle, area and colour.** Judgements along a
common scale are the most accurate; unaligned position next; then length; then
angle, area, and colour saturation. Prefer a dot or bar on a common axis over a
pie, a bubble, or a heatmap cell when the reader has to compare magnitudes.
*(Cleveland & McGill 1984.)* The ordering is robust but not absolute - the
modern replication finds channel accuracy depends on the task and the number of
marks, so treat it as a strong prior, not a law. *(McColeman et al. 2022.)*

**B2. No 3-D effects on 2-D data, and no pie chart for comparison.** Perspective
distorts the very channel the reader is decoding. *(Rougier et al. 2014; Nguyen
et al. 2021 catalogues these as among the most frequent published pitfalls.)*

## C. Colour

**C1. Design for dichromats from the start.** Red-green colour vision deficiency
affects a substantial minority of readers, so a red-versus-green contrast is not
a usable distinction. Use a palette validated for colour-universal design -
`okabe_ito()` ships one. *(Wong 2011a; Okabe & Ito, Color Universal Design.)*

**C2. Never encode anything by colour alone.** Carry the distinction redundantly
in position, shape, line style, or direct labelling, so the figure survives
greyscale printing and dichromatic vision. *(Wong 2011b.)*

**C3. Continuous data needs a perceptually uniform, monotonic-lightness map.**
Rainbow and jet introduce false boundaries where the map's lightness turns and
flatten real gradients where it does not - readers see structure the data does
not contain. Use viridis, cividis, or the scientific colour maps. *(Crameri,
Shephard & Heron 2020; Borland & Taylor 2007.)* The honest counterpoint: rainbow
maps can outperform for reading precise values off a legend in some tasks - the
objection is to using them for spatial structure. *(Ware et al. 2023.)*

**C4. A diverging map is centred on the semantic zero**, not the data midpoint -
0 for a difference, 1 for a ratio, the control value for a fold-change.
Otherwise the neutral colour lands on an arbitrary value and every
above/below judgement the reader makes is wrong. *(Crameri et al. 2020.)*

**Check it, don't assume it:**

```python
cvd_check(["#1f6fb4", "#d9731a"], kind="deuteranopia")
# -> {'ok': True, 'min_delta_e': 117.6, 'confusable': []}
cvd_check(["#d62728", "#2ca02c"], kind="deuteranopia", labels=["red", "green"])
# -> {'ok': False, 'min_delta_e': 8.2, 'confusable': [('red', 'green', 8.2)]}
```

The threshold is a heuristic (dE 15), not a standards-body value. Tighten it for
large filled areas, loosen it for thick lines.

## D. Composition

**D1. Identify the message before choosing the chart.** Know who reads it, decide
the one thing the figure must convey, pick the chart from the data's shape, and
do not trust library defaults - they are tuned for screen exploration, not for
a printed column. *(Rougier, Droettboom & Bourne 2014.)*

**D2. Audit against the known pitfalls** - truncated or dual axes that exaggerate
an effect, missing axis labels or units, inconsistent scales across panels that
invite a false comparison, overplotting that hides density. *(Nguyen et al.
2021.)*

## E. Venue specifications are looked up, never recalled

Column widths, minimum resolution, accepted file formats, font and minimum point
size are venue-specific and they change. **Do not take them from memory or from
this file.** Read the target's current author guidelines before export:

- PLOS — <https://journals.plos.org/plosbiology/s/figures>
- Nature portfolio — <https://www.nature.com/ncb/submission-guidelines/aip-and-formatting>

If no venue is named, the deliverable still needs a stated physical width and a
stated dpi, because a figure sized for a slide is not a figure sized for a
column.

## F. This repo's conventions

1. **A figure is not finished until it is in `figures/`.** Save it as part of the
   step that produced it and list the directory so it is visibly there. A
   session artifact or scratch path does not count. *(CLAUDE.md, Data rules.)*
2. **Seed anything stochastic** - jitter, subsampling, layout initialisation -
   from `configs/params.yaml`, so the figure is byte-reproducible.
3. **Every figure gets a plain-language explanation beside it**: what is on each
   axis, where to look, what the pattern means, and what it does *not* mean.
   Expand jargon on first use. *(CLAUDE.md, Reporting.)*
4. **Every figure is regenerable** from a numbered pipeline step, with the
   parameters that produced it recorded.

## Pre-flight checklist

Before saving a figure that ships:

1. Is any continuous outcome drawn as a bar? If yes, can the reader see the
   distribution? (A1)
2. Is every error bar defined, with n stated? (A2)
3. Is the plotted unit the unit that was analysed? (A3)
4. Could any comparison move from colour or area onto a common position scale? (B1)
5. Does `cvd_check()` pass on the palette, and does every distinction survive
   greyscale? (C1, C2)
6. Is every continuous map perceptually uniform, and every diverging map centred
   on its semantic zero? (C3, C4)
7. Does any axis start somewhere other than zero without saying so? (D2)
8. Width and dpi set deliberately, against the venue's current spec? (E)
9. Did it land in `figures/`, and did you list the directory? (F1)

## Sources

DOIs below resolved against PubMed E-utilities and Crossref.

| # | Source | DOI |
|---|---|---|
| Weissgerber 2015 | Beyond bar and line graphs: time for a new data presentation paradigm. *PLoS Biol* 13:e1002128 | 10.1371/journal.pbio.1002128 |
| Nat Methods 2014 | Kick the bar chart habit (editorial). *Nat Methods* 11:113 | 10.1038/nmeth.2837 |
| Streit 2014 | Bar charts and box plots. *Nat Methods* 11:117 | 10.1038/nmeth.2807 |
| Cumming 2007 | Error bars in experimental biology. *J Cell Biol* 177:7-11 | 10.1083/jcb.200611141 |
| Lord 2020 | SuperPlots: communicating reproducibility and variability in cell biology. *J Cell Biol* 219 | 10.1083/jcb.202001064 |
| Cleveland 1984 | Graphical perception: theory, experimentation, and application. *JASA* 79:531-554 | 10.1080/01621459.1984.10478080 |
| McColeman 2022 | Rethinking the ranks of visual channels. *IEEE TVCG* | 10.1109/TVCG.2021.3114684 |
| Rougier 2014 | Ten simple rules for better figures. *PLoS Comput Biol* | 10.1371/journal.pcbi.1003833 |
| Nguyen 2021 | Examining data visualization pitfalls in scientific publications. *Vis Comput Ind Biomed Art* | 10.1186/s42492-021-00092-y |
| Wong 2011a | Points of view: Color blindness. *Nat Methods* 8:441 | 10.1038/nmeth.1618 |
| Wong 2011b | Points of view: Avoiding color. *Nat Methods* | 10.1038/nmeth.1642 |
| Crameri 2020 | The misuse of colour in science communication. *Nat Commun* | 10.1038/s41467-020-19160-7 |
| Borland 2007 | Rainbow color map (still) considered harmful. *IEEE CG&A* | 10.1109/mcg.2007.323435 |
| Ware 2023 | Rainbow colormaps are not all bad. *IEEE CG&A* | 10.1109/MCG.2023.3246111 |

Okabe M & Ito K, "Color Universal Design", is a web resource, not a DOI-indexed
paper; the palette hex values ship in `kernel.py` as `OKABE_ITO`.

## Helpers

Loading this skill defines:

- `okabe_ito(n=8, include_black=True)` - the colour-universal-design palette.
- `cvd_check(colors, kind="deuteranopia", delta_e_threshold=15.0, labels=None)` -
  Vienot/Brettel/Mollon dichromat simulation plus pairwise CIE76 dE; returns
  `ok`, `min_delta_e`, `confusable` and the simulated hex values.

`figure-style` supplies the rest: `apply_figure_style`, `focal_palette`,
`bar_with_points`, `strip_with_median`, `end_of_line_labels`, `panel_letter`,
`set_frame`, `goodness_arrow`, `panel_crops`.
