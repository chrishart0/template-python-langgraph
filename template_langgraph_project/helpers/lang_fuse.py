from langfuse.callback import CallbackHandler
from template_langgraph_project.settings import settings


def get_langfuse_handler():
    """
    Creates and returns a Langfuse CallbackHandler instance if the necessary
    settings are present; otherwise, returns None.

    :return: CallbackHandler instance or None

    Example usage:
    langfuse_handler = get_langfuse_handler()
    chain.invoke({"input": "<user_input>"}, config={"callbacks": [langfuse_handler]})
    graph.invoke({"input": "<user_input>"}, config={"callbacks": [langfuse_handler]})
    """
    if (
        settings.LANGFUSE_PUBLIC_KEY
        and settings.LANGFUSE_SECRET_KEY
        and settings.LANGFUSE_HOST
    ):
        return CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
    return None


# Example usage:
langfuse_handler = get_langfuse_handler()
