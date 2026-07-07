# Manual pipeline dry run — "Making Beliefs Pay Rent (in Anticipated Experiences)"

- Date: 2026-07-06
- Kind: ad-hoc paper prototype of the D4 analysis pipeline, requested by the user to evaluate whether the Day-1 foundations are generative. Not a ledger task; no state or readiness changes.
- Analyst: single annotator (Claude), by hand, using the frozen contracts only:
  - `docs/COSMOLOGY_PRIMITIVES.md` v1.0.0 (evidence states, voice/stance rules, interpretation rules)
  - `docs/CONFIDENCE_AND_RANKING.md` v1.0.0 (coverage, fit aggregation, abstention gates, provisional-visibility rules)
- Candidates: the three draft cards in `knowledge/cosmologies/cards/` (all `review.status: draft`, unreviewed).
- Text: Eliezer Yudkowsky, "Making Beliefs Pay Rent (in Anticipated Experiences)", 2007-07-29. User-supplied; full text kept out of the repo (copyrighted essay), archived in the session scratchpad. Spans below are verbatim quotes; character offsets omitted for the manual run.

## Method notes

Everything below follows the contracts as written. Where the contract underdetermined a judgment, I made the call, flagged it `[JC-n]` (judgment call), and tested the outcome's sensitivity to flipping it. Those flags are themselves a result: they mark where two human annotators would be most likely to disagree, which is what the `verifier_disagreement` gate will eventually measure.

## Step 1 — Voice inventory (interpretation rule 1: attribute before interpreting)

| Voice | Stance | Consequence |
|---|---|---|
| Author (essayist) | endorsed | counts toward author-level fit (weight 1.0) |
| Two parable arguers ("Yes it does, for it makes vibrations in the air" / "No it does not, for there is no auditory processing in any brain") | quoted, framed as a mistake class | weight 0 |
| Alchemists (phlogiston causes fire) | reported + criticized | weight 0; the author's *criticism* is endorsed |
| English professor / Wulky Wilkinsen (retropositional author) | fictional + criticized | weight 0 |
| Élan vital believers | reported + criticized | weight 0; the author's criticism is endorsed |

A naive extractor would have harvested "it makes vibrations in the air," phlogiston-causation, and élan vital as cosmological commitments of the text. Voice rules filtered all of them; only the author's endorsements and endorsed denials survive.

## Step 2 — Per-primitive extraction (author voice only)

| Primitive | Strength | Normalized claim | Key span(s) |
|---|---|---|---|
| `ultimate_reality` | weakly_implied `[JC-1]` | Reality is grounded in unseen physical causes behind experience | "the world does, in fact, contain much that is not sensed directly"; "the unseen causes of experience" |
| `constituents` | explicit | Unseen physical entities (atoms) exist; phlogiston and élan vital do not (negation preserved, rule 2) | "the atoms are in fact there"; "believe in things that are not only unseen but unreal" |
| `origin` | unobserved | — | — |
| `causality_and_agency` | strongly_implied | Events are produced by a lawlike causal order that constrains experience in advance; putative causes yielding no advance predictions are unreal | "a network of inferred causes behind sensory experience"; "constraining the experience in advance"; the gravity example used as a paradigm true causal belief |
| `cosmic_structure` | unobserved | — | — |
| `time` | unobserved (clock talk is chronology; excluded by the primitive spec) | — | — |
| `human_place` | explicit | Humans are one animal species among others, distinguished by a superior — and uniquely corruptible — capacity to model the unseen | "better than any other species in the world, learn to model the unseen"; "a uniquely human flaw among animal species" |
| `self_and_consciousness` | strongly_implied | Perception and belief are processes carried out by the brain | "you see what your retina and visual cortex have processed of that light"; "The same brain that builds a network of inferred causes…" |
| `fundamental_problem` | explicit `[JC-2]` | Humanity's characteristic disorder is holding belief networks disconnected from experience ("floating" beliefs; believing the unreal) | "It is a uniquely human flaw among animal species, a perversion of Homo sapiens's ability…" |
| `transformation` | weakly_implied `[JC-3]` | The disorder is overcome through a disciplined practice: continually testing beliefs against anticipated experience and evicting those that fail | "The rationalist virtue of empiricism consists of constantly asking which experiences our beliefs predict—or better yet, prohibit"; "If a belief turns deadbeat, evict it" |
| `destiny` | unobserved | — | — |
| `epistemic_access` | explicit | Legitimate access to reality's order runs through empirical anticipation: beliefs must predict or prohibit experiences; inference to unseen causes is valid when predictive; unfalsifiable beliefs are illegitimate | "Every question of belief should flow from a question of anticipation"; "what would definitely falsify this belief?" |

Judgment calls in extraction:

- `[JC-1]` The text never makes a fundamentality claim; the primitive's ambiguity test ("if it only names something that exists, use `constituents`") pushes the atom span to `constituents`. Physicalist grounding is a plausible overall reading, so `weakly_implied`; a stricter annotator scores `unobserved`.
- `[JC-2]` "A uniquely human flaw" is directly asserted, hence `explicit` — but reading it as the text's *fundamental problem* (rather than one flaw among many) is an interpretive step a second reviewer might resist.
- `[JC-3]` The practice is explicit, but whether it has the existential scope the `transformation` primitive requires (vs. the "ordinary learning" exclusion) is genuinely borderline. The essay frames it as "a foundational skill… on which all other technique rests," addressed to the species-level flaw, which is why it is scored at all.

**Evidence coverage** (uniform weights; usable = explicit / strongly_implied / weakly_implied, attributable voice): 8 of 12 primitives → `evidence_coverage = 0.667`. Strictest variant (drop JC-1 and JC-3): 6/12 = 0.500.

## Step 3 — Claim-by-claim comparison and fit

Contribution = relation score × strength weight × stance weight (all stances endorsed = 1.0); fit = Σ contributions / Σ weights. Relation scores: entails +1.0, compatible +0.5, tension −0.5, contradicts −1.0. Strength weights: explicit 1.0, strongly_implied 0.7, weakly_implied 0.35. `unspecified` pairs are excluded from fit and reported separately.

### Candidate: scientific-naturalism

| Card claim (primitive) | Relation | Contribution / weight |
|---|---|---|
| ultimate_reality — everything is physical | compatible | +0.175 / 0.35 |
| constituents — no supernatural beings; all entities physical | compatible (evidence supports instances, not the universal) | +0.5 / 1.0 |
| origin — no supernatural creation | unspecified (text silent) | excluded |
| causality_and_agency — causal closure of the physical | compatible | +0.35 / 0.7 |
| cosmic_structure — single natural world | unspecified | excluded |
| human_place — humans natural organisms continuous with nature | **entails** `[JC-4]` ("among animal species" directly asserts it) | +1.0 / 1.0 |
| self_and_consciousness — mind supervenes on the physical (contested) | compatible | +0.35 / 0.7 |
| epistemic_access — scientific method the authoritative route, all areas | **entails** `[JC-5]` (the text's norm is explicitly universal: "Every question of belief…") | +1.0 / 1.0 |

**Fit = 3.375 / 4.75 = +0.711.** Cautious variant (JC-4, JC-5 demoted to compatible): +0.500 — still well above every gate.

### Candidate: christian-classical-theism

| Card claim (primitive) | Relation | Contribution / weight |
|---|---|---|
| ultimate_reality — God absolutely simple, ultimate | tension | −0.175 / 0.35 |
| constituents — uncreated God + creation visible and invisible | compatible (atoms fit inside creation; nothing denied) | +0.5 / 1.0 |
| origin ×2 — creation; temporal beginning by faith | unspecified | excluded |
| causality_and_agency — first efficient cause, God | compatible `[JC-6]` (a reviewer applying the essay's phlogiston pattern would say tension) | +0.35 / 0.7 |
| cosmic_structure — visible and invisible realms | unspecified | excluded |
| time — timeless eternity | unspecified | excluded |
| human_place — creatures of God, objects of saving action | tension `[JC-7]` (deflationary "among animal species" strains against unique soteriological status without contradicting it) | −0.5 / 1.0 |
| fundamental_problem — estrangement from God | tension `[JC-8]` (rival diagnosis; see contract-gap finding 2) | −0.5 / 1.0 |
| transformation — salvation through Christ | tension (rival mechanism) | −0.175 / 0.35 |
| destiny — judgment, resurrection | unspecified | excluded |
| epistemic_access — reason + revelation; some truths **by faith alone**, indemonstrable | **contradicts** — the text's universal norm ("Every question of belief should flow from a question of anticipation… If a belief turns deadbeat, evict it") directly excludes faith-alone assent to indemonstrable content | −1.0 / 1.0 |

**Fit = −1.5 / 5.4 = −0.278.**

### Candidate: buddhist-madhyamaka

| Card claim (primitive) | Relation | Contribution / weight |
|---|---|---|
| ultimate_reality — all phenomena empty of svabhāva | tension `[JC-9]` ("the atoms are in fact there" realism strains against it; a reviewer could say compatible via conventional truth) | −0.175 / 0.35 |
| ultimate_reality — emptiness of emptiness | unspecified (the text evidence does not bear on this meta-claim; see contract-gap finding 3) | excluded |
| constituents — nothing non-empty; conventional existence | compatible | +0.5 / 1.0 |
| causality_and_agency — dependent origination | compatible (both affirm regular conditionality) | +0.35 / 0.7 |
| self_and_consciousness — no independent self; skandhas | compatible (both reject a freestanding soul-substance) | +0.35 / 0.7 |
| transformation — liberation via the two truths → nirvāṇa | tension (rival mechanism) | −0.175 / 0.35 |
| destiny — saṃsāra not different from nirvāṇa | unspecified | excluded |
| epistemic_access — two truths; ultimate knowledge beyond conceptual conventions | tension (conventional-truth half coheres; trans-conceptual knowledge conflicts with the universal anticipation norm) | −0.5 / 1.0 |
| epistemic_access — no thesis; therapeutic arguments | tension `[JC-10]` | −0.5 / 1.0 |

**Fit = −0.15 / 5.1 = −0.029.**

## Step 4 — Signals and gates

| Signal | Value |
|---|---|
| `evidence_coverage` | 0.667 (strict variant 0.500) |
| `top_fit` | +0.711 — scientific-naturalism |
| `second_fit` | −0.029 — buddhist-madhyamaka |
| third | −0.278 — christian-classical-theism |
| unresolved strong contradictions with top candidate | 0 |
| `verifier_disagreement` | not measurable (single annotator); 10 flagged judgment calls stand in for it |
| `out_of_distribution` | no (first-person discursive essay is squarely in the target genre) |

| Gate | Check | Result |
|---|---|---|
| `coverage_floor` | 0.667 ≥ 0.25 | pass (passes even at strict-variant 0.500) |
| `verifier_disagreement` | 0.0 ≤ 0.34 (caveat: unmeasured) | pass |
| `out_of_distribution` | false | pass |
| `fit_floor` | 0.711 ≥ 0.35 | pass |
| `margin_floor` | 0.711 − (−0.029) = 0.740 ≥ 0.10 | pass |
| `contradiction_block` | 0 < 1 | pass |

**Outcome: `proceed`.**

## Step 5 — The report the system would render

> **Best-matching reference cosmology: Scientific naturalism (contemporary philosophical)** — candidate fit +0.71; evidence coverage 0.67 (8 of 12 primitives).
> **Confidence: high (heuristic band) — provisional — uncalibrated.** No calibrated confidence exists yet (`calibrated_confidence: null`).
> Runner-up: Buddhist Madhyamaka, fit −0.03; Christian classical theism, fit −0.28 (one contradiction: the text's universal anticipation norm vs. faith-alone epistemic access).
> **Where the text exceeds its best match:** the text asserts an explicit `fundamental_problem` (floating beliefs — belief networks disconnected from experience) and a `transformation` practice (test every belief against anticipation; evict deadbeat beliefs). The scientific-naturalism reference card records both primitives as unspecified — the tradition has no canonical doctrine there. The text is naturalism *plus* a problem-and-practice structure its reference tradition does not codify.
> **Unspecified on both sides:** origin, cosmic_structure, time, destiny.
> **What evidence would most change the result:** an explicit claim about what is metaphysically fundamental (ultimate_reality is only weakly implied); any statement on origins or ultimate trajectory; clarification of whether the anticipation norm extends to metaphysics as such. All draft cards are unreviewed; no scholarly authority is claimed.

Note the band sits at the fit boundary: under the cautious relation variant (fit 0.50–0.61) the band drops to **medium**. The verdict does not change; the displayed band does. This is exactly the kind of threshold sensitivity D6-002 calibration is for.

## Robustness

Flipping every flagged judgment call simultaneously against the top candidate (JC-1 and JC-3 dropped from coverage → 0.500; JC-4 and JC-5 demoted → fit 0.500; JC-6–JC-10 resolved in either direction) leaves the outcome unchanged: proceed, top candidate scientific-naturalism, margin ≥ 0.44. On this text the verdict is insensitive to every identified annotator disagreement. That will not hold for genuinely hybrid texts — which is what the gates are for.

## Contract gaps surfaced (cheap to fix now, before D2-001 and D4-001)

1. **The relation vocabulary lacks a rule for rival non-exclusive answers.** When the text and a card give *different* answers to the same primitive that are not logically incompatible (floating beliefs vs. estrangement from God as `fundamental_problem`), neither `compatible` nor `contradicts` is right. I used `tension` (JC-7, JC-8); the contract should say so explicitly or add a defined convention.
2. **Per-claim vs. per-primitive `unspecified`.** When a card carries two claims on one primitive and the text evidence bears on only one (Madhyamaka's emptiness-of-emptiness), the contract does not say whether the untouched claim is `unspecified`. I applied it per claim; this should be codified before D4-001 implements aggregation.
3. **Coverage is strength-blind.** A `weakly_implied` reading counts toward coverage exactly as much as an `explicit` assertion. Fine as a v1 decision, but worth an explicit note; a strength-weighted coverage variant may be a D6-002 candidate.
4. **`verifier_disagreement` needs an operational definition** before the gate is testable end-to-end: disagreement over what, at which granularity (span / stance / strength / relation)? The ten JC flags above suggest relation-level disagreement is where the mass is.

## What this run says about generativity

- The headline label ("reads as scientific naturalism") is unsurprising for this text; if the desired product is classification, this run adds little beyond confirmation that the machinery agrees with the obvious.
- The non-obvious value showed up in the residue, not the ranking: the voice filter discarding four seductive pseudo-commitments; the text *out-running* its best-matching card on exactly the soteriological primitives (problem + practice); the contradiction pin-pointing precisely where the essay and classical theism part ways (faith-alone epistemic access, not God or creation).
- Design implication for D2-004 and D5-001: foreground the per-primitive evidence, the "text exceeds card" residue, and the fired/near-fired gates; the fit ranking is the least informative part of the output.
