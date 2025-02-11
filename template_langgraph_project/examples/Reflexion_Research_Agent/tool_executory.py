# template_langgraph_project/examples/Reflexion_Research_Agent/tool_executory.py
from template_langgraph_project.helpers.llm import get_llm
from template_langgraph_project.settings import settings
from typing import List
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from template_langgraph_project.helpers.logger_helper import get_logger
from template_langgraph_project.examples.Reflexion_Research_Agent.schemas import (
    AnswerQuestion,
    Reflection,
)
from template_langgraph_project.examples.Reflexion_Research_Agent.chains import parser
from langgraph.prebuilt import ToolInvocation
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolExecutor
from collections import defaultdict
import json

logger = get_logger()

llm = get_llm(mode="fast")

search = TavilySearchAPIWrapper(tavily_api_key=settings.TAVILY_API_KEY)
tavily_tool = TavilySearchResults(api_wrapper=search, max_results=1)
tool_executor = ToolExecutor(
    [tavily_tool]
)  # Allows us to batch tool invocations and run the async tool calls in parallel


def execute_tools(state: List[BaseMessage]) -> List[ToolMessage]:
    tool_invocation: AIMessage = state[-1]
    parsed_tool_calls = parser.invoke(tool_invocation)

    ids = []
    tool_invocations = []

    for parsed_tool_call in parsed_tool_calls:
        for query in parsed_tool_call["args"]["search_queries"]:
            logger.info(f"Executing tool with query: {query}")
            tool_invocations.append(
                ToolInvocation(tool="tavily_search_results_json", tool_input=query)
            )
            ids.append(parsed_tool_call["id"])

    outputs = tool_executor.batch(tool_invocations)

    # Map each output to its corresponding id and tool input
    outputs_map = defaultdict(dict)
    for id_, output, invocation in zip(ids, outputs, tool_invocations):
        outputs_map[id_][invocation.tool_input] = output

    # Convert the mapped outputs t ToolMessage objects
    tool_messages = []
    for id_, mapped_output in outputs_map.items():
        tool_messages.append(
            ToolMessage(content=json.dumps(mapped_output), tool_call_id=id_)
        )

    return tool_messages


if __name__ == "__main__":

    human_message = HumanMessage(
        content="Write about AI startups in Chattanooga, TN,"
        " list startups that do that and raised capital."
    )

    answer = AnswerQuestion(
        answer="",
        reflection=Reflection(missing="", superfluous=""),
        search_queries=[
            "Chattanooga AI startups funding rounds",
            "AI startups Chattanooga TN 2025",
            "venture capital in AI startups Chattanooga",
        ],
        id="call_asdRLKJHASDFLKJHASDFLKJH",
    )

    raw_response = execute_tools(
        state=[
            human_message,
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": AnswerQuestion.__name__,
                        "args": answer.model_dump(),
                        "id": "call_asdRLKJHASDFLKJHASDFLKJH",
                    }
                ],
            ),
        ]
    )

    print(raw_response)
