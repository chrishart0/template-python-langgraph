from typing import Sequence, List
from template_langgraph_project.helpers.logger_helper import get_logger
from template_langgraph_project.helpers.graph_visualizer import save_graph_visualization

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph


from template_langgraph_project.examples.X_basic_Reflection_Agent.chains import (
    generation_chain,
    reflection_chain,
)

logger = get_logger()

REFLECT = "reflect"
GENERATE = "generate"


def generation_node(state: Sequence[BaseMessage]):
    logger.info("Generating post")
    return generation_chain.invoke({"messages": state})


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    """
    Reflect on the post and return a new message to the user.
    Notice that we return a message as if it was from another human.
    This will get fed back to the generation node as a new message.
    """
    logger.info("Reflecting on post")
    response = reflection_chain.invoke({"messages": messages})
    return [HumanMessage(content=response.content)]


builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)

builder.set_entry_point(GENERATE)


# Conditional edge to run generate reflect loop
def should_continue(state: List[BaseMessage]):
    if len(state) > 2:
        return END
    return REFLECT


builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)


graph = builder.compile()

save_graph_visualization(graph, source_file="X_basic_Reflection_Agent.py")


if __name__ == "__main__":
    inputs = [
        HumanMessage(content="Write a post about the benefits of using LangGraph")
    ]
    response = graph.invoke(inputs)
    for message in response:
        print(message.content)
        print("\n")
