# A real case and a metadata repair example

This example accompanies a review of the student bundle at commit
`5ee23c5ee76394233b26c89c1ebd9acae7328aa0` and the public Hugging Face review
subset at revision `aabcff2e1492df35f0aaa9abef657133fffe9b81`.
The existing repository's synthetic teaching workflow remains a separate example.

## Start with the notebook

[Oracle Atlas Colab example](../../notebooks/Oracle_Atlas_Colab_Example.ipynb)
walks through all eight parts using **one real UMA case**. It clones the exact
public student commit and uses the student's unchanged acquisition, processing,
analysis and case-validation code. Seven source files reconstruct five transactions,
nine protocol events, eight transfers and one economic episode.
Expected decomposition: **1,000 USDC.e gross = 750 returned principal + 250 token gain**.
This does not establish total economic profit or external factual truth.

Setup uses [`colab_bootstrap.py`](colab_bootstrap.py), embedded verbatim in the
notebook's first code cell. It installs `uv==0.12.19` into a temporary directory,
creates an isolated Python 3.12 environment, installs the pinned scientific
dependencies, runs `pip check`, and records both the host and scientific Python.
It avoids calling the host interpreter's `venv`/`ensurepip`. If Colab changes its
host minor version, uv obtains a compatible managed interpreter. Setup requires
internet; a Google account is needed for a hosted Colab runtime. No wallet,
API key, paid RPC service or GPU is needed for bundled replay.
Managed-interpreter downloads have not been tested on every future Colab image.

Run all cells from a fresh CPU runtime. The final ZIP includes **both** repeat
runs and setup/environment evidence. The repeated run uses the same code and
inputs; it is a determinism check, not independent human review.

Local fallback:

```bash
python -m pip install ipython==9.17.1
python examples/oracle_review/execute_example.py --report runs/example-execution.json
```

Both the student notebook and the corrected example were executed as nine exact
code cells in fresh Python processes. Their tests and case checks passed. A socket-based
Jupyter kernel could not start in the audit host; hosted Colab also required
Google sign-in. Neither limitation is counted as a scientific-code failure,
and this example is **not claimed to have passed hosted Google Colab**.

## Croissant example

[`croissant.corrected-example.json`](croissant.corrected-example.json) describes
the **existing 15-table review subset**, not the unpublished full cross-protocol
ledger. It preserves the upstream field definitions and Responsible AI text,
repairs JSON-LD context bindings, pins the file URLs, fixes one Boolean type,
declares both the IANA and loader-supported Parquet MIME types, and adds a
bounded provenance example. Authors must verify and expand the lineage for every contributed table, annotation and activity before submission.
This file is a teaching example, not a signed provenance attestation.

The original custom file failed `mlcroissant==1.1.0`: its bare `name`, `license`
and other properties were not bound by its context. Visible JSON keys do not
guarantee valid machine-readable metadata. The platform-generated endpoint
parsed, but supplied no minimal RAI/provenance fields. It also documents skipped
all-null columns; the custom metadata retains the full physical schemas.

To test against an authorized local copy of the pinned Hugging Face revision:

```bash
python -m venv .metadata-env
.metadata-env/bin/python -m pip install -r examples/oracle_review/requirements-metadata.txt
.metadata-env/bin/python examples/oracle_review/audit_croissant.py \
  --metadata examples/oracle_review/croissant.corrected-example.json \
  --data-root /path/to/pinned-huggingface-copy \
  --report runs/croissant-review.json
```

Without a data root or the loader, file/access checks are **not evaluated** and
the command cannot report a complete pass. This helper checks the minimal
profile and exact file/schema access; the
[NeurIPS validator](https://neurips.cc/Conferences/2026/EvaluationsDatasetsHosting)
and scientific review remain separate steps.

## What students must still deliver

1. Fix and revalidate the documented full-core/application semantic and schema
   issues, preserving a versioned change log and before/after counts.
2. Deposit the exact full inputs/outputs or explicitly narrow the manuscript's
   described resource to an accessible, validated release. The small example
   cannot substitute for the full resource.
3. Supply a result-to-command map, complete field dictionary, source/rights
   registry, historical state bundles, and measured full-run resources.
4. Run the revised notebook in a fresh **Google-hosted** runtime and save its
   full traceback on failure, or executed notebook, environment and ZIP on success.
5. Author-review all RAI/provenance statements; validate the exact submitted
   metadata against the exact deposited data. Keep the filled metadata file
   distinct from the automatically generated core-only endpoint.
6. Have a scholar unfamiliar with the project follow the tutorial and record
   interventions and questions. Software success is not human review.

## Standards and attribution

- [Scientific Data submission guidance](https://www.nature.com/sdata/submission-guidelines)
  requires an accessible described dataset and evidence in Technical Validation;
  its Usage Notes are practical access/reuse guidance.
- [NeurIPS 2026 E&D hosting guidance](https://neurips.cc/Conferences/2026/EvaluationsDatasetsHosting)
  requires core plus minimal RAI Croissant metadata and validation. For a future
  submission, check the applicable year's rules again.
- [NeurIPS E&D scope](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets)
  also asks what evaluative claims the dataset supports and under which assumptions.
- [MLCommons specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html)
  defines JSON-LD bindings and source/field semantics.
- [Hugging Face Croissant documentation](https://huggingface.co/docs/dataset-viewer/croissant)
  explains the generated core endpoint and its constraints.

New helper code is covered by the repository MIT license. The notebook's
scientific stages adapt the student's MIT-licensed public tutorial at the
pinned commit. The original metadata is CC BY 4.0, Oracle-Nature contributors,
from the pinned dataset revision; the corrected example retains that license.
Downloaded UMA contract sources retain their upstream AGPL-3.0-only notices.
No private manuscript content or unpublished dataset is included here.
