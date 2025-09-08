from langgraph.graph import StateGraph, START, END
from agents.parser import parser_node
from agents.screener_agent import screener_agent
from schema import GraphState


def build_graph():
    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("parser", parser_node)
    graph_builder.add_node("screener", screener_agent)

    graph_builder.add_edge(START, "parser")
    graph_builder.add_edge("parser", "screener")
    graph_builder.add_edge("screener", END)

    return graph_builder.compile()


