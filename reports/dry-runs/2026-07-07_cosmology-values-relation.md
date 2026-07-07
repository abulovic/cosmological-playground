# Design note: the cosmology–values relation

- Date: 2026-07-07
- Kind: design / theory exploration (not a pipeline task run)
- Participants: Ana, Claude
- Status: working notes — unreviewed
- Feeds: the value-card source choice, and D4-002 (value matching)

## The question

Ana asked us to sharpen the relation between **cosmology, values, and action**, and
to ground it in an existing body of thought — philosophy, sociology, or elsewhere.
Her standing view frames everything below: a cosmology does **not** entail action.
It is a *generative scaffolding*. Holding a certain picture of what is real *makes
certain values and decisions easier to hold*, and there is a feedback loop from what
people *need* to believe back into the cosmology. (Her example: Christian thinkers
such as Aquinas adapted the cosmology out of inner need, creatively, without leaving
it.)

Two pieces were flagged as still open: a **suitable definition of cosmology**, and
**what is left in the relation when the cosmology is removed**.

## The relation we adopt: elective affinity, not entailment

One sentence to stand on:

> Cosmology and values stand in an **elective affinity**, not an entailment: the
> cosmology is a "model of" the world that doubles as a "model for" living, so it
> makes some values easier to hold — and because people must also live, there is a
> return arrow from need back into the cosmology, which is why traditions get
> revised from within.

"Elective affinity" (Weber, *Wahlverwandtschaft*) means a *mutual fit* between a
belief and a way of acting: each makes the other feel natural, without either
*causing* the other. This is the precise name for Ana's "makes easier to hold."

The relation has three arrows:

1. **Down (cosmology → values): not entailment.** Hume's is/ought gap — you cannot
   derive an "ought" from an "is" by logic alone. So the link *cannot* be
   entailment; deriving action from cosmology by logic is a category error. Philosophy
   here explains why the bridge Ana refuses to build was never buildable.
2. **The link itself (an affordance): "makes easier to hold."** Geertz's
   "model of / model for" — the same picture that says how the world *is* doubles as
   a template for how to live, and the two come to seem to confirm each other.
   Taylor's "framework / social imaginary" — a mostly-unspoken background that decides
   what even shows up as a good worth reaching for. Weber's "elective affinity" — the
   mutual fit.
3. **Up (need → cosmology): the feedback loop.** James's "will to believe" — we are
   entitled to hold beliefs we genuinely need in order to live and act. MacIntyre — a
   living tradition is "an argument extended through time," so revolutionaries argue
   the cosmology *forward* from inner need rather than abandoning it.

## Working definition of cosmology (v0.1)

A **cosmology** is a background picture of what is real and how it hangs together —
in this project, a set of claims across the twelve frozen primitives (ultimate
reality, constituents, origin, causality and agency, cosmic structure, time, human
place, self and consciousness, fundamental problem, transformation, destiny,
epistemic access). Three features matter:

- It is an **"is," not an "ought."** It describes reality; by describing reality it
  makes some ways of living look fitting — but it does not contain the values as
  premises. (This is the firewall: cosmological description stays separate from value
  matching.)
- It is held as **background** — mostly taken for granted, not argued for (Taylor's
  social imaginary).
- It is **revisable under need** — the feedback loop can reshape it.

## What is left when we take the cosmology out

Remove the cosmology from the affinity and the values do **not** vanish. They become
**orphaned** — still held, but no longer *made easy* by a supporting picture of
reality. (This is an existing repo concept: see
`knowledge/topics/cosmological-orphaning.md`, doctrines that outlive their supporting
primitives.)

What remains is:

1. **The standing human situation** — the perennial questions any cosmology has to
   answer (how to face death, suffering, strangers, children; how to weigh present
   against future) and the **needs** that pull on belief (James). These do not change
   when the cosmology changes; only the answers that come *easily* change.
2. **The values themselves, now unhosted** — holdable only by effort, and prone to
   wobble. This is Weber's "disenchantment" and Taylor's "malaise of modernity":
   values survive the death of the cosmology that made them feel natural, but now must
   be carried without scaffolding.

So the cosmology's job in the affinity was to make certain values *easy* to hold.
Subtract it and you are left with the human situation plus a set of values that are
now hard to hold, because nothing makes them feel natural.

This reframes disenchantment as a **design space**: different cosmologies re-host
different subsets of the perennial values. Mapping that is exactly what the tool is
for.

(A second, thinner reading of the same question: "cosmology" is just our rich name
for the *is*-pole of the affinity. Strip the grand word and the bare structure is
Hume's is/ought pair — but a *thick* "is," a whole pictured world, not isolated
facts. This tells us the relation is not special to religion: any thick picture of
reality, scientific naturalism included, sits in the same affinity with values.)

## The thinkers (map)

- **David Hume** — *A Treatise of Human Nature* (1739–40), Bk III.i.i. The is/ought
  gap. Grounds arrow 1 (not entailment).
- **Clifford Geertz** — "Religion as a Cultural System" (1966), in *The
  Interpretation of Cultures* (1973). "Model of" / "model for"; the fusion of
  worldview and ethos. Grounds the mechanism of arrow 2.
- **Max Weber** — *The Protestant Ethic and the Spirit of Capitalism* (1904–05);
  "Science as a Vocation" (1917). "Elective affinity" (the relation) and
  "disenchantment" (what removal feels like).
- **Charles Taylor** — *Sources of the Self* (1989); *Modern Social Imaginaries*
  (2004); *A Secular Age* (2007). "Framework," "social imaginary," "malaise." Grounds
  "a background that makes goods reachable."
- **William James** — "The Will to Believe" (1896). Belief answering to need. Grounds
  arrow 3.
- **Alasdair MacIntyre** — *After Virtue* (1981). Tradition as "an argument extended
  through time." Grounds revision-from-within (the Aquinas case).
- Adjacent, for later: **Pierre Bourdieu**, *habitus* — how a background becomes a
  felt personal inclination (*Outline of a Theory of Practice*, 1977); **Mary
  Douglas**, grid/group — a typology of how cosmologies and social forms co-produce
  each other (*Natural Symbols*, 1970).

Anchor: **Weber × Geertz, inside Hume**, with **James / MacIntyre** for the return
arrow.

## What this means for the tool

If the relation is affinity / affordance, the tool must **not** output "this cosmology
⇒ do X." For a held cosmology it should surface:

- which perennial values it **makes easier to hold** (re-hosts),
- which it **makes harder** (orphans),
- which new **questions or tensions** it opens,
- the **branch points** where different moves become live.

The product is a *map of what is made easier and what is opened*, not a verdict. This
matches the "branching as output" stance and the firewall: D4-002 matching reports
"this cosmology makes value X easier to hold," never "entails action Y."

## Decisions reached this session

1. Adopt **elective affinity (Weber), not entailment**, as the working model of the
   cosmology–values relation. (Feeds D4-002.)
2. For the simple prototype, **extract value cards from cosmological texts**, not from
   interviews (interviews are not available to us). Uses MAI's *method* as a template,
   not MAI data.

## Open questions (for review)

- Is the **elective-affinity** anchor the right thing to freeze on, or only a working
  label until we have used it in a few analyses?
- The "what remains" section reads Ana's question as *"what happens to the values"*
  (→ orphaning). If she meant the thinner reading (the bare is/ought relation minus
  the word "cosmology"), that variant is noted above and can be promoted.
- Definition of cosmology is v0.1 and leans on the twelve-primitive ontology; revise
  if the ontology changes.

## Sources

Standard editions of the works listed under "The thinkers." These are working
citations for orientation; anything that later enters a cosmology card must be
re-sourced under the card schema's citation rules.
