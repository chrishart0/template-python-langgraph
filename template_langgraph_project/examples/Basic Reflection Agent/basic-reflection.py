# template_langgraph_project/examples/Reflection Agent/basic-reflection.py

# https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/reflection/reflection.ipynb

# This simple type of reflection can sometimes improve performance by
#   giving the LLM multiple attempts at refining its output and
#   by letting the reflection node adopt a different persona while critiquing the output.
#   However, since the reflection step isn't grounded in any external process,
#   the final result may not be significantly better than the original.


from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Annotated
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from template_langgraph_project.helpers.llm import get_llm
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from template_langgraph_project.helpers.graph_visualizer import save_graph_visualization

### Setup ###
llm = get_llm(mode="fast")
console = Console()


### Prompts ###
# Updated generation prompt for shorter outputs.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a writer assistant tasked with writing concise and engaging x.com posts. "
            "Your posts are short, impactful, and designed to grab attention quickly. "
            "Generate a brief yet compelling post or thread for the user's request. "
            "If the user provides critique, deliver a revised version that remains succinct.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generate = prompt | llm

# Updated reflection prompt for concise feedback.
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an X.com poster known for your elegant style. "
            "Review the submitted post by providing brief, clear critique and specific suggestions for improvement. "
            "Keep your feedback short and actionable to enhance engagement.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
reflect = reflection_prompt | llm

### LangGraph Implementation ###


class State(TypedDict):
    messages: Annotated[list, add_messages]


async def generation_node(state: State) -> State:
    return {"messages": [await generate.ainvoke(state["messages"])]}


async def reflection_node(state: State) -> State:
    # Other messages we need to adjust
    cls_map = {"ai": HumanMessage, "human": AIMessage}
    # First message is the original user request. We hold it the same for all nodes
    translated = [state["messages"][0]] + [
        cls_map[msg.type](content=msg.content) for msg in state["messages"][1:]
    ]
    res = await reflect.ainvoke(translated)
    # We treat the output of this as human feedback for the generator
    return {"messages": [HumanMessage(content=res.content)]}


builder = StateGraph(State)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_edge(START, "generate")


def should_continue(state: State):
    if len(state["messages"]) > 4:
        # End after 2 iterations
        return END
    return "reflect"


builder.add_conditional_edges("generate", should_continue)
builder.add_edge("reflect", "generate")
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
# Add visualization of the graph
save_graph_visualization(graph, source_file="basic-reflection.py")

config = {"configurable": {"thread_id": "1"}}


async def stream_graph_updates_with_styles(user_input: str, config: dict):
    # Using async API, with improved console printout using rich
    async for event in graph.astream(
        {"messages": [HumanMessage(content=user_input)]},
        config,
    ):
        # Pretty print the event with rich styling
        key = list(event.keys())[0]
        console.print(Text(f"========== {key} ==========", style="bold blue"))
        console.print(Markdown(event[key]["messages"][-1].content))
        console.print(Text("==================================\n", style="bold blue"))


if __name__ == "__main__":
    asyncio.run(
        stream_graph_updates_with_styles(
            user_input="Generate an x.com post about LangGraph", config=config
        )
    )
