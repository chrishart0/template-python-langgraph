# template_langgraph_project/examples/Reflexion_Research_Agent/main.py
from typing import List
from langchain_core.messages import BaseMessage
from template_langgraph_project.helpers.graph_visualizer import save_graph_visualization
from langgraph.graph import END, MessageGraph

# Local imports
from template_langgraph_project.helpers.logger_helper import get_logger
from template_langgraph_project.examples.Reflexion_Research_Agent.chains import (
    revisor,
    first_responder,
)
from template_langgraph_project.examples.Reflexion_Research_Agent.tool_executory import (
    execute_tools,
)

logger = get_logger()

MAX_ITERATIONS = 2
builder = MessageGraph()

# Nodes
builder.add_node("draft", first_responder)
builder.add_node("execute_tools", execute_tools)
builder.add_node("revise", revisor)

# Edges
builder.set_entry_point("draft")
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")

# Create a LangGraph conditional edge to work in a loop for N number of iterations calling execute_tools on revise then revise from execute_tools


def should_continue(state: List[BaseMessage]):
    if len(state) > MAX_ITERATIONS * 2:
        return END
    return "execute_tools"


builder.add_conditional_edges("revise", should_continue)

graph = builder.compile()

# Save the graph visualization
save_graph_visualization(graph, source_file="Reflexion_Research_Agent-main.py")

if __name__ == "__main__":

    logger.info("Starting the research agent...")
    response = graph.invoke(
        "Write about AI startups in Chattanooga, TN, list startups that do that and raised capital."
    )
    logger.info(response)
    logger.info("\nResearch agent completed.\n")

    # Print the dict in a readable format
    logger.info("\n------------ All Steps  -----------\n")
    for step in response:
        logger.info(step.pretty_print())
