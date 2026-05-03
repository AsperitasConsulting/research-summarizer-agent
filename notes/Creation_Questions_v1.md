# Creation Questions v1

## Questions for the Project Owner

### Workshop Logistics

1. **Target audience skill level:** Are workshop attendees expected to be familiar with Python testing (pytest) already, or should the starter files include more extensive comments explaining pytest conventions (fixtures, parametrize, etc.)?
- **Answer:** Starter files should include extensive comments explaining pytest conventions.

2. **Workshop duration:** How long is the hands-on coding portion? This affects how many test stubs we include — too many and attendees won't finish; too few and fast attendees get bored.
- **Answer:** The session is 90 minutes. Let's assume that attendees will be coding for 30-45 minutes.

3. **Tavily key provisioning:** The spec mentions this as an open question. For Level 2 tests that call the real search tool, will attendees have a Tavily key? If not, should Level 2 tests use `StubSearchTool` for the search step but still call the real Anthropic API? That would test prompt effectiveness without requiring Tavily.
- **Answer:** A Tavily key is a requirement. They have a generous free tier. That said, we'll need to be able to stub the search tool for level 1 testing.

4. **Solution branch strategy:** The spec notes a folder vs. branch question. A `solution` branch is cleaner — it avoids attendees accidentally seeing answers. Should we use a branch named `solution` and keep the `solution/` directory out of the main branch entirely?
- **Answer:** Omit the solution for now. A `solution` branch will be used, but I'll use Claude Code in the same way attendees will to develop it.

### Technical Decisions

5. **Anthropic SDK version:** Which version of the `anthropic` Python SDK should we pin to? The structured output API surface has changed across versions. Pinning ensures all attendees get the same behavior.
- **Answer:** Pin to the latest stable version available at this time. I might upgrade closer to the presentation date in June.

6. **Python version floor:** The spec says >= 3.11. Should we also set a ceiling (e.g., < 3.14) to avoid compatibility surprises with bleeding-edge Python versions some attendees might have?
- **Answer:** Yes. Good idea.

7. **Pydantic v1 vs v2:** The spec recommends Pydantic but doesn't specify the version. Pydantic v2 is the current standard and has better performance, but some attendees may have v1 installed. Should we pin to v2 explicitly?
- **Answer:** Yes.  Pin to v2.

8. **Structured output mechanism:** The Anthropic SDK offers multiple ways to get structured output (tool use, JSON mode, response_model with instructor). The spec says "request structured output matching SummaryResult schema" but doesn't specify the mechanism. Should we use the SDK's native tool_use approach, or a library like `instructor`? Native tool_use is simpler and avoids an extra dependency.
- **Answer:** Let's use the native tool for simplicity.

### Content Decisions

9. **Sample outputs:** The spec mentions a `sample_outputs/` directory. Should these be JSON files, Python files, or both? How many examples should we include (I'm thinking 2-3 covering different topics)?
- **Answer:** JSON. 2-3 covering different topics.

10. **Level 1 exercises file:** The spec mentions `exercises/level1_prompts.md` with "suggested Claude Code prompts." Are these prompts the attendees would give to Claude Code to help them write tests, or prompts for the agent itself? If the former, we should craft them carefully to guide without giving away the answer.
- **Answer:** Prompts the attendees would give to Claude Code to help them write tests.

11. **LLM-as-judge eval scope:** The `evals/judge_eval.py` is described as "pre-built" for workshop Segment 5. Should it be a runnable script that attendees execute, or a walkthrough/demo the instructor runs? This affects how polished the output needs to be.
- **Answer:** While the instructor will run it, the students should be able to after should they want to.

### Defect Implementation

12. **Defect visibility:** For Option A (NoResultsError not raised), should the defect be obvious when reading the code (e.g., a missing `if` check), or subtly hidden (e.g., the check exists but has a logic error)? Obvious is better for teaching — attendees feel the "aha" moment of writing a test that catches a real gap.
- **Answer:** Make it obvious. The skill of the attendees is unknown.

13. **DEFECTS.md placement:** The spec says to commit `DEFECTS.md` only to the solution branch. Should it document just which option was chosen, or also include the fix? Including the fix makes it a complete reference for the instructor.
- **Answer:** Please include the fix.
