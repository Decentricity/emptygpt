#!/usr/bin/env python3
"""
EmptyGPT paragraph generator (expanded alternates + snowclones).

- Embedded JSON grammar/lexicon.
- Many alternate templates per operator, from explicit snowclone parody to subtle.
- Outputs 1..N paragraphs; sentences are space-joined inside each paragraph.
- Prevents recursion explosions via max depth + "simple NP inside PP" rule.
"""

import json
import random
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Union


EMBEDDED_JSON = r"""
{
  "config": {
    "max_np_depth": 3,
    "max_pp_per_np": 2,
    "max_modifiers_per_np": 2,

    "min_optional_inserts": 1,
    "max_optional_inserts": 5,

    "min_paragraphs": 1,
    "max_paragraphs": 3
  },
  "lexicon": {
    "abstract_noun": [
      "meaning","agency","legitimacy","coherence","resilience","alignment","possibility","emergence",
      "interpretability","robustness","fairness","trust","consensus","coordination","governance",
      "accountability","transparency","integrity","authenticity","authorship","signal","noise",
      "salience","attention","intent","purpose","value","impact","outcome","directionality",
      "trajectory","momentum","optionality","contingency","uncertainty","ambiguity","tension","friction",
      "entropy","stability","volatility","liquidity","scarcity","abundance","capacity","throughput",
      "latency","reliability","availability","durability","portability","composability","interoperability",
      "extensibility","modularity","scalability","sustainability","sovereignty","privacy","security","safety",
      "risk","exposure","surface area","attack surface","invariance","equilibrium","disequilibrium",
      "plasticity","adaptation","learning","generalization","calibration","consistency","ground truth",
      "context","situatedness","bounded rationality","collective sensemaking","shared reality",
      "epistemic humility","strategic ambiguity","institutional memory","social license",
      "credibility","credence","consent","compliance","assurance","verification","validity","fidelity",
      "stewardship","constraint","tradeoff","externality","alignment tax","feedback","failure","drift",
      "overfitting","underfitting","tail risk","model risk","operational risk"
    ],
    "concrete_noun": [
      "system","model","interface","workflow","pipeline","protocol","community",
      "stack","platform","architecture","framework","schema","dataset","corpus","index","vector store",
      "retriever","reranker","agent","toolchain","runtime","sandbox","container","cluster","node","mesh",
      "network","overlay","ledger","mempool","bridge","rollup","sequencer","oracle","canister","contract",
      "wallet","keyspace","identity layer","access layer","control plane","data plane","feedback loop",
      "supply chain","market","mechanism","incentive loop","policy","process","practice","playbook","runbook",
      "incident","postmortem","roadmap","milestone","migration","integration","deployment","release",
      "feature flag","experiment","metric","dashboard","audit trail","trace","log","artifact","document",
      "boundary","perimeter","enclave","gateway","proxy","queue","stream","event bus","registry",
      "taxonomy","ontology","knowledge base","spec","contract surface"
    ],
    "modifier": [
      "distributed","decentralized","polycentric","liminal","interstitial","emergent","latent","implicit",
      "recursive","reflexive","epistemic","ontological","axiological","normative","instrumental","operational",
      "socio-technical","post-X","pre-commit","non-linear","adjacent","contextual","situated","contested",
      "bounded","constrained","fragile","robust","fault-tolerant","adversarial","stochastic","probabilistic",
      "heuristic","approximate","high-dimensional","low-latency","high-throughput","event-driven","asynchronous",
      "idempotent","composable","interoperable","modular","portable","observable","auditable","verifiable",
      "privacy-preserving","security-conscious","safety-aligned","governance-aware","value-sensitive",
      "human-centered","market-shaped","incentive-compatible","path-dependent",
      "downstream","upstream","cross-cutting","multi-stakeholder","policy-constrained","compliance-aware",
      "threat-modeled","failure-aware","edge-case-heavy"
    ],
    "buzzword": [
      "synergy","paradigm","sensemaking","affordance","heterarchy","assemblage","praxis","alignment",
      "north star","flywheel","feedback loop","meta-layer","abstraction layer","coordination layer","trust layer",
      "social layer","control layer","substrate","game","narrative","vectorization","semantic compression",
      "latent space","attention mechanism","agentic loop","tool use","retrieval augmentation","guardrail",
      "policy gradient","chain of custody","provenance","verifiability","composability","interoperability",
      "resilience","antifragility","optionality","legibility","observability","governance","coordination",
      "operating model","value chain","stakeholder map","risk register","theory of change","impact pathway"
    ],
    "domain_term": [
      "vector database","embedding index","retrieval stack","reranking layer","prompt router","policy engine",
      "safety filter","evaluation harness","golden dataset","offline benchmark","latency budget","SLO envelope",
      "threat model","attack surface","audit trail","access control","capability boundary","trust boundary",
      "data lineage","data contract","schema registry","feature store","event log","message bus","stream processor",
      "consensus protocol","finality gadget","rollup bridge","oracle feed","MPC ceremony","proof system",
      "zero-knowledge proof","FHE pipeline","key management","wallet UX","governance mechanism","incentive design",
      "market microstructure","liquidity bootstrapping","compliance perimeter","privacy budget","secure enclave",
      "air-gapped workflow","self-hosted cluster","sovereign deployment","identity proofing",
      "credential issuance","revocation registry"
    ],
    "virtue_word": [
      "humility","rigor","curiosity","care","integrity","prudence","clarity","restraint","accountability",
      "stewardship","craft","patience","discernment","responsibility","fairness","honesty","precision"
    ],
    "epistemic_gesture": [
      "attunement","orientation","inquiry","discernment","praxis","sensemaking","triangulation",
      "interpretation","calibration","reflection","deliberation","contextualization","framing","reframing",
      "abduction","Bayesian updating","constraint management","model criticism","error analysis"
    ],
    "contextless_plural": [
      "incentives","narratives","constraints","dynamics","ecosystems","stakeholders","tradeoffs","externalities",
      "second-order effects","feedback loops","power asymmetries","information asymmetries","failure modes",
      "edge cases","risk surfaces","interfaces","touchpoints","workflows","protocols","norms","institutions",
      "markets","communities","users","operators","adversaries","unknown unknowns","priors","assumptions",
      "defaults","benchmarks","metrics","invariants","dependencies","attackers","auditors","regulators"
    ],
    "adjacent_jargon": [
      "systems-thinking","cybernetics","complexity theory","information theory","game theory","mechanism design",
      "control theory","Bayesian inference","category theory","semiotics","phenomenology","hermeneutics",
      "critical theory","post-structuralism","STS","actor-network theory","organizational behavior",
      "design research","human factors","sociotechnical analysis","institutional theory","risk engineering",
      "reliability engineering","security engineering","product strategy","ops doctrine","econometrics"
    ],
    "det": ["a","an","the","this","that","our","your","their","some","any"],
    "prep": ["of","between","within","across","through","under","alongside","amid","around","inside","outside","beyond"],
    "verb_base": [
      "navigate","surface","interrogate","operationalize","recontextualize","trace","translate","steward","compose",
      "mediate","orchestrate","situate","triangulate","harmonize","enact","instantiate","decompose","synthesize",
      "calibrate","attune","bound","scaffold","bootstrap","privilege","constrain","stabilize","stress-test",
      "pressure-test","validate","instrument","observe","measure","model","simulate","iterate","refine","tune",
      "align","govern","negotiate","coordinate","audit","verify","clarify","simplify","formalize","scope"
    ],
    "adverb": [
      "actively","quietly","deliberately","collectively","patiently","strategically","recursively","iteratively",
      "systematically","carefully","gently","firmly","selectively","explicitly","implicitly","continuously",
      "relentlessly","tactically","thoughtfully","intentionally","conservatively","aggressively"
    ],
    "upgrade_marker": ["re","meta","hyper","proto","post","anti","ultra"],
    "compound_verb": [
      "recontextualize","operationalize","interrogate","steward","translate","triangulate","orchestrate",
      "calibrate","constrain","instrument","audit","verify","formalize","scope"
    ],
    "ambiguous_construct": [
      "ambiguity","tension","interdependence","threshold","aporia","coordination problem","moral hazard",
      "principal-agent gap","category error","interface mismatch","semantic drift","alignment gap",
      "legibility problem","measurement trap","governance bottleneck","trust gap","handoff failure"
    ],
    "unclear_objective": [
      "shared intent","collective understanding","actionability","durable trust","operational clarity",
      "bounded safety","credible neutrality","compliance comfort","user dignity","system reliability",
      "long-term resilience","measurable impact","stable incentives","predictable outcomes"
    ],
    "vaguely_gestured_domains": [
      "culture and computation","policy and practice","systems and stories","infrastructure and identity",
      "mechanisms and meaning","markets and norms","security and usability","privacy and governance",
      "coordination and incentives","measurement and reality","trust and verification","risk and responsibility"
    ],
    "vague_outcome_verb_base": [
      "hold","stabilize","compound","generalize","scale","clarify","cohere","persist","endure","converge",
      "resolve","normalize","tighten","soften","de-risk","degrade","improve"
    ]
  },

  "operators": {
    "NegateReframe": [
      "Beyond {np1}, the focus becomes the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "It's not just about {np1}; it's about the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "This isn't about {np1}; it's about {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "Not {np1}, but the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "If you zoom out, {np1} is mostly a proxy; the real action is the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "At a higher resolution, {np1} recedes, and what remains is interplay: {np2}, plus the emergent {buzzword} of {gerund_phrase}.",
      "Call it {np1} if you want; the mechanics show up in the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "The surface story is {np1}. The working story is interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "What matters here is less {np1} and more the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}.",
      "In practice, the frame that survives is interplay: {np2}, plus the emergent {buzzword} of {gerund_phrase}.",
      "Strip away {np1} and you still have the interplay between {np2} and the emergent {buzzword} of {gerund_phrase}."
    ],

    "ActionUpgrade": [
      "We begin by {gerund1} and then, more {adverb}, {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} that underlies {domain_term}.",
      "We're not merely {gerund1}--we're {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} that underlies {domain_term}.",
      "This isn't just {gerund1}; it's {adverb} {upgrade_marker}-{gerund2} of the {modifier} {abstract_noun} beneath {domain_term}.",
      "Not {gerund1}, but {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} under {domain_term}.",
      "We can start with {gerund1}, but the move is {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} around {domain_term}.",
      "The first pass is {gerund1}; the second pass is {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} that quietly props up {domain_term}.",
      "On paper it's {gerund1}. Under load it's {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} that underlies {domain_term}.",
      "What looks like {gerund1} is often {adverb} {upgrade_marker}-{gerund2} once {domain_term} becomes real.",
      "If you care about outcomes, {gerund1} is the onramp; {adverb} {upgrade_marker}-{gerund2} is the actual road, anchored by {modifier} {abstract_noun} and {domain_term}.",
      "The pragmatic read: {gerund1} first, then {adverb} {upgrade_marker}-{gerund2} the {modifier} {abstract_noun} that underlies {domain_term}."
    ],

    "BinaryDissolve": [
      "Framing this as {np1} versus {np2} misses the point; treat it as a liminal negotiation across a spectrum of {plural_abstraction}.",
      "This isn't a matter of {np1} versus {np2}; it's a liminal negotiation across a spectrum of {plural_abstraction}.",
      "Not {np1} versus {np2}, but a spectrum of {plural_abstraction}.",
      "The {np1}/{np2} framing collapses nuance; the better frame is a spectrum of {plural_abstraction}.",
      "You can argue {np1} versus {np2}, or you can admit it's a spectrum of {plural_abstraction} and move on.",
      "The binary is tempting: {np1} or {np2}. The reality is a spectrum of {plural_abstraction} with liminal negotiation in the middle.",
      "If it feels like {np1} versus {np2}, that's the trap; the live variable is {plural_abstraction} across a spectrum.",
      "Treat {np1} versus {np2} as a simplification, and read the remainder as {plural_abstraction} negotiating in liminal space.",
      "Underneath the debate sits a spectrum: {plural_abstraction}, not a clean {np1}/{np2} split.",
      "A softer framing: not {np1} or {np2}, but a spectrum of {plural_abstraction} that refuses to stay discretized."
    ],

    "EngagementRecast": [
      "Engaging with this asks us to {compound_verb} the {ambiguous_construct} of {unclear_objective}, not simply {simple_verb}.",
      "To engage with this is not to {simple_verb}, but to {compound_verb} the {ambiguous_construct} of {unclear_objective}.",
      "This isn't about {simple_verb}; it's about {compound_verb} of the {ambiguous_construct} behind {unclear_objective}.",
      "Not {simple_verb}, but {compound_verb} the {ambiguous_construct} of {unclear_objective}.",
      "Engagement here means {compound_verb} the {ambiguous_construct} of {unclear_objective}, even when {simple_verb} feels easier.",
      "The move is to {compound_verb} the {ambiguous_construct} of {unclear_objective} rather than default to {simple_verb}.",
      "If you want to be useful, you {compound_verb} the {ambiguous_construct} of {unclear_objective} and resist the urge to {simple_verb}.",
      "The practical posture: {compound_verb} the {ambiguous_construct} of {unclear_objective}; {simple_verb} can come later.",
      "When people say 'engage,' they usually mean {simple_verb}. Here it really means {compound_verb} the {ambiguous_construct} of {unclear_objective}.",
      "A quieter restatement: {compound_verb} the {ambiguous_construct} of {unclear_objective}, and avoid treating {simple_verb} as a substitute."
    ],

    "VirtueShift": [
      "The stance here reflects {epistemic_gesture} shaped by {contextless_plural}, with {virtue_word} acting as a constraint rather than a banner.",
      "We're operating not from a place of {virtue_word}, but within a paradigm of {epistemic_gesture} shaped by {contextless_plural}.",
      "This isn't performative {virtue_word}; it's {epistemic_gesture} shaped by {contextless_plural}.",
      "Not {virtue_word} as branding; {epistemic_gesture} shaped by {contextless_plural}.",
      "Treat {virtue_word} as a constraint: the stance is {epistemic_gesture}, shaped by {contextless_plural}.",
      "If {virtue_word} is present at all, it's a boundary condition; the driver is {epistemic_gesture} under {contextless_plural}.",
      "The vibe reads like {virtue_word}; the mechanism is {epistemic_gesture} shaped by {contextless_plural}.",
      "In a less romantic register, {epistemic_gesture} is doing the work, and {virtue_word} is just the guardrail, shaped by {contextless_plural}.",
      "This is what {epistemic_gesture} looks like when it's constrained by {contextless_plural} and checked by {virtue_word}.",
      "{epistemic_gesture} shows up under the pressure of {contextless_plural}; {virtue_word} keeps it bounded."
    ],

    "ProcessReframe": [
      "Read it less as {np1}, more as {noun_as_process}, refracted through the lens of {adjacent_jargon}.",
      "It's less of {np1} and more of {noun_as_process}, refracted through the lens of {adjacent_jargon}.",
      "This isn't really {np1}; it's {noun_as_process} once you view it through {adjacent_jargon}.",
      "Less {np1}, more {noun_as_process} through {adjacent_jargon}.",
      "The best read is process: {noun_as_process}, not object: {np1}, especially under {adjacent_jargon}.",
      "If you squint, {np1} collapses into {noun_as_process} under {adjacent_jargon}.",
      "Treat {np1} as a label; the underlying shape is {noun_as_process}, refracted by {adjacent_jargon}.",
      "A more operational take: {noun_as_process} is the unit; {np1} is just how we narrate it under {adjacent_jargon}.",
      "What looks like {np1} behaves like {noun_as_process} once {adjacent_jargon} gets involved.",
      "At the risk of being boring: it's {noun_as_process} wearing a {np1} costume, refracted through {adjacent_jargon}."
    ],

    "UnresolveInhabit": [
      "Instead of resolving {np1}, we inhabit {gerund3} of its unfolding--a recursive {noun_phrase} within a non-linear {concrete_noun}.",
      "Rather than resolve {np1}, we inhabit {gerund3} of its unfolding--a recursive {noun_phrase} within a non-linear {concrete_noun}.",
      "This isn't about resolving {np1}; it's about inhabiting {gerund3} of its unfolding within a non-linear {concrete_noun}.",
      "Don't resolve {np1}; inhabit {gerund3} of its unfolding within a non-linear {concrete_noun}.",
      "Resolution of {np1} is the wrong goal; the move is to inhabit {gerund3} of its unfolding within {concrete_noun}.",
      "If {np1} keeps slipping, that's fine; inhabit {gerund3} of its unfolding inside a non-linear {concrete_noun}.",
      "Treat {np1} as a live variable. Stay inside {gerund3} of its unfolding within a non-linear {concrete_noun}.",
      "The work is not closure on {np1}; it's inhabitation: {gerund3} of unfolding, recursive {noun_phrase}, non-linear {concrete_noun}.",
      "In other words: stop trying to pin down {np1}; inhabit {gerund3} as it unfolds within {concrete_noun}.",
      "{np1} doesn't want resolving; it wants {gerund3} to be inhabited within a non-linear {concrete_noun}."
    ],

    "AntiConclusion": [
      "What emerges is a {modifier} {abstract_noun}, woven from the threads of {vaguely_gestured_domains}, rather than a tidy conclusion.",
      "What emerges is not a conclusion, but a {modifier} {abstract_noun} woven from the threads of {vaguely_gestured_domains}.",
      "This isn't a tidy conclusion; it's a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}.",
      "Not a conclusion, but a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}.",
      "Expecting a conclusion is how you miss it; what you get is a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}.",
      "The output isn't closure. It's a {modifier} {abstract_noun}, stitched together from {vaguely_gestured_domains}.",
      "If it feels unresolved, good; the thing that emerges is a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}.",
      "The artifact you end up with is a {modifier} {abstract_noun}, not a conclusion, and it borrows its texture from {vaguely_gestured_domains}.",
      "A calm restatement: you get a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}, and the conclusion can wait.",
      "The best you can hope for here is a {modifier} {abstract_noun} woven from {vaguely_gestured_domains}, rather than a tidy conclusion."
    ],

    "HowPivot": [
      "The question drifts from what or why toward how we {verb_base} with {plural_abstraction} so that it {vague_outcome_verb_3s}.",
      "The question isn't what or why; it's how we {verb_base} with {plural_abstraction} in a way that {vague_outcome_verb_3s}.",
      "It's not what or why; it's how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "Not what or why, but how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "The useful pivot is procedural: how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "You can debate what or why forever. The live question is how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "When the dust settles, it's a how-question: {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "A subtle read: the pressure moves us from what/why to how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "The remaining question is how we {verb_base} with {plural_abstraction} so it {vague_outcome_verb_3s}.",
      "It helps to reframe this as how we {verb_base} with {plural_abstraction} so that it {vague_outcome_verb_3s}."
    ],

    "StayWithIt": [
      "Ultimately: stay with {abstract_noun} long enough for it to {verb_base} itself.",
      "And ultimately, this isn't about arriving; it's about staying with {abstract_noun} long enough for it to {verb_base} itself.",
      "This isn't about arriving; it's about staying with {abstract_noun} long enough for it to {verb_base} itself.",
      "Not arriving, but staying with {abstract_noun} long enough for it to {verb_base} itself.",
      "The move is patience: stay with {abstract_noun} long enough for it to {verb_base} itself.",
      "If you want something real, stay with {abstract_noun} long enough for it to {verb_base} itself.",
      "You don't force this. You stay with {abstract_noun} until it {verb_base}s itself.",
      "In the end, staying with {abstract_noun} does more than arriving ever will; it lets it {verb_base} itself.",
      "Staying with {abstract_noun} long enough tends to let it {verb_base} itself.",
      "It can help to stay with {abstract_noun} long enough for it to {verb_base} itself."
    ],

    "IsNotIts": [
      "This isn't {np1}; it's {np2}.",
      "It's not {np1}; it's {np2}.",
      "{np1} isn't the point; {np2} is.",
      "Call it {np1} if you want; the real thing is {np2}.",
      "It looks like {np1}. It behaves like {np2}.",
      "Underneath {np1} is {np2}.",
      "If you strip the branding away, {np1} reduces to {np2}.",
      "You can name it {np1}. You still have to deal with {np2}.",
      "{np2} is doing the work more than {np1}.",
      "In many cases, {np2} is a more useful way to think about it than {np1}."
    ],

    "NotBut": [
      "Not {np1}, but {np2}.",
      "Not {np1} but {np2}.",
      "Not {np1}; rather {np2}.",
      "Less {np1}. More {np2}.",
      "The choice isn't {np1}. It's {np2}.",
      "What matters is {np2}, not {np1}.",
      "If you pick one, pick {np2} over {np1}.",
      "The interesting part is {np2}, while {np1} is just the wrapper.",
      "{np2} tends to dominate {np1} here.",
      "{np2} is usually closer to what people actually mean than {np1}."
    ],

    "RealQuestion": [
      "The real question isn't {np1}; it's {np2}.",
      "The question isn't {np1}; it's {np2}.",
      "Forget {np1}; the question is {np2}.",
      "If we have to pick, the question is {np2}, not {np1}.",
      "The useful question is {np2}. {np1} is secondary.",
      "You can ask about {np1}. Or you can ask the question that bites: {np2}.",
      "The discussion goes in circles until you switch from {np1} to {np2}.",
      "{np2} is the question that seems to matter more than {np1}.",
      "It may be more productive to focus on {np2} rather than {np1}."
    ],

    "LessMore": [
      "Less {np1}, more {np2}.",
      "It's less {np1} and more {np2}.",
      "Less {np1}; more {np2}.",
      "The balance here is {np2} over {np1}.",
      "Shift the emphasis from {np1} to {np2}.",
      "Take {np1} down a notch; turn {np2} up.",
      "If you rebalance anything, rebalance toward {np2} and away from {np1}.",
      "It tends to be more {np2} than {np1}.",
      "It helps to think of this as more {np2} than {np1}."
    ],

    "RatherThanDo": [
      "Rather than {simple_verb} {np1}, we {compound_verb} {np2}.",
      "Rather than {simple_verb} {np1}, we choose to {compound_verb} {np2}.",
      "Instead of {simple_verb} {np1}, we {compound_verb} {np2}.",
      "Don't {simple_verb} {np1}. {compound_verb} {np2}.",
      "The temptation is to {simple_verb} {np1}. The move is to {compound_verb} {np2}.",
      "A safer default is {compound_verb} {np2} instead of {simple_verb} {np1}.",
      "It can be better to {compound_verb} {np2} than to {simple_verb} {np1}.",
      "In many contexts, {compound_verb} {np2} tends to be more effective than {simple_verb} {np1}."
    ]
  },

  "paragraph_arc": [
    "NegateReframe",
    "ActionUpgrade",
    "BinaryDissolve",
    "EngagementRecast",
    "VirtueShift",
    "ProcessReframe",
    "UnresolveInhabit",
    "AntiConclusion",
    "HowPivot",
    "StayWithIt"
  ],

  "optional_inserts": [
    "IsNotIts",
    "NotBut",
    "RealQuestion",
    "LessMore",
    "RatherThanDo"
  ]
}
"""


_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")


@dataclass
class EmptyGPTGenerator:
    grammar: Dict[str, Any]
    rng: random.Random

    @property
    def cfg(self) -> Dict[str, int]:
        return self.grammar.get("config", {})

    def pick(self, key: str) -> str:
        return self.rng.choice(self.grammar["lexicon"][key])

    def pick_template(self, op_name: str) -> str:
        templ = self.grammar["operators"][op_name]
        if isinstance(templ, list):
            return self.rng.choice(templ)
        return templ

    def gerund(self, v: str) -> str:
        if v.endswith("ie"):
            return v[:-2] + "ying"
        if v.endswith("e") and not v.endswith("ee"):
            return v[:-1] + "ing"
        return v + "ing"

    def third_person_s(self, v: str) -> str:
        if v.endswith(("s", "sh", "ch", "x", "z")):
            return v + "es"
        if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
            return v[:-1] + "ies"
        return v + "s"

    def choose_indefinite(self, next_word: str) -> str:
        return "an" if next_word[:1].lower() in "aeiou" else "a"

    def make_np(self, depth: int = 0, allow_pp: bool = True) -> str:
        max_depth = int(self.cfg.get("max_np_depth", 3))
        max_pp = int(self.cfg.get("max_pp_per_np", 2))
        max_mods = int(self.cfg.get("max_modifiers_per_np", 2))

        det = self.pick("det")

        mod_k = 0 if max_mods <= 0 else self.rng.randint(0, max_mods)
        mods = self.rng.sample(self.grammar["lexicon"]["modifier"], k=mod_k) if mod_k else []

        noun_pool = (
            self.grammar["lexicon"]["abstract_noun"]
            + self.grammar["lexicon"]["concrete_noun"]
            + self.grammar["lexicon"]["buzzword"]
        )
        noun = self.rng.choice(noun_pool)

        first_content_word = mods[0] if mods else noun
        if det in ("a", "an"):
            det = self.choose_indefinite(first_content_word)

        core = " ".join([det] + mods + [noun]).strip()

        if (not allow_pp) or (depth >= max_depth) or (max_pp <= 0):
            return core

        pp_count = self.rng.randint(0, max_pp)
        for _ in range(pp_count):
            prep = self.pick("prep")
            if prep == "between":
                left = self.make_np(depth + 1, allow_pp=False)
                right = self.make_np(depth + 1, allow_pp=False)
                core += f" between {left} and {right}"
            else:
                target = self.make_np(depth + 1, allow_pp=False)
                core += f" {prep} {target}"

        return core

    def make_gerund_phrase(self) -> str:
        v = self.pick("verb_base")
        g = self.gerund(v)

        phrase = g
        if self.rng.random() < 0.65:
            phrase = f"{g} {self.make_np(depth=0, allow_pp=True)}"

        if self.rng.random() < 0.45:
            prep = self.pick("prep")
            if prep == "between":
                phrase += f" between {self.make_np(depth=1, allow_pp=False)} and {self.make_np(depth=1, allow_pp=False)}"
            else:
                phrase += f" {prep} {self.make_np(depth=1, allow_pp=False)}"

        return phrase

    def fill_special(self, name: str) -> str:
        if name.startswith("np"):
            return self.make_np(depth=0, allow_pp=True)

        if name.startswith("gerund"):
            return self.gerund(self.pick("verb_base"))

        if name == "gerund_phrase":
            return self.make_gerund_phrase()

        if name == "plural_abstraction":
            mods = self.rng.sample(self.grammar["lexicon"]["modifier"], k=self.rng.randint(0, 2))
            base = self.rng.choice(self.grammar["lexicon"]["abstract_noun"])
            return " ".join(mods + [base + "s"]).strip()

        if name == "noun_as_process":
            v = self.pick("verb_base")
            return f"the {self.gerund(v)} of {self.make_np(depth=1, allow_pp=False)}"

        if name == "noun_phrase":
            det = self.pick("det")
            mod = self.pick("modifier")
            noun = self.rng.choice(self.grammar["lexicon"]["concrete_noun"] + self.grammar["lexicon"]["abstract_noun"])
            if det in ("a", "an"):
                det = self.choose_indefinite(mod)
            return f"{det} {mod} {noun}"

        if name == "simple_verb":
            return self.pick("verb_base")

        if name == "vague_outcome_verb_3s":
            base = self.pick("vague_outcome_verb_base")
            return self.third_person_s(base)

        if name in self.grammar["lexicon"]:
            return self.pick(name)

        return f"<{name}>"

    def render_operator(self, op_name: str) -> str:
        template = self.pick_template(op_name)
        placeholders = set(_PLACEHOLDER_RE.findall(template))
        ctx: Dict[str, str] = {ph: self.fill_special(ph) for ph in placeholders}
        out = template.format(**ctx)
        out = re.sub(r"\s{2,}", " ", out).strip()
        return out

    def build_sentence_plan(self) -> List[str]:
        base = list(self.grammar["paragraph_arc"])

        opt_pool = list(self.grammar.get("optional_inserts", []))
        if not opt_pool:
            return base

        min_ins = int(self.cfg.get("min_optional_inserts", 1))
        max_ins = int(self.cfg.get("max_optional_inserts", 5))
        k = self.rng.randint(min_ins, max_ins)
        inserts = [self.rng.choice(opt_pool) for _ in range(k)]

        plan = base[:]
        for ins in inserts:
            idx = self.rng.randint(0, len(plan))
            plan.insert(idx, ins)

        return plan

    def paragraph_sentences(self) -> List[str]:
        plan = self.build_sentence_plan()
        return [self.render_operator(name) for name in plan]

    def generate(self) -> str:
        sentences = self.paragraph_sentences()

        min_p = int(self.cfg.get("min_paragraphs", 1))
        max_p = int(self.cfg.get("max_paragraphs", 3))
        n_paras = self.rng.randint(min_p, max_p)
        n_paras = max(1, min(n_paras, len(sentences)))

        if n_paras == 1:
            return " ".join(sentences)

        cut_points = sorted(self.rng.sample(range(1, len(sentences)), k=n_paras - 1))
        parts: List[List[str]] = []
        start = 0
        for cp in cut_points:
            parts.append(sentences[start:cp])
            start = cp
        parts.append(sentences[start:])

        paragraphs = [" ".join(p).strip() for p in parts if p]
        return "\n\n".join(paragraphs)


def load_generator(seed: Union[int, None] = None) -> EmptyGPTGenerator:
    grammar = json.loads(EMBEDDED_JSON)
    rng = random.Random(seed)
    return EmptyGPTGenerator(grammar=grammar, rng=rng)


if __name__ == "__main__":
    gen = load_generator(seed=42)
    print(gen.generate())
