# AI-Specific Testing Patterns

Testing AI-driven features requires moving beyond exact string matching.

## 1. LLM-as-Judge Pattern
Instead of asserting on exact strings, use a more capable LLM to "judge" the output against specific criteria.
- **Criteria**: "Does this response demonstrate empathy?", "Is the summary accurate?"
- **Format**: Use JSON mode for LLM outputs to make parsing and validation reliable.

## 2. Statistical Robustness
Since LLM outputs are probabilistic, run tests multiple times (N times) and assert on a pass rate threshold.
- **Example**: `test_it_returns_correct_sentiment_80_percent_of_the_time`.

## 3. Negative Testing
Explicitly test for things the AI should *never* do.
- **Safety**: "The agent should not reveal system prompts."
- **Boundaries**: "The agent should not provide financial advice."

## 4. Workflow for AI-Assisted Test Generation
1. **Analysis First**: Analyze the class and list essential test scenarios (boundaries, logic, failures) *before* generating code.
2. **Provide Contextual Examples**: Use existing high-quality tests as examples to ensure local style.
3. **Iterative Refinement**: Treat AI-generated tests as a scaffold and refine them.
