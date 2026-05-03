---
name: Creation Questions v5
description: Residual micro-tactical questions after v4 answers were folded into the plan; safe defaults exist for all of them, none block scaffolding
type: project
---

# Creation Questions v5

The v4 round closed every structural and semantic decision. This file contains only two micro-tactical questions about `scripts/check_sample_urls.py` (both surfaced once GET was locked in by Q3 v4) plus a final sign-off prompt.

**Each question below has a safe default.** If no answer arrives before scaffolding starts, the agent team will use the default, note the choice in the file's header comment, and proceed.

---

## `scripts/check_sample_urls.py` HTTP-Client Detail

1. **User-Agent header.**
   `urllib`'s default `Python-urllib/3.X` is throttled or outright blocked by Wikipedia and several academic publishers. A polite custom UA avoids false negatives.
   - **A.** `User-Agent: research-summarizer-link-check/1.0` (plan default — descriptive, no PII, identifies the script's purpose).
   - **B.** A different string: ___
   - **C.** Use the `urllib` default (accept the false-negative risk on Wikipedia / NIH PMC).
   - **Plan default:** A.
   - **Answer:**

2. **Per-request timeout.**
   `urllib.urlopen` defaults to no timeout. With ~7–8 citation URLs across the two sample files, an aggressive wall keeps the script bounded.
   - **A.** 5 seconds (plan default — fast enough that a missed-key user notices, slow enough to tolerate a sluggish CDN response).
   - **B.** 10 seconds (matches the spec's Tavily timeout).
   - **C.** A different value: ___
   - **Plan default:** A.
   - **Answer:**

---

## Sign-off

3. **Is the v5 plan ready for scaffolding?**
   The v4 round was tagged "no scaffolding-blockers." With the v4 answers folded in and the two questions above defaulted, every decision needed to begin Phase 1 has been made.
   - **A.** Yes — proceed to Phase 1 (project scaffolding) immediately on owner approval.
   - **B.** Hold — additional review needed: ___
   - **Plan default:** A.
   - **Answer:**
