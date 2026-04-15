import os
from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_groq import ChatGroq
from tavily import TavilyClient
import requests
import psycopg2
from mcp import ClientSession
from langchain_mcp.adapters.client
from langgraph.types import interrupt, Command
from prompts import interpret_user_response_prompt

load_dotenv()


class GraphState(TypedDict):
    query: str
    web_results: List[str]
    git_results: List[str]
    db_results: List[str]
    steps: List[str]
    next_step: List[str]
    final_report: Optional[str]
    approved: Optional[bool]


llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))



#Orchestrator Node
def orchestrator(state: GraphState) -> str:
    """
    Decide next node dynamically based on query.

    """
    prompt = f"""
You are an orchestrator for a research workflow.

User query: {state['query']}
Current progress:
- Web results: {len(state['web_results'])}
- Git results: {len(state['git_results'])}

- DB results: {len(state['db_results'])}
- Steps done: {state['steps']}

Decide the next action:
- Analyze the user query and choose the correct node.
- Only return a single node name: "web", "db", or "summarize"
- Choose a node that is most relevant for the query.
- If enough information is collected, return "summarize".
- Do not return nodes unnecessarily.

Return ONLY the node name.
"""
    decision = llm.invoke(prompt).content.strip().lower()
    state["next_step"] = decision
    return state

# Web Search Node 
def web_search(state: GraphState) -> GraphState:
    response = tavily_client.search(query=state["query"], limit=5)
    urls_contents = [f"{r.get('url','')} | {r.get('content','')[:200]}" for r in response.get("results", [])]

    state["web_results"].extend(urls_contents)
    state["steps"].append("web")
    return state

# # Git Search Node 
# def git_search(state: GraphState) -> GraphState:
#     payload = {
#         "tool": "grep.search",
#         "args": {"query": state["query"], "limit": 5}
#     }
#     resp = requests.post("http://localhost:8603/mcp", json=payload)
#     resp.raise_for_status()
#     urls = [r["url"] for r in resp.json().get("results", []) if "url" in r]

#     state["git_results"].extend(urls)
#     state["steps"].append("git")
#     return state

def git_search(state):
    query = state["query"]

    # Directly pass command + args to ClientSession
    with ClientSession(
        command="uvx",
        args=["/home/web-h-009/grep-mcp/src/grep_mcp/__main__.py"]
    ) as session:
        session.initialize()

        # List tools (optional)
        print("Available tools:", session.list_tools())

        # Call the grep-mcp search tool
        result = session.call_tool(
            name="search",
            arguments={
                "query": query,
                "limit": 5
            }
        )

    matches = []
    for item in result.content:
        matches.append({
            "repo": item.get("repo"),
            "file": item.get("path"),
            "url": item.get("url"),
            "snippet": item.get("text"),
        })

    return {
        **state,
        "github_results": matches
    }


# DB Search Node 
def db_search(state: GraphState) -> GraphState:

    db_search_prompt= f"""

- Analyze the given query.
- Search the query related content in every table/row/column.
-


    """

    conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
    cur = conn.cursor()
    cur.execute(
        "SELECT report FROM reports WHERE query ILIKE %s LIMIT 5",
        (f"%{state['query']}%",)
    )
    rows = cur.fetchall()
    state["db_results"].extend([r[0] for r in rows])
    state["steps"].append("db")
    cur.close()
    conn.close()
    return state

# Summarize Node 
def summarize(state: GraphState) -> GraphState:
    prompt = f"""
- Create a final research report using available data.

WEB RESULTS:
{state['web_results']}

GIT RESULTS :
{state['git_results']}

DB RESULTS:
{state['db_results']}
"""
    report = llm.invoke(prompt).content
    state["final_report"] = report
    return state

# Human Approval Node 
def human_approval(state: GraphState) -> GraphState:
    if state.get("approved") is None:
        user_input = interrupt(
            {
                "question": "Would you like me to explore this further?",
                "options": []
            }
        )

        state["approved"] = user_input
        return state

    prompt = interpret_user_response_prompt.format_messages(
        user_input=state["approved"]
    )

    response = llm.invoke(prompt).content.strip().upper()
    state["approved"] = True if response == "YES" else False
    return state


# Save Node 
def save_to_db(state: GraphState) -> GraphState:
    conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reports (query, report) VALUES (%s, %s)",
        (state["query"], state["final_report"])
    )
    conn.commit()
    cur.close()
    conn.close()
    return state


graph_state = GraphState(
    query="",
    web_results=[],
    git_results=[],
    db_results=[],
    steps=[],
    final_report=None,
    approved=None
)

builder = StateGraph(GraphState)
builder.add_node("orchestrator", orchestrator)
builder.add_node("web", web_search)
builder.add_node("git", git_search)
builder.add_node("db", db_search)
builder.add_node("summarize", summarize)
builder.add_node("approve", human_approval)
builder.add_node("save", save_to_db)

# Graph flow
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges(
    "orchestrator",
    lambda s: s["next_step"],
    {
        "web": "web",
        "db": "db",
        "git": "git",
        "summarize": "summarize"
    }
)
builder.add_edge("web", "orchestrator")
builder.add_edge("git", "orchestrator")
builder.add_edge("db", "orchestrator")
builder.add_edge("summarize", "approve")
builder.add_conditional_edges(
    "approve",
    lambda s: "save" if s["approved"] else "end",
    {
        "save": "save",
        "end": END
    }
)
builder.add_edge("save", END)



if __name__ == "__main__":


    # resume_config ={
    #     "configurable": {
    #         "thread_id": "query"
    #     }
    # }

    with PostgresSaver.from_conn_string(os.getenv("POSTGRES_URL")) as checkpointer:

        checkpointer.setup()

        graph = builder.compile(checkpointer=checkpointer)

        graph.invoke({
            "query": input("Enter research topic: "),
            "web_results": [],
            "git_results": [],
            "db_results": [],
            "steps": [],
            "final_report": None,
            "approved": None
        },
        config = {
        "configurable": {
            "thread_id": "test-db-thread",
            "checkpoint_ns": "test",
          }
        }

    )

    # while True:
    #         snapshot = graph.get_state(resume_config)

    #         if not snapshot.interrupts:
    #             break

    #         payload = snapshot.interrupts[0].value
    #         print("\n" + payload["question"])
    #         user_input = input("→ ").strip()

    #         graph.invoke(
    #             Command(resume=user_input),
    #             config=resume_config,
    #         )

    # print("\nWorkflow completed")