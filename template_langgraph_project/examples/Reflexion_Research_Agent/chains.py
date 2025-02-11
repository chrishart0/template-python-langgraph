# template_langgraph_project/examples/Reflexion_Research_Agent/chains.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from template_langgraph_project.helpers.llm import get_llm
from langchain_core.output_parsers import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.messages import HumanMessage
from datetime import datetime
from template_langgraph_project.examples.Reflexion_Research_Agent.schemas import (
    AnswerQuestion,
    ReviseAnswer,
)
from template_langgraph_project.helpers.logger_helper import get_logger

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

first_responder = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

revise_instructions = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
    - You MUST include numerical citations in your revised answer to ensure it can be verified.
    - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In the form of:
        - [1] https://example.com
        - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""

revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")


if __name__ == "__main__":
    logger.info("Starting the first responder chain...")
    human_message = HumanMessage(
        content="Write about AI startups in Chattanooga, TN,"
        " list startups that do that and raised capital."
    )
    chain = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
        | parser_pydantic
    )

    response = chain.invoke({"messages": [human_message]})

    result = response[0]
    # logger.info(result)
    # logger.info(result[0])

    # parse the result
    answer = result.answer
    reflection = result.reflection
    search_queries = result.search_queries

    print(result.model_dump())
    print("\n------------\n")

    logger.info(f"Answer: {answer}")
    logger.info(f"Reflection: {reflection}")
    logger.info(f"Search Queries: {search_queries}")

    print("\n------------\n")
