from rag.llm import get_llm
from langchain.agents import create_agent
from agent.tools import (check_sanctions_list,get_vendor_credit_score,calculate_cross_border_tax,validate_fx_hedge,categorize_expense)
from agent.prompts import (RISK_AGENT_PROMPT,TAX_AGENT_PROMPT,CONTROL_AGENT_PROMPT,SYNTHESIS_PROMPT_TEMPLATE)
from logger import GLOBAL_LOGGER as log

# ==========================================
# LLM & AGENT CREATION
# ==========================================

llm = get_llm()


def create_specialized_agent(tools, system_prompt):
    """Creates a LangGraph react agent with the given tools and system prompt."""
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

# ==========================================
# INSTANTIATE AGENTS
# ==========================================

risk_agent = create_specialized_agent(
    [check_sanctions_list, get_vendor_credit_score],
    RISK_AGENT_PROMPT,
)

tax_agent = create_specialized_agent(
    [calculate_cross_border_tax, validate_fx_hedge],
    TAX_AGENT_PROMPT,
)

control_agent = create_specialized_agent(
    [categorize_expense],
    CONTROL_AGENT_PROMPT,
)



# ==========================================
# ORCHESTRATION (THE SUPERVISOR)
# ==========================================



class ProcurementSupervisor:
    def __init__(self):
        self.llm = llm

    def _invoke_agent(self, agent, request: str) -> str:
        """Invoke a LangGraph agent and extract the final AI message content."""
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request}]}
        )
        content = result["messages"][-1].content
        # create_react_agent may return content as a list of content blocks
        # e.g. [{'type': 'text', 'text': '...'}, ...]
        if isinstance(content, list):
            return "\n".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return content

    def run_audit(self, request: str) -> dict:
        log.info("Starting audit phase", phase="1 - Risk & Compliance")
        risk_result = self._invoke_agent(risk_agent, request)
        log.info("Phase complete", phase="Risk & Compliance", result=risk_result)

        log.info("Starting audit phase", phase="2 - Tax & Treasury")
        tax_result = self._invoke_agent(tax_agent, request)
        log.info("Phase complete", phase="Tax & Treasury", result=tax_result)

        log.info("Starting audit phase", phase="3 - Financial Control")
        control_result = self._invoke_agent(control_agent, request)
        log.info("Phase complete", phase="Financial Control", result=control_result)

        # Final Synthesis by the Supervisor (CFO)
        synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            risk_result=risk_result,
            tax_result=tax_result,
            control_result=control_result,
        )

        log.info("Starting audit phase", phase="4 - CFO Synthesis")
        cfo_memo = self.llm.invoke(synthesis_prompt).content
        log.info("CFO Synthesis complete", memo=cfo_memo)
        return {
            "risk_result": risk_result,
            "tax_result": tax_result,
            "control_result": control_result,
            "cfo_memo": cfo_memo,
        }



# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":
    supervisor = ProcurementSupervisor()

    complex_request = """
    Purchase Request:
    - Vendor: ShadowTrade LLC
    - Item: High-performance AI GPU Servers
    - Total Cost: 120,000 EUR
    - Destination: India Branch
    - FX Rate quoted: 1 EUR = 98 INR
    """

    final_memo = supervisor.run_audit(complex_request)
    log.info("Audit complete", memo=final_memo)