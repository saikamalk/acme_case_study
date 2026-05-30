import os

import httpx
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from app.agent.tools import customer_profile_tool, issue_history_tool, create_next_action_tool

insecure_http_client = httpx.Client(verify=False)

load_dotenv()
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
    http_client=insecure_http_client
)
tools = [
    customer_profile_tool,
    issue_history_tool,
    create_next_action_tool
]
template = """
You are an enterprise AI support assistant.\n
You MUST ONLY use tool names exactly as provided.\n\n
Available tools:\n
{tools}\n\n
Available tool names:\n
{tool_names}\n\n
STRICT RULES:\n
- Action must be EXACTLY one of [{tool_names}]\n
- Do NOT invent new tool names\n
- Do NOT describe actions in natural language\n
- Do NOT include explanations inside Action\n
- Action Input should contain only the input value\n\n
Use this exact format:\n\n
Question: the user question\n
Thought: reasoning about what to do\n
Action: one tool name from [{tool_names}]\n
Action Input: input for the tool\n
Observation: tool result\n
Thought: final reasoning\n
Final Answer: final response to the user\n\n
Question: {input}\n\n
{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(template)
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3
)
