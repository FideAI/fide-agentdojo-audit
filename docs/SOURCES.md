# Sources and attribution

AgentDojo source and released records are pinned to commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60`. Acquire them with `archive/acquire.py`; historical instructions are read as data, never executed. Its root MIT notice is retained in `LICENSES/AgentDojo-MIT.txt`. Public availability is not blanket permission to redistribute every raw record.

- [AgentDojo v3](https://arxiv.org/abs/2406.13352v3): original benchmark and source of the study environment.
- [Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks? v2](https://arxiv.org/abs/2510.05244v2): prior success-metric and benchmark-quality discussion.
- [Do Agent Benchmarks Do What They Say? v1](https://arxiv.org/abs/2609.37315v1): prior executable-contract audit.
- [Can Agent Benchmarks Support Their Scores? v1, Gao and Zhou](https://arxiv.org/abs/2605.10448v1): direct prior work on evidence-supported bounds and selection from dropping unknowns. Those methods are not claimed as Fide inventions.
- [AgentDojo PR 193](https://github.com/ethz-spylab/agentdojo/pull/193): multiple-match scoring, public-trace reconstruction and historical implementation qualifications.
- [AgentDojo PR 191](https://github.com/ethz-spylab/agentdojo/pull/191): stronger witnesses and version-preservation concerns.

The private research process retained full-text/source snapshots and exact acquisition records. Those snapshots are not redistributed here. This is a bounded source review, not a systematic search establishing priority. The existing correction belongs to upstream authors.

[Acquisition metadata](SOURCE-ACQUISITIONS.json) preserves exact URLs, retrieval times and content hashes without redistributing full texts.

## October 13 relevance refresh

- [Passing the Test You Trained On, Liu, v1](https://arxiv.org/abs/2610.03448v1): recent detector evaluation on replay-derived tool outputs; distinct from our record-exclusion comparison.
- [Formal Runtime Verification, Kekatos et al., v1](https://arxiv.org/abs/2610.09793v1): offline monitoring and trace requirements; a downstream use of saved AgentDojo labels, not a result we reproduced or corrected.

Targeted full-text methods/results/limitations review also revisited the contract audit’s constructed repair controls and Gao and Zhou’s evidence-selection framework. The specific registration/old-version compatibility result leads the revised paper. Broader benchmark-audit, evidence-bounds and logging ideas are credited prior work. At retrieval, upstream main still matched the study pin and PRs 191/193 were open and unmerged. Acquisition metadata records the dated check. No new experiments or claim of global priority resulted from this refresh.
