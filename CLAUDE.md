# CLAUDE.md: Project rules for Claude Science

This repo is a reproducible-analysis project. At the start of every session read this file and
`README.md`, then load the domain-method skill for the work at hand — README lists what is
vendored under `skills/`; for single-cell work it is `scrnaseq-pipeline`. The rules below cover
how work is recorded, verified, gated and reported here, whatever the domain; the analysis
method itself lives in the skill. Follow both.

## Notebook-style working
- Work in notebooks in `workflows/` (Quarto `.qmd`, R Markdown `.Rmd`, or Jupyter `.ipynb`).
- One small step per chunk. Before each chunk, write 1-2 sentences saying what it does and why.
- Every chunk must produce a visible output I can verify: a table, printed dimensions, or a plot.
- After each chunk or stage, state briefly what the output shows and flag anything unexpected.
- Do not skip ahead. Finish and show one stage before starting the next.
- Notebooks must run top to bottom on a clean session.

## Reproducibility
- Set one global random seed (from `configs/params.yaml`) at the top of every notebook.
- Put all thresholds and parameters in `configs/params.yaml`, not hard-coded in chunks.
- End every notebook with a session-info chunk (`sessionInfo()` or package versions).
- Use relative paths from the repo root. No absolute paths like `C:\Users\...`.
- Record every package install in `environment/` (renv snapshot or environment.yml).

## Data rules
- Never modify or overwrite anything in `data/raw/`.
- Write intermediates to `data/processed/`, tables to `results/`, plots to `figures/`.
- **A deliverable is not finished until it is in its directory, and I want to see that it
  landed.** Save the figure or table into its folder as part of the step that produced it,
  not "later", and end the step by listing that directory so the file is visible. A session
  artifact, a scratch-workspace file or a temp path does not satisfy this: if it is not in
  `figures/`, `results/` or `data/processed/`, it does not exist as far as this repo is
  concerned, and anyone cloning the repo cannot follow the analysis.
- Running the work in a scratch workspace is fine and often sensible. Treating the scratch
  workspace as the *destination* is the mistake. Keeping the repo free of unwanted
  machinery — scripts, configs, environments — is a different request from withholding the
  outputs; do not confuse the two.
- Check the output directories at the **first** step boundary, not the last. Three empty
  directories at step 2 is a two-second fix; at step 13 it is a silent inconsistency in
  everything already written.
- Document the source of every dataset in `data/metadata/DATA_SOURCES.md`.
- Do not commit large data files (see `.gitignore`).

## Git rules
- Do not commit or push unless I ask. When asked, use a clear message describing the stage
  (for example `Add step 6 filtering; thresholds in configs/params.yaml`).
- Never commit secrets, tokens, or `.env` files.
- Never rewrite history (no force-push) without asking.

## Reporting
- At the end of the session, write the analysis log entry specified in `README.md`: one new
  Markdown file in `Analysis Logs/`, named by date and topic, never overwriting an earlier one.
- Be explicit about uncertainty. If a result looks off (odd cell counts, batch effects), say so
  rather than smoothing over it.

- **After every numbered step of the analysis, give me a short summary in the response:
  one to two paragraphs saying what was done and how it was verified.** Not a bullet list of
  commands. Say what the step produced, what the check was, and what the check would have
  caught had it failed.
- **If a step produces a graph, show the graph with that summary.** Distributions,
  projections, heatmaps and the like are shown inline, not merely described or saved
  to a path. A step whose output is visual is not reported until I can see it.
- Flag anything unexpected in the same summary rather than in a later step.
- **Stop after each numbered analysis step and wait for my approval before starting the next.**
  Do not chain steps together, even when the next one is quick, cheap or obvious. Steps 7, 8 and
  9 are three stops, not one. If a step turns out to need an unplanned sub-step, that is another
  stop. End each summary by naming what the next step will be, what it needs from me, and any
  decision I have to make before it can run.
- **Every figure gets a plain-language explanation next to it.** Say what is on each axis, where
  to look, what the pattern means, and — just as important — what it does *not* mean. Expand
  jargon on first use: name the term, say in one clause what it is, and say why this step uses
  it, rather than leaving the convention to be inferred.
  Assume I know the biology but not this pipeline's conventions. A figure I would have to ask you
  to interpret is not a finished figure.

## Verification
- **Every verification must be visible to me.** Do not describe a result as checked,
  confirmed, verified or validated unless the check itself and its real output appear in the
  response. If I cannot see the check, it did not happen as far as I am concerned.
- **Show the check, not a summary of it.** Give the code or command you ran and the actual
  output it produced. "Checksums match" is not a verification; the expected and observed
  digests side by side is.
- **State what would have counted as a failure**, before or alongside the result, so I can
  tell whether the check could have failed at all. A check that cannot fail is not a check.
- **Label every number as measured or quoted.** If a figure comes from a paper, a database
  page, or your own recall rather than from a computation run in this session, say so
  explicitly. Never present a remembered value as a measurement.
- **Prefer checks against an invariant the data must satisfy.** Example: TPM columns must sum
  to 1e6, and testing that is how you find out a matrix is already log-transformed rather
  than linear TPM. A check that only restates what the code did proves nothing.
- **Read results back from the saved file before quoting them.** Do not re-type numbers from
  memory or from an earlier cell's output.
- **When a check fails, or an earlier claim turns out to be wrong, say so plainly and correct
  the record in the same response.** Do not quietly drop it or restate it as if it had always
  been right.

## Installs and new machinery
- **Ask me before installing anything.** That includes conda or pip packages, creating a new
  conda environment, and building environments from the specs in `environment/`. Say what you
  want to install, why this step needs it, and what fails without it. Then wait for my answer.
- **Ask me before adding machinery to the repo.** A new script in `src/`, a new config block,
  a new notebook, a wrapper, a helper module, an abstraction. Default to doing the step in the
  session and showing me the output first; write the file only once the step works and I have
  agreed it is worth keeping.
- **Do not build a reusable helper for something done once.** One concrete step beats a
  framework. If a step is repeated later, that is when it becomes a function.
- Reading and running code in the session needs no approval. Only installs and new files do.

## Agents
Agent definitions, if any, live in `.claude/agents/`. **The directory is currently empty** —
nothing is defined there, so do not assume a reviewer or writer agent exists. If a role is
worth keeping, propose it first and write the definition only once I agree. Roles that have
come up but are not implemented:
- `qc-reviewer`: checks QC thresholds and outputs before moving on.
- `methods-writer`: drafts methods and results text from the notebooks.
