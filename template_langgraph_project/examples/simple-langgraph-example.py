# template_langgraph_project/examples/simple-langgraph-example.py

# Example modified from:
# https://langchain-ai.github.io/langgraph/tutorials/introduction/

from typing import Annotated
from template_langgraph_project.helpers.llm import get_llm
from typing_extensions import TypedDict
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = get_llm(mode="fast")
model = "gpt-4o"


def chatbot(state: State):
    print("\nstate[messages]")
    print(state["messages"])
    print("-----------------\n")
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

console = Console()


### Chat Interface with Markdown and Colors ###
def stream_graph_updates_with_styles(user_input: str):
    if not user_input.strip():
        console.print(Text("Empty input. Please type something.", style="bold yellow"))
        return

    # Stream and display graph updates directly after user input
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            assistant_message = value["messages"][-1].content

            # Display assistant's message with markdown and style
            console.print(Text("Assistant:", style="bold green"))
            markdown_response = Markdown(assistant_message)
            console.print(markdown_response)
            # Line break and divider
            console.print(Text("\n", style="bold white"))


def visualize_graph():
    try:
        # Get the Mermaid diagram source
        mermaid_source = graph.get_graph().draw_mermaid()

        # Create markdown content with mermaid diagram
        markdown_content = f"""# LangGraph Visualization

```mermaid
{mermaid_source}
```
"""

        # Save to a markdown file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "graph.md", "w") as f:
            f.write(markdown_content)

        console.print(
            Text("\nGraph visualization saved to output/graph.md", style="bold green")
        )
        console.print(
            Text(
                "Open in VSCode and press Ctrl+Shift+V (Cmd+Shift+V on Mac) to preview\n",
                style="bold blue",
            )
        )
    except Exception as e:
        console.print(
            Text(f"Could not generate graph visualization: {e}", style="bold red")
        )


# Call this before starting the chat loop
visualize_graph()

while True:
    try:
        # Prompt for user input and style it nicely
        user_input = input(Text("You: ", style="bold magenta"))
        if user_input.lower() in ["quit", "exit", "q"]:
            console.print(Text("Goodbye!", style="bold red"))
            break

        stream_graph_updates_with_styles(user_input)
    except Exception as e:
        console.print(Text(f"Error: {e}", style="bold red"))
        console.print(
            Text("An error occurred. Using fallback input...", style="bold yellow")
        )
        user_input = "What do you know about LangGraph?"
        stream_graph_updates_with_styles(user_input)
        break
