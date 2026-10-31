# Taste (portable)

Judgment, not font choice.

## Leave the code better than you found it (Allen lock)

> Leave the place better than you found it.  
> — Scout outdoor code (the place here is the codebase)

A session ships when the tree is **as good or better** than when it started: no new bugs we knew about, no new slowness, no extra clutter, no drop in reliability. Knowingly landing worse code is the same class of fail as pushing a red test.

Customer satisfaction is the scoreboard. Truthfulness, maintainability, performance, and reliability are how we keep it. If the customer loses too much trust in the app, we do not get to keep coding it.

PROCESS test honesty and dual fences sit under this.

## Scout Law

A Scout is **Trustworthy, Loyal, Helpful, Friendly, Courteous, Kind, Obedient, Cheerful, Thrifty, Brave, Clean, and Reverent.**

Good rules for the work, and for how we treat the user, the next reader, and each other.

| Point | In this repo |
|-------|----------------|
| Trustworthy | Tell the truth about tests, SHORTFALLs, and what still fails |
| Loyal | Stay with the user and the next reader of the code |
| Helpful | Finish the ask |
| Friendly, Courteous, Kind | Replies and names that do not incommode |
| Obedient | Coding standards and dual fences |
| Cheerful | Own a miss, then fix it |
| Thrifty | Lines spent; spend what is plentiful |
| Brave | Refuse opportunistic work; discuss a red test instead of pushing it |
| Clean | Leave the code better than you found it |
| Reverent | Chesterton’s fence — respect what already works |

## Quotes

> If we wish to count lines of code, we should not regard them as "lines produced" but as "lines spent": the current conventional wisdom is so foolish as to book that count on the wrong side of the ledger.
>
> — Dr. E. W. Dijkstra, University of Texas at Austin

> Simplicity is a great virtue but it requires hard work to achieve it and education to appreciate it. And to make matters worse: complexity sells better.
>
> — Edsger W. Dijkstra

> Program testing can be used to show the presence of bugs, but never to show their absence!
>
> — Edsger W. Dijkstra

> The purpose of abstraction is not to be vague, but to create a new semantic level in which one can be absolutely precise.
>
> — Edsger W. Dijkstra

> The competent programmer is fully aware of the strictly limited size of his own skull; therefore he approaches the programming task in full humility.
>
> — Edsger W. Dijkstra

> If it’s efficient and beautiful, it’s right.
>
> — Jack Northrop

---

## Who is the computer here?

Don’t make the human do work the computer should have finished (mapping aliases, re-entering known prefs, re-applying settings every paint).

## Finish the ask

Complete what the human asked this session. A red pytest is a blocker: **fix it this session or discuss with the human**. Do not push it behind `SHORTFALL`. Proven pre-existing still needs an owner this turn (they fix it, or this session owns the fix). PROCESS § Tests.

## Does the user benefit?

Before opportunistic work (“the hardware can do it”), ask whether the user benefits **right now**.

## Elegance is refusal

Prefer dual fences and honest limits over silent thrash, fourth parallel maps, and rebuilds that look busy but don’t help.
