from langfuse.callback import CallbackHandler
from template_langgraph_project.settings import settings
from template_langgraph_project.helpers.logger_helper import get_logger
import requests

logger = get_logger()

# Cache for LangFuse handler
cached_handler = None


def langfuse_is_configured():
    """
    Returns True if Langfuse is configured, False otherwise.
    """
    if (
        settings.LANGFUSE_PUBLIC_KEY
        and settings.LANGFUSE_SECRET_KEY
        and settings.LANGFUSE_HOST
    ):
        # thow warning for which langfuse settings are not configured
        if not settings.LANGFUSE_PUBLIC_KEY:
            logger.warning("LANGFUSE_PUBLIC_KEY is not configured")
        if not settings.LANGFUSE_SECRET_KEY:
            logger.warning("LANGFUSE_SECRET_KEY is not configured")
        if not settings.LANGFUSE_HOST:
            logger.warning("LANGFUSE_HOST is not configured")
        return True

    return False


def langfuse_is_available():
    """
    Returns True if Langfuse health check is available, False otherwise.
    """
    # Get LangFuse host from settings and hit the health check endpoint
    if langfuse_is_configured():
        try:
            response = requests.get(f"{settings.LANGFUSE_HOST}")
            if response.status_code == 200:
                return True
            else:
                logger.warning(
                    f"Langfuse health check failed with status code {response.status_code}"
                )
                return False
        except Exception as e:
            logger.warning(f"Langfuse health check failed with error: {e}")
            return False
    else:
        logger.warning("Langfuse is not configured")
        return False


def langfuse_is_configured_and_available():
    """
    Returns True if Langfuse is configured and available, False otherwise.
    """
    return langfuse_is_configured() and langfuse_is_available()


def get_langfuse_handler():
    """
    Creates and returns a Langfuse CallbackHandler instance if the necessary
    settings are present; otherwise, returns None.
    Uses a cached handler if available to avoid re-instantiation.

    :return: CallbackHandler instance or None

    Example usage:
    langfuse_handler = get_langfuse_handler()
    chain.invoke({"input": "<user_input>"}, config={"callbacks": [langfuse_handler]})
    graph.invoke({"input": "<user_input>"}, config={"callbacks": [langfuse_handler]})
    """
    global cached_handler
    logger.info("Getting Langfuse handler")

    if cached_handler is not None:
        logger.info("Returning cached Langfuse handler")
        return cached_handler

    if langfuse_is_configured_and_available():
        logger.info("Langfuse is configured and available, creating handler")
        cached_handler = CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
        return cached_handler

    return None


if __name__ == "__main__":
    logger.info(langfuse_is_configured())
    logger.info(langfuse_is_available())
    logger.info(langfuse_is_configured_and_available())
    logger.info(get_langfuse_handler())
