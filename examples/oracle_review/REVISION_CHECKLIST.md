# Close the gap between claims and deposited artifacts

Use this checklist with the corrected notebook and Croissant example. A small
working case is useful evidence for that case. It does not validate the full
cross-protocol archive or every downstream interpretation.

| Artifact | Required revision | Evidence to return |
| --- | --- | --- |
| Manuscript | Match every count, schema assertion, validation statement and availability claim to the exact deposited release. Complete practical Usage Notes. | A claim-to-file-to-command matrix and a clean compiled draft. |
| Full data release | Deposit the described resource and its source/rights registry, field dictionary, checksums, collection boundaries and historical state. | Immutable revision, download links, before/after counts and a release manifest. |
| Scientific code | Resolve the known UMA, Tellor, DVM, enumeration and checksum issues in the student's issue log; regenerate affected views. | Versioned fixes, meaningful regression checks and measured full-run logs. |
| Colab notebook | Run all cells on a fresh Google-hosted CPU runtime. Record the host and isolated scientific environment. | Executed notebook, full traceback if it fails, environment record and ZIP containing both repeat runs. |
| Dataset Card | Describe every actual configuration, its observation unit, source lineage, missing/censored values, permitted uses and evaluation boundaries. | Counts and types agreeing with deposited files and Croissant. |
| Croissant metadata | Bind JSON-LD terms, supply core plus all eight minimal RAI/provenance fields, use stable file identities and correct physical types. | NeurIPS-linked validator report and actual data-access/schema checks for the exact submitted file. |
| Human review | Ask a reader unfamiliar with the project to follow the instructions and separately evaluate paper, code and dataset. | Completed assessments, recorded interventions and a point-by-point response. |

For each issue, return its ID, affected file(s), commit or dataset revision,
command, expected result, observed result, evidence link, and remaining blocker.
Do not clear an issue by changing an expected checksum, hiding a failing check,
or repeating an unsupported claim in another artifact. Preserve prior versions.

Keep configured, accrued, claimable and realized outcomes distinct. Preserve
right censoring and distinguish zero, missing, unknown and not applicable.
Protocol adjudication is not independent external factual truth; wallet
addresses are not verified real-world identities. Gross receipts are not total
net economic profit. Evaluation claims need evidence appropriate to the
construct and split, not only a successful file load.

An author-approved change in the scientific scope requires corresponding changes
throughout the paper, data release, code, tutorial and metadata. Merely weakening
one availability sentence does not resolve missing data or incorrect semantics.

The examples' validation receipt explicitly separates local execution from
hosted Colab execution, metadata format/access checks from scientific validity,
and deterministic repetition from independent human review.
