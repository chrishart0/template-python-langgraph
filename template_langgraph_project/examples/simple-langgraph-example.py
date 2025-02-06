# template_langgraph_project/examples/simple-langgraph-example.py

# Example modified from:
# https://langchain-ai.github.io/langgraph/tutorials/introduction/

from template_langgraph_project.settings import settings
from typing import Annotated

from typing_extensions import TypedDict

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

from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    model=settings.AZURE_OPENAI_MODEL,
    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
)


def chatbot(state: State):
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

while True:
    try:
        # Prompt for user input and style it nicely
        user_input = input(Text("You: ", style="bold magenta"))
        if user_input.lower() in ["quit", "exit", "q"]:
            console.print(Text("Goodbye!", style="bold red"))
            break

        stream_graph_updates_with_styles(user_input)
    except Exception as e:
        console.print(Text("An error occurred. Using fallback input...", style="bold yellow"))
        user_input = "What do you know about LangGraph?"
        stream_graph_updates_with_styles(user_input)
        break