# Cosmological primitives — version 1 contract

Status: **frozen for prototype implementation**
Version: `1.0.0`
Frozen: 2026-07-06
Owner: research framework
Human-review status: **methodology review still required before pilot claims of domain validity**

## Purpose and scope

This ontology is an analytic scaffold for claims represented in a selected text. It is not a universal inventory of worldviews, a taxonomy of people, or a way to infer an author's private beliefs. It decomposes textual evidence into twelve dimensions so that candidate cosmologies can be compared claim by claim instead of assigned by resemblance to a broad religious or cultural label.

The unit of analysis is a claim made by an identified textual voice. A text may represent several incompatible cosmologies, leave most dimensions unobserved, or support a hybrid or novel result.

## Evidence contract

All twelve primitives allow exactly these evidence states:

- `explicit`: the relevant voice directly asserts the claim.
- `strongly_implied`: the claim is not stated verbatim but is required to make coherent sense of multiple endorsed statements.
- `weakly_implied`: the claim is a plausible reading but alternatives remain comparably supported.
- `unobserved`: the text supplies no responsible basis for a claim on this primitive.

`Unobserved` is not evidence that a claim is false. It carries no source span. Every other state must store:

- an exact, offset-addressable text span;
- the speaker, narrator, or other voice responsible for it;
- stance toward the proposition: `endorsed`, `quoted`, `reported`, `criticized`, `fictional`, or `unclear`;
- the normalized claim;
- an inference rationale explaining why the span supports that claim and strength;
- alternative readings when the evidence is underdetermined.

Evidence strength describes support in the submitted text, not whether the proposition is true and not how typical it is of a reference tradition.

## Global interpretation rules

1. Attribute before interpreting. Quotation, reported speech, criticism, irony, and fictional dialogue are not author endorsement.
2. Preserve negation. “There are no gods” supports a negative constituents claim; it is not evidence for gods.
3. Do not infer a primitive from genre, identity terms, or a tradition name alone. “She is a Buddhist” is metadata about a person, not evidence for emptiness or no-self.
4. Treat metaphor as `unclear` unless the surrounding text licenses an ontological reading. Poetic personification alone is insufficient.
5. A span may support more than one primitive, but each use needs its own rationale.
6. Local events count only when the text presents them as revealing a general feature of reality, existence, or the human condition.
7. Preserve contradictions and voice-specific claims. Do not average them into a falsely coherent position.
8. Absence of a reference-card claim from the text is `unspecified`, not `contradicts`.
9. Extract descriptions before matching candidates. Candidate labels must not determine which claims are noticed.

## Primitive specifications

Each primitive below allows `explicit`, `strongly_implied`, `weakly_implied`, and `unobserved` under the common evidence contract above.

### 1. Ultimate reality (`ultimate_reality`)

**Definition:** Claims about what is most fundamental, irreducible, or metaphysically basic.

**Include:** assertions that reality is fundamentally material, mental, spiritual, divine, empty of intrinsic nature, relational, informational, processual, plural, or otherwise grounded.

**Exclude:** an inventory of particular beings without a claim about fundamentality; evaluative phrases such as “what matters most”; rhetorical uses of “real.”

**Counterexample:** “The threat became real at dawn” describes recognition of danger, not the metaphysical basis of reality.

**Ambiguity test:** Ask whether the passage answers “what is reality ultimately made of or grounded in?” If it only names something that exists, use `constituents` instead.

### 2. Constituents (`constituents`)

**Definition:** Claims about the kinds of beings, entities, processes, powers, or relations that exist and can participate in reality.

**Include:** gods, spirits, ancestors, souls, physical entities, fields, minds, processes, relations, or multiple ontological realms when their existence is asserted or denied.

**Exclude:** fictional entities acknowledged only as fictional; grammatical personification; mere named objects with no cosmological relevance.

**Counterexample:** “Fortune smiled on the expedition” does not by itself posit Fortune as an agent or being.

**Ambiguity test:** Distinguish a literal ontological commitment from imagery by checking recurrence, causal participation, and the stance of the relevant voice.

### 3. Origin (`origin`)

**Definition:** Claims about how reality, life, humanity, or the present cosmic order arose or whether such an origin is denied or unknowable.

**Include:** creation, emanation, emergence, evolution, ordering of chaos, cyclic recurrence, beginningless existence, and explicit suspension of origin claims.

**Exclude:** the beginning of a local event, biography, institution, or story unless generalized into cosmogenesis or anthropogenesis.

**Counterexample:** “The village began beside the river in 1820” is local history, not a cosmic origin claim.

**Ambiguity test:** Record the object whose origin is described. Do not silently turn an origin of social order into an origin of reality.

### 4. Causality and agency (`causality_and_agency`)

**Definition:** Claims about what produces events and which kinds of agents or principles can make a difference in the world.

**Include:** natural law, chance, providence, karma, fate, spirits, reciprocal relations, free agency, determinism, emergence, and denials of agency.

**Exclude:** a single everyday causal statement with no implication beyond the event; moral responsibility considered only as praise or blame.

**Counterexample:** “The dropped glass broke on the floor” does not alone establish a naturalistic or deterministic cosmology.

**Ambiguity test:** Ask whether the passage treats the causal pattern as a general feature of reality or as evidence for a class of cosmic agents.

### 5. Cosmic structure (`cosmic_structure`)

**Definition:** Claims about the large-scale organization, differentiation, boundaries, or hierarchy of reality.

**Include:** one or many worlds, layered realms, dualisms, hierarchies, immanence and transcendence, sacred centers, interdependence, and boundaries between natural and supernatural domains.

**Exclude:** physical layout, social hierarchy, or spatial imagery without a claim about the organization of reality.

**Counterexample:** “The palace had three levels, with servants below” describes architecture and society, not a three-tier cosmos.

**Ambiguity test:** Spatial metaphors count only when the text uses them to organize kinds or regions of existence.

### 6. Time (`time`)

**Definition:** Claims about the form, direction, scale, or metaphysical status of time.

**Include:** linearity, cyclicality, eternity, branching time, progress, decline, recurrence, timelessness, and apocalyptic temporal structure.

**Exclude:** chronology, tense, duration, deadlines, or repetition that does not imply a general temporal pattern.

**Counterexample:** “Every Tuesday the train returned” is a schedule, not evidence for cyclical cosmic time.

**Ambiguity test:** Ask whether recurrence is merely periodic or is presented as the form of history, life, or reality.

### 7. Human place (`human_place`)

**Definition:** Claims about humanity's status, role, dependence, or relation to the wider cosmos and other kinds of being.

**Include:** exceptionalism, stewardship, fallenness, embeddedness, accidental emergence, kinship with nonhumans, cosmic purpose, or human insignificance.

**Exclude:** claims about one person's social identity, personality, or importance; ethical duties without a cosmological account of human status.

**Counterexample:** “Mara was the most important person in the committee” does not make humanity cosmically exceptional.

**Ambiguity test:** Separate claims about humans as a kind from claims about a particular character or community.

### 8. Self and consciousness (`self_and_consciousness`)

**Definition:** Claims about what a self, person, subject, mind, or experiencer is and how consciousness relates to body and world.

**Include:** soul, no-self, embodied or extended mind, mind–body dualism, continuity or dissolution of personal identity, panpsychism, and distributed consciousness.

**Exclude:** temporary emotions, personality descriptions, memory failures, or ordinary reflection without an ontological claim about selfhood.

**Counterexample:** “I did not feel like myself after the journey” need not deny a persisting self.

**Ambiguity test:** Look for claims about constitution, persistence, location, or boundaries of experience—not merely its current contents.

### 9. Fundamental problem (`fundamental_problem`)

**Definition:** Claims that diagnose a pervasive existential, cosmic, or human condition as disordered, deficient, entrapping, or estranged.

**Include:** sin, ignorance, suffering, craving, alienation, imbalance, bondage, meaninglessness, or a claim that there is no fundamental disorder.

**Exclude:** isolated practical problems, villains, policy disagreements, and the evaluator's own judgment that a worldview is harmful.

**Counterexample:** “The bridge is broken, so we cannot cross” presents a plot obstacle, not the fundamental human predicament.

**Ambiguity test:** The diagnosis must generalize beyond a local difficulty and belong to the represented cosmology; its badness is recorded separately as a value relation when applicable.

### 10. Transformation (`transformation`)

**Definition:** Claims about the process by which the fundamental condition of persons, society, or cosmos is overcome, healed, awakened, reconciled, or otherwise changed.

**Include:** salvation, enlightenment, liberation, conversion, harmony, ritual renewal, technological transcendence, progress, and acceptance when presented as a fundamental response.

**Exclude:** ordinary learning, character development, repair, or political tactics without existential or cosmological scope.

**Counterexample:** “After practice, she became a better violinist” does not establish a path of salvation or liberation.

**Ambiguity test:** Extract the proposed mechanism, not the evaluator's approval of the resulting state. A desired end may also generate a separate value-card match.

### 11. Destiny (`destiny`)

**Definition:** Claims about the ultimate or characteristic trajectory of persons, history, life, or the cosmos.

**Include:** judgment, afterlife, renewal, liberation, recurrence, extinction, heat death, progress, open futures, and explicit denials of purpose or predetermined end.

**Exclude:** forecasts for local events, personal ambitions, narrative endings, or “destiny” used as emotional rhetoric.

**Counterexample:** “The team is destined to win tonight” is a local prediction unless the passage turns it into a general doctrine of fate.

**Ambiguity test:** Record whose destiny is at issue and distinguish teleology (a directed end) from a predicted outcome.

### 12. Epistemic access (`epistemic_access`)

**Definition:** Claims about how cosmological knowledge is possible, warranted, transmitted, limited, or denied.

**Include:** revelation, reason, empirical inquiry, testimony, tradition, ritual, contemplation, intuition, altered experience, plural methods, skepticism, and ineffability.

**Exclude:** a source citation by itself, ordinary perception of a local fact, or the analyst's assessment of evidence quality.

**Counterexample:** “I saw rain through the window” is ordinary observation, not a general account of access to cosmological truth.

**Ambiguity test:** Ask whether the text presents the method as licensing knowledge about reality's wider order, not merely this event.

## Boundary between cosmology and values

Cosmological primitives are descriptive commitments about reality, existence, the human condition, transformation, destiny, and access to such knowledge. Values answer what is desirable, admirable, sacred, forbidden, or worth pursuing. The two can be textually linked but must never be collapsed.

| Passage-level content | Store as cosmology | Store as value relation |
|---|---|---|
| “Humans were appointed custodians of a living earth.” | `human_place`: humans have a custodial cosmic role; possibly `constituents`: earth is living, if literal | stewardship or care only if the passage presents custody as desirable or obligatory |
| “Craving binds beings to suffering; release comes through insight.” | `fundamental_problem`, `causality_and_agency`, and `transformation` | liberation or wisdom only when normatively endorsed |
| “Equality is good.” | none without further claims about reality | candidate value match to equality |
| “All minds are fragments of one consciousness.” | `ultimate_reality` and `self_and_consciousness` | none unless unity is also praised or prescribed |

Operationally:

- Primitive extraction happens before MAI value matching.
- A value match must cite its own exact span and rationale; it cannot inherit evidence merely because a primitive was extracted.
- `fundamental_problem` records the cosmology's diagnosis, not the system's moral agreement with it.
- `transformation` records the represented mechanism; goals and virtues implied by that mechanism are separate candidate value matches.
- Moral-graph edges are external sourced data and are never inferred from primitive proximity.

## Comparison with scholarly frameworks

The twelve primitives are a project decision, not a claim that scholarship has converged on twelve universal categories. They were stress-tested against three complementary frameworks:

| Framework | Relevant structure | Coverage in this contract | Deliberate difference |
|---|---|---|---|
| Aerts, Apostel et al., seven components of a worldview | world model, explanation, evaluation, possible futures, knowledge construction, action, and worldview fragments/origins | world model and explanation are decomposed across `ultimate_reality` through `human_place`; futures across `time` and `destiny`; knowledge construction in `epistemic_access` | evaluation and action are not treated as cosmological evidence. They belong to values/praxeology, while `transformation` records only cosmologically framed mechanisms |
| Kearney's anthropological logico-structural model | self, other/non-self, relationship, classification, causality, space, and time | `self_and_consciousness`, `constituents`, `human_place`, `causality_and_agency`, `cosmic_structure`, and `time` preserve these relational and cognitive concerns | this contract adds origin, existential diagnosis, transformation, destiny, and epistemic access because the product must compare complete textual claims, including soteriological and eschatological ones |
| Smart's multidimensional study of religions and secular worldviews | doctrinal/philosophical, narrative/mythic, ethical/legal, ritual, experiential/emotional, social/institutional, and material dimensions | primitive claims mainly concern doctrinal/philosophical content; narrative, ritual, experience, and material forms may supply context or evidence | ethical claims remain in the values layer; social, ritual, experiential, narrative, and material dimensions are not themselves cosmological primitives. This prevents doctrine-only analysis from pretending to describe a whole religion |

This triangulation produces three constraints:

1. A worldview is more than ontology, so the contract includes explanation, temporal trajectory, human condition, transformation, and epistemology.
2. A religion or culture is more than its cosmological propositions, so this system must describe its output narrowly as text-level cosmological analysis.
3. Values and action can interact with cosmology without serving as substitute evidence for it.

### Scholarly sources

Accessed 2026-07-06.

- `[source:aerts-apostel-1994-worldviews]` Diederik Aerts, Leo Apostel, et al., *World Views: From Fragmentation to Integration* (VUB Press, 1994), especially “The Seven Components of a World View.”
- `[source:kearney-1984-world-view]` Michael Kearney, *World View* (Chandler & Sharp, 1984). The seven-category summary used here is independently supported by `[source:schafer-2004-world-view-theory]` Marc Schafer, “World view theory and the conceptualisation of space in mathematics education,” *Pythagoras* 59 (2004), pp. 8–17.
- `[source:smart-1998-dimensions-sacred]` Ninian Smart, *Dimensions of the Sacred: An Anatomy of the World's Beliefs* (University of California Press, 1998), especially chapters 1–7.

Canonical URLs, access dates, review status, and website-ready citations are stored in `knowledge/sources.json` under these stable IDs.

These sources motivate coverage and boundaries. They do not establish that this ontology is culturally universal or empirically validated.

## Difficult-case review fixtures

These synthetic passages are methodology fixtures, not claims about any historical tradition. Offsets must be calculated from the exact submitted string by the implementation.

| Case | Exact evidence span | Expected handling |
|---|---|---|
| Negation | “No god steers the stars; their paths follow impersonal regularities.” | `constituents`: denial of a steering god; `causality_and_agency`: impersonal regularity. Preserve the negation. |
| Quotation and criticism | “The priest says, ‘The river judges us.’ I reject that superstition.” | The embedded claim is `quoted` and `criticized`, not narrator-endorsed. Do not infer the narrator believes in an agentive river. |
| Multiple voices | “Mina said death opens the true world. Sol answered that death ends every mind.” | Two voice-specific, contradictory `destiny` and possibly `self_and_consciousness` claims. Do not merge them. |
| Metaphor | “At dusk the old house remembered its children.” | At most `weakly_implied` with stance `unclear`; normally abstain on distributed consciousness without literalizing context. |
| Sparse evidence | “The cup is blue.” | All primitives `unobserved`; result should be `insufficient evidence`. |
| Hybrid pattern | “Matter alone exists, yet the dead return through the memories of the living and guide their choices.” | Preserve potential tension: materialist `ultimate_reality`, socially mediated ancestor-like agency, and an ambiguous account of postmortem continuity. A mixture may outrank a forced single card. |
| Out of distribution | “To reset the router, hold the rear button for ten seconds.” | No cosmological extraction; `insufficient evidence`. |
| Cosmology/value boundary | “The universe has no purpose, but we ought to protect every conscious creature.” | `destiny`: no cosmic purpose; value candidate: protection/care. The obligation is not evidence for cosmic purpose. |

## Reviewer protocol

For each fixture or future reviewed passage, two reviewers should independently:

1. mark the smallest sufficient exact span;
2. identify voice and stance before assigning a primitive;
3. assign evidence strength or `unobserved`;
4. write a normalized claim and one-sentence rationale;
5. record a plausible alternative reading;
6. identify any separate value-bearing span.

Agreement is assessed separately for span overlap, voice, stance, primitive, and evidence strength. A disagreement is preserved as review evidence; it is not resolved by silently choosing the more confident annotation.

## Freeze and change control

Version 1 freezes the twelve primitive IDs, their definitions, the four evidence states, and the cosmology/value boundary for downstream schemas and evaluation. Wording clarifications may be patch releases. Adding, removing, merging, or changing the meaning of a primitive requires:

- an entry in `DECISIONS.md`;
- migration notes for cosmology cards and evaluation labels;
- review of at least the difficult-case fixtures above;
- a major or minor ontology version change, as appropriate.

This freeze authorizes implementation consistency; it does not satisfy the charter's human domain-review gate.
