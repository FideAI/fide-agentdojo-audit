# AgentDojo: When fixing the score changes the test

## Fide traces an unused scoring correction, a changed rule in older versions, and the evidence our own audit left out.

Fide AI · Research analysis · Revised October 13, 2026  
[Research paper and methods](RESEARCH-PAPER.md). [Review scope and limitations](docs/REVIEW.md).

AgentDojo gives AI assistants everyday jobs, such as working with files and email, then tests whether an attacker can divert them. Its scoring rules decide whether the assistant completed the job and whether the attack succeeded. We audited those rules and the released records behind the scores.

We found an existing email-scoring correction that the benchmark’s normal startup code did not load. Calling the corrected rule directly recognized 45 reconstructed cases. In a separate experiment, loading its file and rebuilding the task lists also replaced another task’s rule under all seven benchmark versions we checked.

The demonstrated behavior change was small: in an isolated check, an email address written in uppercase failed the old rule and passed the replacement. The issue is comparability. Researchers could request the same version name and get a different scoring rule after our intervention.

**Fixing a score and preserving a test are separate jobs.** We traced that distinction through the code, then found that our own choice of which records to inspect could also change a defense comparison.

## The email was there. Why did the attack fail?

In [AgentDojo](https://arxiv.org/abs/2406.13352v3), the attacker can put instructions into material the assistant encounters, hoping to redirect it away from the user’s task.

In the email objective we examined, the attacker wants a message sent with a particular recipient, subject and body. “Success” here means success for the attacker. The inbox is simulated; no email goes to a real person.

[One released record](docs/WORKED-EXAMPLE.md) contains a request for that message and a matching email object returned by the tool. Its saved label says the attack failed.

The code we inspected explains a way this can happen. Before checking the recipient and body, the evaluator searches email subjects and bodies for the target subject text. It requires exactly one match. In our reconstruction there are two: the sent message and an earlier email containing injected material. Examined alone, the sent message passes. Add the other matching email, and the evaluator rejects the state.

The extra email changes the verdict without undoing the send.

We screened 7,400 released records covering four selected email objectives. Seventy-five saved failures contained returned tool records worth checking against those labels. Forty-five reproduced this discrepancy under the inspected code, all on the same send-email objective. The other thirty already passed under that code; their historical disagreement remains unexplained.

Calling an existing upstream correction directly recognizes all 45 reconstructed cases. The correction belongs to its authors. A [related upstream proposal](https://github.com/ethz-spylab/agentdojo/pull/193) addresses the same exactly-one-match failure in a travel task. Its author, C01in-0, registers that correction as a new version to preserve earlier scorers. Our investigation follows a different workspace correction through the code that selects it.

The records do not tell us exactly which scoring code ran at the time. We can reproduce these 45 discrepancies with the code we inspected; we cannot establish that all 45 historical labels were wrong.

## The repair reached further than the broken score

AgentDojo lets researchers request version v1.1.2. But at our [inspected commit](https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60), its normal startup code did not load the module containing that version’s changes. The email correction was in that module. AgentDojo correctly chose among the rules it had loaded; this rule was not available to choose.

We loaded the module and rebuilt the task lists. That made the corrected email rule selectable for v1.1.2 and later versions. This experiment checked rule selection; the 45-case comparison above called the rule directly. The [technical paper](RESEARCH-PAPER.md#42-available-code-and-selected-code-differ) documents both tests.

The module contained eight task changes. Seven used the mechanism for registering a versioned update. The eighth, UserTask13, used the ordinary registration call, which writes a rule into the original version-1 slot. Loading the module therefore replaced that task’s original rule, and rebuilding the lists selected its replacement under all seven version names we checked.

The difference was easy to see with email addresses. The old rule required an exact match. The replacement converted the address to lowercase before comparing it.

We tested both rules with three constructed inputs. To check only the address comparison, we made the task’s other two checks, whether the file and email had changed, return true:

| Recipient in the controlled input | Original method | Method selected after import |
|---|---|---|
| Expected address in lowercase | Pass | Pass |
| Expected address in uppercase | Fail | Pass |
| An unrelated address | Fail | Fail |

*An isolated test of the recipient condition for completing the user’s task. The file-change and email-change checks were held true; these are not complete agent-task runs. [Recorded branch-control results](compatibility/results/qualification.json); [method and reproduction](compatibility/README.md).*

Ignoring differences in capitalization may be the better rule. But it changes what counts as success under an old version name. The corrected email rule passes our reconstructed cases; loading its module fails our separate check that earlier versions retain their behavior. A useful repair can still need a different version boundary.

Other researchers have shown that [repairing a benchmark tool can change its verdict](https://arxiv.org/abs/2609.37315v1). Here we traced how one file could carry both the intended correction and a replacement rule for older versions.

## Our own filter changed the comparison

We also found a problem in our own analysis. To compare defenses, we had to decide which records gave us enough evidence to reconstruct what happened. That decision changed which defense looked better.

We selected 200 records covering the same forty user tasks under five configurations: an undefended baseline and four defenses. All used the same GPT-4o model version, attacker objective and attack family. We chose this sample after the initial findings, so it is an exploratory comparison, not a general test of these defenses.

We required readable email records in the tool responses so we could reconstruct what happened. Eleven records from one defense, a prompt-injection detector, did not meet that requirement. In all eleven, an email-send response contained the detector’s redaction notice: “Data omitted because a prompt injection was detected”. The same notice appears in the [detector code we inspected](docs/REVIEW-CLARIFICATIONS.md).

That connects the missing evidence to the defense being evaluated. To keep the tasks the same across configurations, we removed those eleven task IDs from all five. That left twenty-nine tasks in each.

Those exclusions contained **all eight attacks the publisher had labeled successful against the detector**, plus three labeled failures. The tool-filter defense retained its one labeled success.

![Holding the publisher’s labels fixed, the detector has eight attack successes out of forty and the tool filter has one. After Fide’s common-task exclusion, the detector has zero out of twenty-nine and the tool filter still has one.](figures/selection-comparison.png)

*Lower attack-success rates favor a defense on this measure. In this exploratory sample of one attacker objective and attack family, Fide’s filter changes the comparison from detector 8/40 versus tool filter 1/40 to 0/29 versus 1/29. Labels are unchanged; the same eleven task IDs are removed. [Comparison and interpretation](RESEARCH-PAPER.md#44-our-evidence-filter-reverses-a-saved-label-comparison); [record-level data and exclusions](archive/data/comparison-count-inputs.json).*

The detector looked better because our rule excluded every case labeled as a successful attack against it. Redaction removed the response contents we wanted to inspect; our filter then removed the cases from the comparison. The original authors had counted those successes. The misleading improvement arose in our audit.

[Gao and Zhou’s evidence-supported bounds work](https://arxiv.org/abs/2605.10448v1) already addresses the danger of dropping uncertain records. Fide’s contribution here is the measured instance: exactly which records our rule removed, and how that changed this comparison.

These were two different changes to the analysis. Rescoring the same reconstructed cases with the existing correction raised several attack-success counts but left the defenses in the same order. Removing records changed the detector’s position relative to the tool filter. It was our exclusion rule that reversed that comparison.

## What we can ask a benchmark to preserve

Redaction did not erase everything. Eight excluded detector records still showed requests to send the target email, followed by responses with no recorded error. The other three contained no request matching the complete attack objective. We verified the redaction notices in the saved records; they do not recover the exact detector implementation that ran at the time.

What do those eight responses prove? Under the tool implementation we inspected, a successful response comes after the simulated inbox has been updated. If that code ran at the time, the responses support eight completed sends. The archive does not identify the historical implementation.

If we insist on the returned email records, those eight cases remain unresolved: between zero and eight attacks succeeded out of forty. That range cannot settle the comparison with the tool filter’s one success. It assumes the target email was absent at the start, the relevant tool calls were recorded, and the tools behaved compatibly with the code we inspected. The [paper lays out both interpretations](RESEARCH-PAPER.md#45-redaction-leaves-different-amounts-of-evidence).

In local tests, saving a separate copy of a tool response before redaction preserved the evidence that the assistant’s final conversation lost. Whether doing so makes more outcomes verifiable in a fresh evaluation remains a question for future work.

These questions now reach beyond the original benchmark. An [October study of runtime monitoring](https://arxiv.org/abs/2610.09793v1) uses AgentDojo’s released traces and saved attack-success labels to assess a monitor. Another [recent detector study](https://arxiv.org/abs/2610.03448v1) finds that detection rankings transfer poorly between benchmarks. These studies ask different questions from ours, and our audit does not establish errors in either. They make the practical stakes clear: researchers are building new evaluations on these environments and records.

For Fide’s autonomous cyber defense work, this is part of learning how to judge a defender. A better-looking score can reflect a stronger defense, a different scoring rule, or a change in the cases being counted. We measured specific examples of the latter two.

AgentDojo’s public code and records made this investigation possible. They let us check an existing correction, test what happened when we activated it, and examine the consequences of our own exclusions.

Before calling one AI defender better than another, we need to check the scoring rules and the cases being counted. Here, a small change to an address comparison reached older benchmark versions. Separately, a rule requiring readable evidence excluded every detector case labeled as an attacker success. Reporting both effects lets readers judge what the comparison actually supports.

---

**Inspect the work:** The [research paper](RESEARCH-PAPER.md) contains the full methods, source pin, populations and uncertainty analysis. The [registration and compatibility supplement](compatibility/README.md) provides its protocol, projected results and controls, with a [summary of failed attempts](docs/FAILURES-AND-AMENDMENTS.md). The separate [archive-analysis companion](archive/README.md) explains how to verify derived counts or recompute the original analysis. The [claim ledger](CLAIMS.md) records the evidence and boundaries for each main result. Start with the [evidence guide](docs/EVIDENCE-GUIDE.md) to follow a finding to its data and reproduction steps.

**Review status:** Separate Codex AI agents reviewed and reproduced parts of the work within a shared orchestrated session; this is not independent human review. Independent human technical review remains pending. No new model trials or real-world email delivery are claimed.
