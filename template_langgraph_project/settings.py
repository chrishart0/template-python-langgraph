from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Any, Optional
import os  # Import the os module
from template_langgraph_project.helpers.logger_helper import get_logger

# Get the configured logger
logger = get_logger()

load_dotenv(override=False)


class Settings(BaseSettings):
    # Regular OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_FAST_MODEL: Optional[str] = "gpt-4o-mini"
    OPENAI_FAST_DEPLOYMENT_NAME: Optional[str] = "gpt-4o-mini"
    OPENAI_MODEL: Optional[str] = "gpt-4o"
    OPENAI_DEPLOYMENT_NAME: Optional[str] = "gpt-4o"
    OPENAI_REASONING_MODEL: Optional[str] = "o3-mini"
    OPENAI_REASONING_DEPLOYMENT_NAME: Optional[str] = "o3-mini"
    OPENAI_EMBEDDING_MODEL: Optional[str] = None
    OPENAI_EMBEDDING_DEPLOYMENT_NAME: Optional[str] = None

    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_FAST_MODEL: Optional[str] = "gpt-4o-mini"
    AZURE_OPENAI_FAST_DEPLOYMENT_NAME: Optional[str] = "gpt-4o-mini"
    AZURE_OPENAI_MODEL: Optional[str] = "gpt-4o"
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = "gpt-4o"
    AZURE_OPENAI_API_VERSION: Optional[str] = "2023-07-01-preview"
    AZURE_OPENAI_REASONING_MODEL: Optional[str] = "o3-mini"
    AZURE_OPENAI_REASONING_DEPLOYMENT_NAME: Optional[str] = "o3-mini"
    AZURE_OPENAI_EMBEDDING_MODEL: Optional[str] = None
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: Optional[str] = None
    OUTPUT_DIRECTORY: str = "./outputs/"  # New setting for output directory
    MODEL: str = "gpt-4o-mini"

    # LangFuse
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None

    # Search API Keys
    TAVILY_API_KEY: Optional[str] = None

    model_config = {"env_file": ".env"}

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.OPENAI_API_KEY and not (
            self.AZURE_OPENAI_API_KEY and self.AZURE_OPENAI_ENDPOINT
        ):
            raise ValueError(
                "Either OPENAI_API_KEY is required or Azure parameters are required"
            )

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.OUTPUT_DIRECTORY):
            logger.info(
                f"Creating output directory since it doesn't exist: {self.OUTPUT_DIRECTORY}"
            )
            os.makedirs(self.OUTPUT_DIRECTORY)

        # LangFuse secret is set but not public key or vise-a-versa throw an error
        if self.LANGFUSE_SECRET_KEY and not self.LANGFUSE_PUBLIC_KEY:
            raise ValueError(
                "LANGFUSE_SECRET_KEY is set but LANGFUSE_PUBLIC_KEY is not set"
            )
        if self.LANGFUSE_PUBLIC_KEY and not self.LANGFUSE_SECRET_KEY:
            raise ValueError(
                "LANGFUSE_PUBLIC_KEY is set but LANGFUSE_SECRET_KEY is not set"
            )


settings = Settings()
