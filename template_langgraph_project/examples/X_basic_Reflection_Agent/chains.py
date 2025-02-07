from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from template_langgraph_project.helpers.llm import get_llm

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a viral twitter influencer grading a x.com post. Generate critique and recommendations for the user's post."
            " Always provide detailed recommendations, including requests for length, virality, style, etc.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an x.com Gen AI influencer assistant tasked with writing excellent x.com posts."
            " Generate the best x.com post possible for the user's request."
            " If the user provides critique, respond with a revised version of your previous attempts.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


llm = get_llm()

generation_chain = generation_prompt | llm
reflection_chain = reflection_prompt | llm
