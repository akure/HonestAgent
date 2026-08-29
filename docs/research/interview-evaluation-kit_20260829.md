# HonestAgent Customer Interview Evaluation Kit

**Purpose:** Validate the problem, workflow, adoption requirements, and pilot value with target users before hackathon submission.  
**Status:** Ready for real interviews; synthetic rehearsal is documented separately.  
**Evidence rule:** Do not convert this kit into customer evidence until real participants provide consent and the interview is completed.

## 1. Participant profile

Recruit people who own, operate, secure, or approve AI-agent workflows with meaningful tool side effects. Prefer at least three participants across different organizations or independent teams.

| Participant ID | Role category | Workflow category | Interview date | Consent status | Publication permission |
|---|---|---|---|---|---|
| `P__` | Platform / Security / SRE / Operations / Data | Finance / Support / Deploy / Data / Other | `YYYY-MM-DD` | Pending | Pending |

Do not record names, employers, customer names, credentials, personal data, regulated records, or confidential architecture in the public evidence file.

## 2. Invitation message

```text
Subject: 30-minute research interview about AI-agent action safety

Hello,

I am researching how teams control AI agents before they perform consequential
actions such as sending messages, changing records, deploying software, issuing
refunds, or spending money. I would like to understand your current workflow,
approval process, failure modes, and evidence requirements.

This is voluntary product research, not a sales commitment. Please do not share
confidential, personal, regulated, customer, credential, or proprietary information.
We can use anonymous notes only. The interview takes approximately 30 minutes.

Would you be willing to participate under those conditions?
```

## 3. Consent opening

Read this before taking notes:

```text
This discussion is voluntary and may be stopped at any time. Please do not share
confidential, personal, regulated, customer, credential, or proprietary information.
I will record only sanitized notes under an anonymous participant ID unless you give
separate permission for recording or an anonymized quotation. You may review or
withdraw your material before synthesis. The results will be used to validate a
problem statement and evaluation plan, not to claim that your organization endorses
HonestAgent.

Do you consent to anonymous note-taking for this research?  Yes / No
May we use an anonymized quotation after you review it?       Yes / No
May we record audio/video?                                    Yes / No
```

If consent is not given, stop the interview or continue without retaining notes, according to the participant’s preference.

## 4. Moderator instructions

Ask about the current process before showing HonestAgent. Do not lead the participant toward agreement, ask them to praise the product, or describe a hypothetical answer as an observed fact. Separate direct participant statements from interviewer interpretation. Ask for ranges or categories instead of sensitive numbers. If confidential information is volunteered, stop note-taking, ask the participant to restate using a generic example, and redact the original immediately.

Use a synthetic demonstration only after the problem section. The demonstration should show one read-only action, one consequential action that pauses, one reviewer approval, and one invalid or replayed handoff that is blocked. Do not connect the demo to a live provider or real executor.

## 5. Interview questions

### Current workflow

1. What AI agent, automation, or tool-calling workflow do you own or review?
2. What systems can it read from or change?
3. Which actions are externally visible, difficult to reverse, or financially/materially consequential?
4. Walk me through the last time one of those actions needed human approval.
5. Where is the approval decision recorded today?

### Failure modes and evidence

6. What can go wrong between the agent proposing an action and the executor performing it?
7. How do you handle stale approvals, duplicate requests, changed arguments, replay, or provider timeouts?
8. What evidence would a security, audit, or compliance reviewer need before allowing this workflow in production?
9. How do you prove that a blocked action never reached the executor?
10. What is the cost of a false allow? What is the cost of a false block?

### Adoption and fit

11. Which integration boundary would be easiest for your team: SDK, HTTP service, MCP, or another boundary?
12. Who should own the reviewer queue, policy changes, audit retention, and emergency disable procedure?
13. What would make a two-week pilot for one workflow useful?
14. What would prevent adoption even if the control worked as described?
15. Which part of this approach is least valuable or least credible?

### After the demonstration

16. What changed, if anything, in your view of the problem?
17. Which action would you pilot first, and what would the acceptance test be?
18. What deployment, identity, data, or latency requirement did we fail to address?
19. Would you be willing to review a sanitized pilot proposal? This is not a purchase commitment.
20. May I read back a short anonymized summary for accuracy?

## 6. Structured note form

```text
Participant ID: P__
Role category: __
Organization identifier: do not publish; keep private or omit
Consent: anonymous notes yes/no; quotation yes/no; recording yes/no
Relevant workflow: __
Systems/tools involved: generic description only
Consequential actions: __
Current approval process: __
Observed or personally experienced failure mode: __
Current evidence/audit requirement: __
False-allow cost category: low / medium / high / unknown
False-block cost category: low / medium / high / unknown
Preferred integration boundary: __
Likely pilot workflow: __
Adoption blocker: __
Disconfirming signal: __
Direct quote approved for publication: yes/no/not requested
Participant correction requested: yes/no
Researcher interpretation: __
Sanitization check complete: yes/no
```

## 7. Evaluation scorecard

Score each dimension from 0 to 2 using the participant’s own evidence, not enthusiasm:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Concrete bottleneck | No relevant bottleneck | General concern | Specific current failure or costly manual step |
| Consequence | No meaningful side effect | Potential side effect | Clearly irreversible, externally visible, or material action |
| Existing control gap | No gap | Informal or partial control | Clear inability to prove pre-execution authorization |
| Evidence need | Unknown | General audit concern | Specific required evidence or reviewer workflow |
| Pilot fit | No candidate workflow | Possible workflow | Named workflow and acceptance test |
| Adoption readiness | No interest or strong blocker | Conditional | Clear next step subject to stated requirements |
| Disconfirming insight | None captured | Weak objection | Specific reason the product may not fit |

Do not add scores across participants to claim product-market fit. Use the scorecard to compare evidence quality and identify which assumptions remain untested.

## 8. Synthesis template

After interviews, complete this table without names or identifying details:

| Theme | Participants supporting | Direct evidence | Confidence | Product implication |
|---|---:|---|---|---|
| Pre-execution approval bottleneck | `__/__` | Sanitized paraphrases or approved quotes | Low/Med/High | __ |
| Stale/replayed/mismatched approval risk | `__/__` | __ | Low/Med/High | __ |
| Audit evidence requirement | `__/__` | __ | Low/Med/High | __ |
| Preferred integration surface | `__/__` | __ | Low/Med/High | __ |
| Latency or review-burden objection | `__/__` | __ | Low/Med/High | __ |
| Adoption blocker | `__/__` | __ | Low/Med/High | __ |
| Disconfirming signal | `__/__` | __ | Low/Med/High | __ |

The final synthesis must state the number and role mix of participants, repeated observations, disagreements, adoption blockers, disconfirming signals, and what the interviews did not establish. It must not claim customer endorsement, willingness to pay, product-market fit, or production readiness without direct evidence.

## 9. Publication checklist

Before committing an anonymized synthesis:

- [ ] Each participant gave consent for anonymous notes.
- [ ] Any quote has separate permission and participant review.
- [ ] Names, employers, customer references, contact details, PII, credentials, and confidential details are removed.
- [ ] Raw recordings and notes remain outside the public repository.
- [ ] Synthetic rehearsal personas are not mixed with real participant evidence.
- [ ] At least one adoption blocker and one disconfirming signal are included.
- [ ] The README problem statement matches the evidence.
- [ ] No willingness-to-pay or product-market-fit claim exceeds the evidence.
- [ ] The evidence file identifies the date, method, participant count, and limitations.

## 10. Hackathon evidence classification

- **Real interview evidence:** consented, anonymized, relevant participant interviews meeting the checklist above.
- **Synthetic rehearsal:** useful for preparation only; not a customer signal.
- **Sales conversation:** not automatically research evidence; separate discovery, sales, and validation claims.
- **Demo reaction:** not evidence of a current operational bottleneck unless the participant independently describes that bottleneck first.
