import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.graph.state import AgentState
from app.config import settings
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8000/mcp/sse"
MAX_TOOL_ROUNDS = 3

mcp_client = MultiServerMCPClient(
    {"prodigy": {"url": MCP_SERVER_URL, "transport": "sse"}}
)


async def llm_node(state: AgentState) -> dict:
    try:
        tools = await mcp_client.get_tools()
        logger.info("MCP tools loaded", extra={"tools": [t.name for t in tools]})

        llm = ChatOpenAI(
            api_key=settings.ai_api_key,
            model=settings.ai_model,
            max_tokens=settings.ai_max_tokens,
            temperature=settings.ai_temperature,
        ).bind_tools(tools)

        system_content = load_prompt("system")
        messages = [SystemMessage(content=system_content)]

        for h in state.get("history", []):
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))

        user_message = state["user_message"]
        retry_prompt = state.get("retry_prompt")
        if retry_prompt:
            user_message = f"{user_message}\n\n[Системное напоминание: {retry_prompt}]"

        messages.append(HumanMessage(content=user_message))

        # Tool calling loop — the model can call tools several times in a row
        for round_num in range(MAX_TOOL_ROUNDS):
            response = await llm.ainvoke(messages)

            if not response.tool_calls:
                return {"final_answer": response.content}

            logger.info(
                "LLM requested tool calls",
                extra={"round": round_num, "tools": [t["name"] for t in response.tool_calls]},
            )
            messages.append(response)

            for tool_call in response.tool_calls:
                tool = next((t for t in tools if t.name == tool_call["name"]), None)
                if tool:
                    try:
                        result = await tool.ainvoke(tool_call["args"])
                        messages.append(
                            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                        )
                        logger.info("Tool call completed", extra={"tool": tool_call["name"]})
                    except Exception as exc:
                        logger.warning("Tool call failed", exc_info=exc)
                        messages.append(
                            ToolMessage(content=f"Ошибка: {exc}", tool_call_id=tool_call["id"])
                        )

        # If no final answer was produced within MAX_TOOL_ROUNDS — one last call without tools
        final_response = await llm.ainvoke(messages)
        return {"final_answer": final_response.content}

    except Exception as exc:
        logger.error("LLM generation failed", exc_info=exc)
        return {"error": str(exc), "final_answer": None}
