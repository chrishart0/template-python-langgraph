# template_langgraph_project/examples/simple-langgraph-example.py

# Example modified from:
# https://langchain-ai.github.io/langgraph/tutorials/introduction/

from typing import Annotated
from template_langgraph_project.helpers.llm import get_llm
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from template_langgraph_project.helpers.graph_visualizer import save_graph_visualization
from template_langgraph_project.helpers.logger_helper import get_logger

logger = get_logger()


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


# Prepare persistent memory
memory = MemorySaver()

# Pass the initial state to the StateGraph constructor.
graph_builder = StateGraph(State)

llm = get_llm(mode="fast")


def chatbot(state: State):
    # Optionally, you can print or log the full conversation so far:
    print("\nCurrent State Messages:")
    print(state)
    print("-----------------\n")
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

logger.info("Compiling graph")
graph = graph_builder.compile(checkpointer=memory)

console = Console()


### Chat Interface with Markdown and Colors ###
def stream_graph_updates_with_styles(user_input: str, config: dict):
    if not user_input.strip():
        console.print(Text("Empty input. Please type something.", style="bold yellow"))
        return

    # Stream and display graph updates directly after user input
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values",
    ):
        # event["messages"][-1].pretty_print()
        assistant_message = event["messages"][-1].content
        # Display assistant's message with markdown and style
        console.print(Text("Assistant:", style="bold green"))
        markdown_response = Markdown(assistant_message)
        console.print(markdown_response)
        # Line break and divider
        console.print(Text("\n", style="bold white"))


# Instead of calling visualize_graph(), now call save_graph_visualization(graph)
save_graph_visualization(graph)

while True:
    # Tell LangGraph to use a specific thread ID for chat history
    config = {"configurable": {"thread_id": "1"}}
    try:
        # Prompt for user input and style it nicely
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            console.print(Text("Goodbye!", style="bold red"))
            break

        stream_graph_updates_with_styles(user_input, config)
    except Exception as e:
        console.print(Text(f"Error: {e}", style="bold red"))
        console.print(
            Text("An error occurred. Using fallback input...", style="bold yellow")
        )
        fallback_input = "What do you know about LangGraph?"
        stream_graph_updates_with_styles(fallback_input, config)
        break
