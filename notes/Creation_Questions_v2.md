# Creation Questions v2

Open items remaining after incorporating the v1 answers. None of these block scaffolding — they're refinements that shape the final attendee experience and the polish of supporting artifacts.

---

## Workshop Mechanics

1. **Attendee Tavily key sourcing.**
   Will each attendee sign up for their own free-tier Tavily key during the workshop, or should they be asked to sign up beforehand? Sign-up flow during a 90-minute workshop will eat into the coding budget. Suggest a "before you arrive" prerequisite step in the README.
    - **Answer:** They will be given requirements, including Claude and Tavily keys

2. **Anthropic key sourcing.**
   Same question as above for the Anthropic API key. Some attendees may be new to Anthropic's console and not have a billing-enabled key. Should we recommend a small prepaid balance ($5) as part of pre-work?
   - **Answer:** They will be given requirements, including Anthropic API keys

3. **Network constraints.**
   If the workshop runs in a venue with restrictive networking (some corporate offices block API calls), is there a fallback plan? Level 1 tests work fully offline with `StubSearchTool`, but Level 2 requires Anthropic + Tavily reachability.
   - **Answer:** The conference is providing free unrestricted wifi. This is not a concern.

---

## Defect Implementation

4. **Confirm "obvious by omission."**
   The v2 plan implements the defect as a missing block of code (no empty-results check), with no comment marker. Confirm this is the intended degree of obviousness, or whether you'd prefer a leading-marker comment such as `# (handle empty results before prompting)` to signal the gap.
   - **Answer:** Please place a comment.

5. **Single defect, or layered?**
   The spec says "at least one." Should this build seed only Option A, or should the plan also stage Options B and C as commented-out scaffolds the instructor could enable for advanced attendees?
   - **Answer:** Simplicity is better.  One defect.

---

## Sample Outputs

6. **Real vs synthetic URLs in `sample_outputs/`.**
   Should the citations in the JSON samples point to real, live URLs (and risk linkrot before June) or to clearly synthetic `https://example.com/...` URLs that won't decay but look less realistic?
   - **Answer:** Real, but common and unlikely to change.

7. **Sample count.**
   Two samples (photosynthesis, quantum computing) is the v2 default. Add a third (espresso brewing or similar) for variety, or keep it minimal?
   - **Answer:** Two is sufficient. Minimal works.

---

## LLM-as-Judge Eval

8. **Judge model choice.**
   The eval should use a model different from the agent. v2 plan suggests `claude-sonnet-4-6`. Confirm, or would you prefer a specific Sonnet pin and the same June re-check process used for Haiku?
   - **Answer:** Confirmed.

9. **Rubric scoring scheme.**
   Pass/fail per dimension is simplest. A 1–5 scale conveys more nuance but takes longer to explain on a workshop screen. Recommend pass/fail. Confirm.
   - **Answer:** Use pass/fail.

10. **Eval failure topic.**
    Should the eval be scripted to run against a topic where the agent typically passes the rubric (smooth demo) or where it sometimes fails (more honest, opens conversation about evaluation)? Recommend a topic that passes most runs but has discussable edge cases.
    - **Answer:** There won't be much time for discussion. I don't have recommendations without having the agent to experiment with.

11. **Trace artifact.**
    Should `judge_eval.py` write its output (agent result, judge prompt, judge response, scoring) to a file under `sample_outputs/` for attendees to review later, or only print to stdout?
    - **Answer:** Write the output so that the instructor can discuss using the solution branch if absolutely needed.

---

## Exercises

12. **Level 2 prompts file.**
    The spec only mentions `exercises/level1_prompts.md`. Given there's a Level 2 stub test as well, should we add a parallel `level2_prompts.md` with one or two prompt suggestions, or keep Level 2 unscaffolded to encourage attendees to extrapolate?
    - **Answer:** Yes, please add parallel prompts for all levels. Even though we won't be able to include all in the workshop, it might be useful for attendees to review on their own time.

13. **Prompt phrasing voice.**
    The Level 1 prompts will be presented as text an attendee pastes into Claude Code. Should they read as direct imperatives ("Write a test that...") or framed as a conversation ("I want to verify that...")? Imperatives are faster but less natural; conversational phrasing models good agent-collaboration habits.
    - **Answer:** I agree. Use conversational phrasing.

---

## README & Documentation

14. **Workshop walkthrough in README.**
    Should the README include a step-by-step "What to expect during the workshop" section, or stay narrowly focused on setup and run instructions? A walkthrough helps async readers but adds clutter for attendees who just need to get a green `verify_setup.py`.
    - **Answer:** Stay narrowly focused.

15. **Pin-refresh playbook.**
    The owner mentioned possibly upgrading dependencies closer to June. Should the README include the exact commands for that refresh (`pip install -U ... && pip freeze | grep ... > requirements.txt`) so it's a 30-second task instead of a fresh dependency audit?
    - **Answer:** Yes, include commands to make it a 30-second task.

---

## verify_setup.py

16. **Tavily reachability check.**
    Spec says "warn if absent, do not fail" for Tavily. If the key **is** present, should `verify_setup.py` make a free-tier search call to confirm the key is valid, or trust its presence? Validating costs a quota unit per attendee per run, but it surfaces typos early.
    - **Answer:** Trust the key.

17. **Output verbosity.**
    Should `verify_setup.py` print a single-line PASS/FAIL per check (clean), or include diagnostic detail (Python version number, SDK versions detected, etc.) for instructor screen-sharing?
    - **Answer:** Include diagnostic detail.

---

## Build & Versioning

18. **`requirements.txt` exact pins.**
    The plan recommends pinning specific versions captured at build time. Should we also generate a `requirements-lock.txt` (full transitive closure via `pip freeze`) for full reproducibility, or keep only the top-level pins?
    - **Answer:** Please also generate the requirements lock.

19. **Repository name.**
    The spec uses `research-summarizer/` in its layout, but the working directory is `research-summarizer-agent/`. Should we leave the working directory as-is (no rename) and document the mismatch, or rename one to match?
    - **Answer:** Please leave as is.

20. **License & attribution.**
    The repo already has a `LICENSE`. Should the README, sample outputs, and prompt files carry any specific attribution or workshop branding (organization name, event name, etc.)?
    - **Answer:** No.
