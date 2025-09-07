from langgraph.graph import StateGraph, START, END
from agents.screener import screener_node
from agents.parser import parser_node
from schema import GraphState


def build_graph():
    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("parser", parser_node)
    graph_builder.add_node("screener", screener_node)

    graph_builder.add_edge(START, "parser")
    graph_builder.add_edge("parser", "screener")
    graph_builder.add_edge("screener", END)

    return graph_builder.compile()


