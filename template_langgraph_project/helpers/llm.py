# template_langgraph_project/helpers/llm.py

# This helper will give either Azure or regular OpenAI LLM based on the settings.py file
# Will handle fast model, regular model, reasoning model, embedding model

from template_langgraph_project.settings import settings
from template_langgraph_project.helpers.logger_helper import get_logger
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from typing import Literal
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register


logger = get_logger()

logger.info("Registering Phoenix tracer provider")
tracer_provider = register(
    project_name="template_langgraph_project",
    endpoint="http://localhost:6006/v1/traces",
)

logger.info("Instrumenting LangChain in Phoenix tracer provider")
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)


def get_llm(mode: Literal["fast", "default", "reasoning"] = "default"):
    """
    Returns the appropriate LLM based on settings configuration.

    Args:
        mode (str): The mode to use - "fast", "default", or "reasoning"

    Returns:
        OpenAI or AzureChatOpenAI: Configured LLM instance
    """

    # Check if both API keys are configured
    if settings.OPENAI_API_KEY and settings.AZURE_OPENAI_API_KEY:
        logger.warning(
            "Both OpenAI and Azure OpenAI are configured in .env file. Defaulting to Azure OpenAI."
        )

    # Use Azure if configured
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        model_mapping = {
            "fast": settings.AZURE_OPENAI_FAST_MODEL,
            "default": settings.AZURE_OPENAI_MODEL,
            "reasoning": settings.AZURE_OPENAI_REASONING_MODEL,
        }
        deployment_mapping = {
            "fast": settings.AZURE_OPENAI_FAST_DEPLOYMENT_NAME,
            "default": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            "reasoning": settings.AZURE_OPENAI_REASONING_DEPLOYMENT_NAME,
        }

        return AzureChatOpenAI(
            model=model_mapping[mode],
            deployment_name=deployment_mapping[mode],
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
        )

    # Fallback to regular OpenAI
    elif settings.OPENAI_API_KEY:
        model_mapping = {
            "fast": settings.OPENAI_FAST_MODEL,
            "default": settings.OPENAI_MODEL,
            "reasoning": settings.OPENAI_REASONING_MODEL,
        }

        print(f"Using OpenAI model: {model_mapping[mode]}")

        return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=model_mapping[mode])

    else:
        raise ValueError("No valid API configuration found in settings")
