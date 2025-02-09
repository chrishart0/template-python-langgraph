# template_langgraph_project/examples/Reflexion_Research_Agent/chains.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from template_langgraph_project.helpers.llm import get_llm
from langchain_core.output_parsers import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.messages import HumanMessage
from template_langgraph_project.helpers.logger_helper import get_logger
from datetime import datetime
from template_langgraph_project.examples.Reflexion_Research_Agent.schemas import (
    AnswerQuestion,
)

logger = get_logger()

llm = get_llm(mode="fast")
parser = JsonOutputToolsParser(return_id=True)
parser_pydantic = PydanticToolsParser(tools=[AnswerQuestion])


actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be sever to maximize improvement.
3. Recommend search queries to research information and improve your answer.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    ]
).partial(time=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 word answer."
)

first_responder_chain = (
    first_responder_prompt_template
    | llm
    | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
)

if __name__ == "__main__":
    logger.info("Starting the first responder chain...")
    human_message = HumanMessage(
        content="Write about AI-Powered SOC / autonomous soc problem domain,"
        " list startups that do that and raised capital."
    )
    chain = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
        | parser_pydantic
    )

    result = chain.invoke({"messages": [human_message]})
    logger.info(result)
