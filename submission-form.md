# Ceramic Tile Shade-Matching Case Study: Answers

## 1. The real problem, in two sentences

The client's real problem is that nobody can translate a measured colour and gloss difference into a specific change to the printer input, so every batch change becomes a slow, subjective cycle of editing, printing, firing and re-comparing while the line keeps producing. They asked for a faster comparison (6-7 hours down to 5-6 minutes), but a better comparison alone won't fix it, because their spectrophotometer already measures the difference. The missing piece is the mapping from that measurement to an input edit, and the kiln firing step is physical and cannot be compressed to 5-6 minutes.

---

## 2. The people in the deal

Procurement lead (my contact from the call): The cost is capped, and a paid $18,000 discovery phase is a go/no-go gate before the remaining $147,000. The value case is built on their own loss-per-m² figure, and I won't promise savings before we measure it.

Plant / production head (likely economic buyer) [assumption]: The goal is less off-shade production at batch changeover, with the line and batch release staying under their control.

Quality / lab head, owns master tile and tolerances [assumption]: Their tolerances govern everything. Nothing is released without a verified fired sample and human approval, and tolerances are never relaxed to force a pass.

Lab technicians / Photoshop operators, daily users [assumption]: It is a recommendation tool, not a replacement. They keep the final decision and their current workflow, with less trial and error.

Printer / process engineer [assumption]: We need the editable colour channels, safe adjustment limits, and a record of each change. Kiln and raw-material root causes are out of scope.

IT/OT and security [assumption]: Light footprint: file import/export, no printer write-back, no MES/ERP integration, and an audit trail.

---

## 3. Five questions for the next call, ranked

Ranked by how much each answer could change scope, price, or go/no-go.

**Question 1:** Do you have records pairing each printer-input change with the resulting fired-tile measurement, and can the exact image or settings be recorded?
- Why it matters: Decides whether the model learns from history or needs new controlled trials. This is the biggest swing in cost and schedule.
- Assumed meanwhile: No usable history, so I budget bounded calibration trials in Phase 2.

**Question 2:** What do "6-7 hours" and "5-6 minutes" each include? Is 6-7 hours one round or time to final approval, and does 5-6 minutes cover printing and firing?
- Why it matters: Defines the success metric and the baseline.
- Assumed meanwhile: 6-7 hours is one round, and 5-6 minutes means measurement-to-recommendation time only, because firing is a physical step.

**Question 3:** What are your numeric tolerances for L*, a*, b* and gloss, and how repeatable is your lab measurement?
- Why it matters: Without tolerances there is no definition of "match", and noisy measurement makes any model look wrong.
- Assumed meanwhile: Provisional tolerances are agreed with their quality team before testing, and measurement uncertainty must stay within 20% of the tolerance band.

**Question 4:** What does the 5,000-10,000 m² figure represent, what happens to that material (scrapped, downgraded, reworked, sold), and what does it cost you per m²?
- Why it matters: It is the whole value case, and the figure was unclear on the recording.
- Assumed meanwhile: It is exposure, not confirmed loss, and $5/m² is an illustrative placeholder only.

**Question 5:** How many SKUs, batch changes per year, and correction rounds per changeover do you have, and which printer controls can be edited?
- Why it matters: Sets pilot size, how fast we can collect baseline data, and the annual value.
- Assumed meanwhile: One printer, 3-5 pilot SKUs, and humans applying the edits in Photoshop.

---

## 4. Options considered and why this one

Standardised lab workflow: Keep as a prerequisite, not the answer. It improves repeatability but still leaves people guessing the image edit.

Camera / vision-only inspection: Ruled out as the primary approach. No evidence of stable lighting or production-grade imaging, and no proven link between image appearance and printer edits. Could return later as an extra check.

Calibrated decision support: CHOSEN. It uses measured colour and gloss plus past printer changes and results to recommend a small, bounded change, with a technician approving. It fills the exact gap: the lab measures the difference, but nobody knows how to turn it into an edit.

Fully automatic closed-loop printer control: Ruled out for now. No validated response data, confirmed printer integration, or safe limits. A wrong automatic edit could produce the wrong shade at production scale.

Root-cause optimisation (kiln, glaze, raw materials): Deferred. The client calls it a separate, harder problem, and the process data doesn't exist yet.

---

## 5. How the client will know the pilot worked

Baseline: At least 20 consecutive batch starts on the current manual process, recording rounds, active labour minutes, waiting and firing time, area produced before approval, and what happened to that material.

Final shade conformance: At least 90% meet every colour and gloss limit, and no worse than baseline.

Applied recommendations that improve: At least 80% reduce colour error without breaking another limit.

Correction rounds: Median at least 50% lower than baseline.

Active operator minutes per batch start: Median at least 30% lower than baseline.

Decision latency (measurement to recommendation): 90th percentile at or below 6 minutes.

Releases without verification and approval: Zero.

(All thresholds are proposed; the client's quality and production owners approve them before testing.)

Runs: Baseline, then shadow mode (recommendations logged, not used), then human-approved assisted mode on separate batches. Test on whole batches not used for training, split by batch or time, never by individual readings. With about 20 cases, percentages are directional, not proof.

Who measures: The client's lab takes the readings and the quality owner signs off. We analyse the data, and finance confirms the disposition of off-shade material.

Stop or pause if:
- Measurement uncertainty exceeds 20% of the tolerance band.
- Any batch is released without verification and approval.
- A recommendation causes an unreviewed out-of-limit result.
- Two model-guided corrections fail on one sample (that case reverts to the manual process).
- Gates are missed on held-out batches.

---

## 6. Cost to the client, cost to us, and value

Pricing structure: Fixed-scope pilot with a paid discovery gate and milestone payments. Phase 0 is $18,000. After it, either side can stop, or the client authorises the remaining $147,000 on an updated scope. Each later phase is billed 50% at start and 50% at its exit milestone.

Client cost, implementation: $18,000 + $25,000 + $56,000 + $47,000 + $19,000 = $165,000 (range $140,000-$190,000).

Client cost, running: $300-1,200/month hosting + $2,000-5,000/month support = $2,300-6,200/month, or $27,600-74,400/year.

Client cost, year one at $3,000 per month: $165,000 + $36,000 = $201,000.

Optional hardware, not included: $5,000-25,000 one-time.

Our cost, effort: 169-217 person-days.

Our cost per day: Not in the notes. Use your real rate.

Our cost, illustration at an assumed $500 per day: About $84,500-108,500, a gross margin of roughly 34-49% on $165,000.

Client value, formula: Net annual benefit = avoided off-shade loss + labour capacity released - recurring cost. Avoided loss = batches per year x exposed m² x preventable share x net avoidable loss per m².

Client value, illustration at 50% prevention and $5 per m²: $12,500-25,000 saved per correction interval.

Client value, year-one break-even: About 40,200 m² recovered, or 9-17 correction intervals. At $2/m² it needs 100,500 m², and at $10/m² it needs 20,100 m².

Caveat: Not an ROI claim until we have the client's real volume, loss per m² and labour hours. Labour can't be priced yet, because 6-7 hours is elapsed time, not active person-hours.

---

## 7. Timeline

First result the client sees: A feasibility and scope report at the end of Phase 0 (Milestone M0), in week 2. It covers data availability, tolerances, the measurement protocol, whether a safe trial process exists, and a go/no-go decision on the remaining $147,000.

Milestone M0, week 2: Feasibility and scope signed off. The client sees the confirmed data, tolerances and refined price and schedule.

Milestone M1, weeks 4-5: Baseline of the current process and a measurement-repeatability result. Work continues only if the measurements and paired records are adequate, or the client approves a controlled calibration plan.

Milestone M2, weeks 9-11: Working MVP in a test environment, with offline results on held-out batch data.

Milestone M3, weeks 13-16: Pilot results from shadow mode and then human-approved recommendations, with a recommendation to scale or defer.

Milestone M4, weeks 14-18: Handover, with the runbook, training, documentation and a support proposal.

Total: 14-18 calendar weeks. The phases may overlap slightly if site and data access allow. The timeline starts only once access, data and the client's subject-matter experts are available.

Steps that depend on the client, not us:
- Site access, security review and named owners from business, quality, IT/OT and procurement.
- Approved master tiles and versions, the pilot SKU list, and sign-off on numeric colour and gloss tolerances.
- Historical records pairing printer-input changes with fired-tile measurements, plus access to printer reference files and the Photoshop workflow.
- Lab spectrophotometer and gloss-meter access, calibration records, and an export method for readings.
- Staff time for workshops, sample printing, kiln firing slots and measurement during baseline, calibration trials and the pilot.
- Approval of safe printer-adjustment bounds, and the production schedule, since trials can only run when batch changes actually happen.
- Timely go/no-go decisions at each gate. A delayed gate delays everything after it.
- Finance confirming the disposition and cost of off-shade material, which the value case depends on.

Two timing risks:
- The physical print, fire and cool steps can't be shortened by software, so each correction round has a fixed physical duration regardless of how fast our recommendation is.
- Collecting 20 baseline batch starts inside Phase 1 depends on how often the client changes batches, which is unknown. If changeovers are infrequent, the baseline takes longer and the dates slip.

---

## 8. Where I pushed back, narrowed, or said no

- I told them not to build autonomous printer control in phase one, since there is no validated mapping or safe bounds yet.
- I refused to commit to 5-6 minutes end to end. I reframed it as decision latency, because firing is physical.
- I narrowed the scope to one site, one printer, and 3-5 SKUs, with no MES/LIMS/ERP integration.
- I said no to camera-only inspection as the primary approach and no to kiln/raw-material root-cause work in this phase.
- I made discovery a paid gate so we don't commit $147k before the data is confirmed.
- I won't set tolerances after seeing results, and I won't silently accept near-matches. The client currently does that, and it should become a recorded quality decision.
- I won't promise savings, only a pilot that measures them.

---

## 9. What is most likely to go wrong, and what I didn't trust

Most likely failure: there is no paired input-change-to-fired-tile data, and the kiln or firing time shifts the shade enough that a correction learned in one context doesn't transfer. Then Phase 2 grows, the price rises, and the model abstains often.

A second risk is the baseline. Collecting 20 batch starts inside a 2-3 week Phase 1 may not be possible, depending on how often they change batches. That number is unknown.

What I didn't trust in the notes:
- The 5,000-10,000 m² figure. The notes themselves say it was unclear on the recording, and it may not be lost material at all.
- The 6-7 hours (one round or total?) and the 5-6 minutes (decision or end to end?). Both are undefined.
- The claim that "the rest of the batch runs fine after the first approval." It is unverified, and if untrue, the value case changes.
- The proposed gates (90%, 80%, 70%, 50%, 30%). These are starting points for discussion, not evidence-based thresholds.
- The $5/m² figure and the prevention percentages, which are placeholders.
- The effort numbers. The total line says 167 while the roles sum to 169, and "6-8 people" is vague. Treat them as ROM estimates.
- The spectrophotometer measures a small area, so one spot may not represent the whole tile.

---

## 10. What I used AI for

Tools: Claude (Anthropic) and GPT [version: check your chat history].

- Claude: helped me understand the call notes and terminology (CIELAB, ΔGloss, kiln firing, master tile vs production sample), and pressure-tested my own raw solution against alternatives.
- GPT: [I used it for the problem statement, solution options, and build plan documents. Confirm this and say what you gave it as input.]

**Where it helped:** terminology, structuring the options comparison, drafting the answer outlines, and checking arithmetic (phase prices and milestone payments both sum to $165,000, and the break-even figures hold).

**Where it misled me or needed checking:**
- Claude went too technical. When I asked it to explain a term, it often started teaching the concept in depth instead of helping me write it into my document. It wasn't wrong, but it didn't fit what I needed, which was a short plain definition I could document.
- The GPT documents needed checking. [I used GPT [version: check your history] for the problem statement, solution options, and build plan. I'm not certain which version it was.] I treated the numbers in them as unverified until I checked them against each other. [Only keep the next two lines if you actually checked these yourself:] The effort total says 167 days but the role breakdown adds up to 169. The success thresholds (90%, 80%, 50%, 30%) and the $5/m² value figure are placeholders, not client data.

**What I threw away or rewrote:**
- I dropped the long, teaching-style explanations from Claude and kept only the short definitions I needed for the documentation.
- I switched to GPT for the documentation work because it was better suited to producing the structured documents.
- [Add anything else you really discarded, such as thresholds, cost figures, or wording that didn't sound like you. If you discarded nothing else, leave it out rather than inventing it.]
