# 09 · The audit agents (`backend/agent/`)

A RAG pipeline **answers questions**. An **agent** **does work**: it decides which tools to call, reads the results, and continues until it can give an answer.

## Concepts

| Term | Meaning |
|---|---|
| **Tool** | A Python function the model is allowed to call. The model reads its name, arguments and docstring to decide when to use it |
| **System prompt** | The standing instructions for an agent: role, responsibilities, how to decide, and exactly how to format the answer |
| **Agent** | A model + tools + a system prompt, running in a loop: think → call a tool → read the result → think again → answer |
| **Supervisor** | Ordinary Python code that runs several agents and combines their results |

## The five tools — `tools.py`

Each tool is a function marked with `@tool` from `langchain_core.tools`:

| Tool | Used by | What it does | Data source |
|---|---|---|---|
| `check_sanctions_list(vendor_name)` | Risk | Screens a vendor name against well-known sanctions lists | The model's general knowledge |
| `get_vendor_credit_score(vendor_name)` | Risk | Returns a score from 0–100 and a risk level (unknown vendors get 45) | The model's general knowledge |
| `calculate_cross_border_tax(amount, origin, destination)` | Tax | VAT/GST, import duty, total landed cost | The model's general knowledge |
| `validate_fx_hedge(currency_pair, rate_used)` | Tax | Compares the quoted exchange rate with the market rate; flags a difference above 5 % | **Live data** from `api.frankfurter.dev`; falls back to the model if it is unreachable |
| `categorize_expense(amount, item_description)` | Control | CapEx or OpEx, depreciation period, approval flags | The model's general knowledge |

> Four of the five tools ask the language model instead of calling real databases. That is a simplification for teaching. A real system would call a sanctions-screening service, a credit bureau, a tax engine, and so on.

How a tool is defined:

```python
@tool
def categorize_expense(amount: float, item_description: str) -> str:
    """Determines if the expense is Capital Expenditure (CapEx) or Operational (OpEx) using accounting standards."""
    ...
```

The docstring is part of the tool's description. The model uses it to decide when to call the tool, so write it clearly.

Each tool handles failure on its own. If the model call fails, it returns a message such as `SYSTEM WARNING: ... Manual review required.` rather than crashing the audit. Shared helpers: `_ask_llm()` (calls the model, catches errors) and `extract_text()` (normalises the reply).

## The prompts — `prompts.py`

There are four prompts. Each of the three agent prompts follows the same four parts:

1. **Role**: who the agent is
2. **Responsibilities**: what it is accountable for
3. **Decision framework**: which tool to call first, what thresholds to apply
4. **Output format**: an exact template for the answer

Example (shortened) from the risk prompt:

```
DECISION FRAMEWORK:
1. Run `check_sanctions_list` first — this is a hard blocker. A RED ALERT means immediate rejection.
2. Run `get_vendor_credit_score` next. Score ≥ 75 → LOW RISK ... Score < 50 → HIGH RISK ...

OUTPUT FORMAT — always respond in this exact structure:
SANCTIONS CHECK: [CLEARED / RED ALERT — reason]
CREDIT SCORE: [score] → [LOW / MODERATE / HIGH] RISK
...
```

A fixed output format makes the next step reliable. The CFO prompt looks for these exact words in the reports:

| Word | Comes from | Effect |
|---|---|---|
| `RED ALERT` | sanctions tool / risk prompt | Final decision: REJECTED |
| `FX ALERT` | exchange-rate tool | Final decision: CONDITIONAL HOLD |
| `HOLD FOR TREASURY AUDIT` | tax prompt | Final decision: CONDITIONAL HOLD |

If you rename one of these words, rename it everywhere.

All company details in the prompts (Aldermoor Industries, Hamburg, thresholds such as €250,000 and €1,000,000) are fictional.

## The supervisor — `agents.py`

Creating an agent takes one call:

```python
from langchain.agents import create_agent

def create_specialized_agent(tools, system_prompt):
    return create_agent(model=get_llm(), tools=tools, system_prompt=system_prompt)
```

The supervisor creates three agents, each with its own tools and prompt:

```python
self.risk_agent    = create_specialized_agent([check_sanctions_list, get_vendor_credit_score], RISK_AGENT_PROMPT)
self.tax_agent     = create_specialized_agent([calculate_cross_border_tax, validate_fx_hedge], TAX_AGENT_PROMPT)
self.control_agent = create_specialized_agent([categorize_expense], CONTROL_AGENT_PROMPT)
```

`run_audit()` runs them one after another and then asks the model for the CFO memo:

```python
risk_result    = self._invoke_agent(self.risk_agent, request)
tax_result     = self._invoke_agent(self.tax_agent, request)
control_result = self._invoke_agent(self.control_agent, request)

synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(risk_result=..., tax_result=..., control_result=...)
cfo_memo = extract_text(self.llm.invoke(synthesis_prompt).content)
```

Calling an agent means passing it a message list and reading the last message:

```python
result = agent.invoke({"messages": [{"role": "user", "content": request}]})
text = extract_text(result["messages"][-1].content)
```

Each phase is written to the log, so you can follow an audit in the terminal.

The agents run **sequentially**. They could run in parallel because they do not depend on each other. Sequential code is easier to read and debug.

### LangChain and LangGraph

`create_agent` is LangChain's standard way to build an agent. Internally it runs on **LangGraph**, which is why `langgraph` is listed in `requirements.txt` and appears in log output. This project does not write any LangGraph code. LangGraph itself is worth learning when you need loops, branches or shared state that a simple agent cannot express ([15](15-alternatives-and-next-steps.md)).

### Run the supervisor without the web server

From the `backend/` folder, with `GOOGLE_API_KEY` exported in your terminal (this run does not read `.env`, because `.env` is in the project root):

```bash
cd backend
GOOGLE_API_KEY=your-key python -m agent.agents
```

It audits a built-in sample request and prints the CFO memo.

## Things to know about agent output

- The model writes the text, so wording changes from run to run. The structure (headings and key words) should stay stable.
- Setting `LLM_TEMPERATURE=0` (the default) makes answers more repeatable. If a model repeats itself or loops, try `1.0`.
- A model can be wrong. Real audits keep a human in the loop.

## Try it yourself

1. Add a sixth tool, for example `check_delivery_risk(country: str)`, and give it to the control agent.
2. Change a threshold in `RISK_AGENT_PROMPT` (for example the 75 for "low risk") and run the same request again.
3. Submit a request with an exchange rate far from the market rate and read the CFO memo.
4. Remove the output-format section from one prompt. Compare the result and the CFO memo.
