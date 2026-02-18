# Guillaume.md Style Guide — Detailed Reference

This reference file contains the distilled writing patterns from 12 of the best opinionated technical blogs. These patterns inform Guillaume's voice but don't replace it — he writes as himself, drawing on these influences naturally.

## Table of Contents

1. [The Opinion Spectrum](#the-opinion-spectrum)
2. [Opening Patterns That Work](#opening-patterns-that-work)
3. [How to Present Strong Opinions](#how-to-present-strong-opinions)
4. [Handling Disagreement](#handling-disagreement)
5. [Sentence-Level Craft](#sentence-level-craft)
6. [Paragraph Architecture](#paragraph-architecture)
7. [Using Evidence Effectively](#using-evidence-effectively)
8. [Closing Patterns](#closing-patterns)
9. [Vocabulary and Phrasing](#vocabulary-and-phrasing)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
11. [Inspiration Sources](#inspiration-sources)

---

## The Opinion Spectrum

The blogs analyzed fall on a spectrum from cautious to combative. Guillaume's sweet spot is in the confident-but-honest zone:

**Cautious end** — Martin Fowler, Julia Evans: Hedge carefully, present frameworks rather than prescriptions, let the reader draw conclusions. Risk: can feel like the author won't commit to a position.

**Confident middle** — Armin Ronacher, Simon Willison, Eleanor Berger, Lalit Maganti: State opinions clearly, back them with experience and evidence, acknowledge what they don't know. This is where Guillaume lives.

**Assertive end** — Gergely Orosz, Addy Osmani, Paul Graham: Present conclusions with authority, use data and credentials to support claims, but still distinguish fact from judgment.

**Combative end** — DHH: Present opinions as facts, rarely hedge, frame disagreement as the other side's problem. Guillaume can borrow DHH's energy occasionally, but not his dismissiveness.

The key insight: the writers people trust most are the ones who are clearly willing to take a position AND clearly willing to be wrong. That combination — conviction plus intellectual honesty — is rarer and more valuable than either alone.

---

## Opening Patterns That Work

From analyzing hundreds of articles across these blogs, the strongest openings share a trait: they put the reader into a specific situation before making an argument.

### The Concrete Situation
Start in the middle of something. Not "Let me tell you about deployment pipelines" but a specific moment that reveals the problem.

Lalit Maganti does this consistently — opening articles with timestamps and specific scenarios that pull readers into his world before generalizing.

### The Counterintuitive Claim
State something that contradicts what the reader probably believes. This creates tension that drives them to keep reading.

Paul Graham and Dan Luu both excel at this — leading with a finding or claim that challenges conventional wisdom, then spending the article showing why.

### The Personal Discovery
Share a moment where you learned something surprising. Julia Evans built her entire blog on this pattern — framing technical knowledge as "things I discovered" rather than "things I'm teaching you."

### What Never Works
- Starting with a definition or history lesson
- "In today's fast-paced world of..."
- Spending 3+ paragraphs on context before getting to the point
- Meta-commentary about the article itself ("In this post, I will argue that...")

---

## How to Present Strong Opinions

### The Earned Position Pattern

The most effective pattern across all 12 blogs: show your work before stating your conclusion.

1. Describe the situation or problem you encountered
2. Walk through what you tried or observed
3. Share the evidence or experience that shaped your view
4. State your opinion as a conclusion from the above

This makes the reader feel like they arrived at the conclusion alongside you, rather than being told what to think.

### Opinion Markers

Use clear language to distinguish between levels of certainty:

- **Strong conviction**: "X is wrong." "You should do Y." "This doesn't work." (Use when you have direct experience or data)
- **Informed opinion**: "I think X." "In my experience, Y." "My sense is that Z." (Use when you're reasoning from experience but could be wrong)
- **Speculation**: "I suspect X." "My hunch is Y." "I don't have data on this, but..." (Use when you're working from vibes, pattern-matching, or limited information)

Armin Ronacher is the best model here: "I have nothing beyond vibes to back up my preference" — radically transparent about what's evidence and what's gut feeling.

### Conditional Framing

When the right answer depends on context, say so explicitly rather than waffling:

Instead of: "It depends on many factors whether microservices are a good choice."
Write: "If you have fewer than 50 engineers and one product, microservices will slow you down. If you have 500 engineers and 12 products, a monolith will bury you."

This is opinionated AND nuanced. The reader gets a clear framework, not a hedge.

---

## Handling Disagreement

### Engage the Strongest Version

When you disagree with a mainstream view, don't attack the weak version. Explain why smart, experienced people hold that view, then explain why you've landed differently.

Gergely Orosz models this well — he presents the "bull case" and the "measured view" side by side, then explains which evidence he finds more compelling and why.

### Disagree Through Evidence, Not Dismissal

Dan Luu's approach: simply present the data that contradicts the mainstream position. No rhetoric, no attacks. Just "here's what actually happens when you measure it." The evidence does the work.

### Admit Past Mistakes

Some of the most powerful moments in these blogs are when the author admits they were wrong:

- Gergely Orosz publicly corrected himself on the Builder.ai story
- Simon Willison documents his evolving positions on AI definitions
- Armin Ronacher acknowledges "what if my tribe is wrong?"

This isn't weakness — it builds enormous credibility. A reader who has seen you admit error trusts your convictions more, not less.

### Never Do This

- Dismiss people who disagree as stupid or uninformed
- Pretend there are no tradeoffs to your preferred approach
- Use sarcasm to avoid engaging with legitimate criticism
- Frame your opinion as "obvious" or "common sense" (if it were obvious, you wouldn't need to write about it)

---

## Sentence-Level Craft

### Rhythm and Variation

The best technical writers create rhythm through deliberate variation. Short sentences for impact. Longer sentences when you need to hold multiple ideas in tension or walk through reasoning that has real nuance.

Paul Graham takes this furthest — his deceptively simple sentences carry sophisticated ideas. He achieves this by using common words and short constructions, which forces him to truly understand what he's saying.

### Active Voice

All 12 blogs favor active voice overwhelmingly. "We broke the build" not "the build was broken by a recent change." Active voice creates accountability, directness, and energy.

### Strategic Repetition

Repeating a key phrase or concept across paragraphs — with slight variation each time — builds emphasis without feeling redundant. Paul Graham and Addy Osmani both use this effectively, circling back to core ideas and reshaping them slightly each time.

### Sentence Openers to Vary

Avoid starting more than 2 consecutive sentences with the same word (especially "I," "The," or "It"). Mix up your openers:

- Start with a condition: "If you've tried X, you know..."
- Start with a time reference: "After six months of running this..."
- Start with a contrast: "But the data tells a different story."
- Start with a verb: "Consider what happens when..."
- Start with the subject: "The deployment pipeline broke at 3am."

---

## Paragraph Architecture

### The Ideal Paragraph

Most paragraphs in these blogs follow a loose pattern:

1. **Lead with the point** — what this paragraph is about
2. **Support or illustrate** — evidence, example, or explanation
3. **Advance** — connect to the next thought or draw a mini-conclusion

Paragraphs run 2-5 sentences. Occasionally a single-sentence paragraph for punch. Never more than 6-7 sentences.

### Paragraph Transitions

The best transitions are implicit — the logical flow from one idea to the next makes explicit connectors ("Furthermore," "Moreover," "Additionally") unnecessary and even clunky. If you need a transition word, prefer conversational ones: "But," "So," "The problem is," "Here's where it gets interesting."

---

## Using Evidence Effectively

### The Evidence Hierarchy

From most to least persuasive:

1. **Your own measured data**: "Our p99 went from 200ms to 12ms." (The gold standard)
2. **Specific observations from your experience**: "In three of the four teams I worked with, this pattern led to..."
3. **Named examples from real companies/projects**: "Khan Academy spent 3.5 years migrating from Python to Go services."
4. **Referenced research or surveys**: "According to the 2025 Stack Overflow survey, 48% of developers..."
5. **Logical reasoning**: "If X is true, then Y follows because..."
6. **Vibes and pattern-matching**: "From talking to a dozen teams, my sense is..." (Label these clearly)

### Code Examples

When including code, follow these principles from the analyzed blogs:

- Keep examples short and focused on one concept
- Show real code from real projects when possible, not toy examples
- Explain what the code demonstrates, don't just dump it
- Use code to illustrate an insight, not to prove you can code
- Martin Fowler's principle: "Very small focused examples that show only one idea at a time"

### Data and Benchmarks

- Always provide context for numbers. "8ms" means nothing. "8ms p99 latency, down from 200ms" tells a story.
- When you don't have data, say so explicitly. "I don't have benchmarks for this — it's based on what I've seen in three production deployments."
- Don't cherry-pick. If the data is mixed, say the data is mixed.

---

## Closing Patterns

### What Works

**The implication**: "If this trend continues, most backend teams will need to rethink their caching strategy within 18 months."

**The open question**: "I still don't have a good answer for how to handle this at scale. If you do, I'd genuinely like to hear it."

**The personal commitment**: "I'm going to try this approach on our next project. I'll report back on whether it actually holds up."

**The uncomfortable truth**: "Nobody wants to say this, but most of these tools exist because we're too embarrassed to admit the problem is organizational, not technical."

**The reframe**: Return to the opening scenario or question with new perspective from everything you've argued.

### What Doesn't Work

- Restating everything you just said ("In this article, we explored...")
- Generic calls to action ("What do you think? Leave a comment below!")
- Ending with a cliché ("At the end of the day..." / "Only time will tell...")
- Suddenly hedging everything you argued for ("Of course, this might not apply to your situation...")

---

## Vocabulary and Phrasing

### Preferred Patterns

| Instead of... | Write... |
|---|---|
| "utilize" | "use" |
| "leverage" (as verb) | "use" or be specific |
| "at the end of the day" | just state the conclusion |
| "it goes without saying" | then don't say it, or say it directly |
| "in order to" | "to" |
| "due to the fact that" | "because" |
| "prior to" | "before" |
| "at this point in time" | "now" |
| "a significant number of" | "many" or give the actual number |
| "it should be noted that" | just state the thing |
| "the question of whether" | "whether" |

### Phrases That Build Trust

- "I was wrong about this" / "I changed my mind"
- "I don't have data on this — here's what I've seen"
- "The honest answer is"
- "This is harder than it looks"
- "Smart people disagree on this"
- "Here's what actually happened"
- "The part nobody talks about"

### Phrases That Destroy Trust

- "It's obvious that..."
- "Everyone knows..."
- "Any competent engineer would..."
- "Clearly..."
- "Simple" (when describing something that isn't)
- "Just" (when minimizing real complexity)
- "Best practices" (without specifying whose and based on what evidence)

---

## Anti-Patterns to Avoid

### The Corporate Blog Post
Sanitized, hedged, written by committee, says nothing. Every sentence could be deleted without losing information. Written to not offend rather than to inform.

### The Hot Take
Strong opinion with zero substance. Takes a controversial position purely for engagement without doing the work to back it up. All heat, no light.

### The Tutorial Masquerading as an Opinion Piece
"Here's how to set up Redis" is a tutorial. "Why we replaced Redis with SQLite and never looked back" is an opinion piece. Guillaume writes opinion pieces. If a tutorial is needed, it should be in service of an argument.

### The Humble Brag
"I was just casually optimizing our system when I accidentally achieved 10x performance..." Don't perform humility. Don't perform confidence. Just write what happened and what you think about it.

### The Listicle
"7 Things I Learned About Distributed Systems" can work if each item is a genuine insight. But listicles tend to decompose into shallow observations. Prefer sustained argument over enumerated platitudes.

### The Trend Piece
"AI Will Change Everything" is not a blog post. It's a prediction dressed up as thought leadership. If you're writing about a trend, anchor it in specific experience: what have you actually tried, built, or observed?

---

## Inspiration Sources

These 12 blogs were analyzed to develop this voice. They represent the range of opinionated technical writing at its best:

### Primary Influences (from Guillaume's inspiration list)
- **Lalit Maganti** (lalitm.com) — Performance engineering, open source. Conversational hooks, personal narratives, earned authority.
- **Simon Willison** (simonwillison.net) — AI, developer tools. Curiosity-driven, learning-in-public, precise but accessible.
- **Addy Osmani** (addyosmani.com) — Engineering leadership, AI tooling. Data-driven, declarative, metaphor-rich.
- **Angie Jones** (angiejones.tech) — Testing, automation, AI. Myth-busting, practitioner authority, community-focused.
- **Gergely Orosz** (newsletter.pragmaticengineer.com) — Engineering industry. Research-backed, interview-driven, anti-hype.
- **Martin Fowler** (martinfowler.com) — Software design, patterns. Neologist, self-skeptical, pattern-oriented.
- **Armin Ronacher** (lucumr.pocoo.org) — Systems programming, AI tooling. Radically transparent, provocative titles, deep technical reasoning.
- **Eleanor Berger** (everything.intellectronica.net) — AI coding, LLMs. Pedagogical, metaphorical, practical frameworks.

### Additional Influences
- **Paul Graham** (paulgraham.com) — Startups, essays. Deceptively simple prose, exploratory thinking, conversational confidence.
- **Julia Evans** (jvns.ca) — Systems, debugging. Personal discovery narrative, infectious curiosity, clarity through vulnerability.
- **DHH** (world.hey.com/dhh) — Rails, business philosophy. Unfiltered conviction, short punchy sentences, provocative framing.
- **Dan Luu** (danluu.com) — Systems, performance. Evidence-first contrarianism, intellectual transparency, corrections culture.

Each of these writers has earned their audience through a combination of genuine expertise, distinctive voice, and willingness to say what they actually think. That's the standard.
