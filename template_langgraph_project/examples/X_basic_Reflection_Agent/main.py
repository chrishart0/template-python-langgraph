from typing import Sequence, List
from template_langgraph_project.helpers.logger_helper import get_logger
from template_langgraph_project.helpers.graph_visualizer import save_graph_visualization

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
from langchain_community.callbacks import get_openai_callback


from template_langgraph_project.examples.X_basic_Reflection_Agent.chains import (
    generation_chain,
    reflection_chain,
)

logger = get_logger()

REFLECT = "reflect"
GENERATE = "generate"


def generation_node(state: Sequence[BaseMessage]):
    logger.info("Generating post")
    with get_openai_callback() as cb:
        response = generation_chain.invoke({"messages": state})
        logger.info(
            f"Generation tokens: {cb.total_tokens} (Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens})"
        )
    return response


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    """
    Reflect on the post and return a new message to the user.
    Notice that we return a message as if it was from another human.
    This will get fed back to the generation node as a new message.
    """
    logger.info("Reflecting on post")
    with get_openai_callback() as cb:
        response = reflection_chain.invoke({"messages": messages})
        logger.info(
            f"Reflection tokens: {cb.total_tokens} (Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens})"
        )
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

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0

    with get_openai_callback() as cb:
        response = graph.invoke(inputs)
        total_prompt_tokens = cb.prompt_tokens
        total_completion_tokens = cb.completion_tokens
        total_cost = cb.total_cost

        logger.info("\nToken Usage Summary:")
        logger.info(f"Prompt tokens: {total_prompt_tokens}")
        logger.info(f"Completion tokens: {total_completion_tokens}")
        logger.info(f"Total tokens: {total_prompt_tokens + total_completion_tokens}")
        logger.info(f"Total cost: ${total_cost:.4f}")

    for message in response:
        print(message.content)
        print("\n")
