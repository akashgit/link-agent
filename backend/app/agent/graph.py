from langgraph.graph import StateGraph

from app.agent.state import AgentState
from app.agent.nodes.research import research_node
from app.agent.nodes.draft import draft_node
from app.agent.nodes.generate_image import generate_image_node
from app.agent.nodes.optimize import optimize_node
from app.agent.nodes.proofread import proofread_node
from app.agent.nodes.approve import approve_node


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("research", research_node)
    graph.add_node("draft", draft_node)
    graph.add_node("generate_image", generate_image_node)
    graph.add_node("optimize", optimize_node)
    graph.add_node("proofread", proofread_node)
    graph.add_node("approve", approve_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft", "generate_image")
    graph.add_edge("generate_image", "optimize")
    graph.add_edge("optimize", "proofread")
    graph.add_edge("proofread", "approve")

    return graph
