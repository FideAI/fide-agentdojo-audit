# Release-candidate qualification

The combined standalone repository was checked on October 2, 2026 (America/Los_Angeles). [Exact results](QUALIFICATION.json) distinguish the unchanged archive subpackage from the newly portable compatibility experiment.

- A new Python 3.11 environment installed all 70 pinned dependencies; a fresh public fetch acquired the exact upstream commit.
- Original and amended full archive reruns each matched all 7,400 cohort hashes, 200 selected hashes and four projected tables, with native and amendment controls passing.
- The portable compatibility experiment matched all twelve projected output files, the source diff, 892 selected entries per arm, all six utility observations and expected failed blanket-repair gates. All 100 source files remained unchanged.
- Both charts regenerated in PNG, SVG and PDF in a separate fresh rendering environment.
- Offline verification checks explicit release hashes, archive sealing, derived compatibility relations, local link destinations and sensitive-string patterns.

The dependency lock specifies versions, not wheel hashes. Same-host caches were used. Cross-platform execution, historical runtime identity, independent human review and broad semantic repair correctness are not qualified. Checks do not approve publication.

A clean local Git clone with another new Python environment also reproduced the full original archive analysis and all compatibility results, leaving the checkout unchanged. It used the documented `--source` option to reuse the already acquired public source checkout. Exact tested commit and results are recorded in QUALIFICATION.json. Subsequent qualification-documentation and link-validator updates do not alter the scientific executables.

The [evidence-navigation additions](docs/EVIDENCE-GUIDE.md) were checked against both existing full archive runs. All four minimized projections matched, and the worked record matched its sealed source hash. Its match sets and evaluator outcomes also agreed with the separately authored AI review. The release verifier now checks these projections against the sealed count inputs and the reported control relationships. No sealed archive file or experimental algorithm changed.
