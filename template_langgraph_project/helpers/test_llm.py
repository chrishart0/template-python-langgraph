import unittest
from unittest.mock import patch
from template_langgraph_project.helpers.llm import get_llm
from langchain_openai import AzureChatOpenAI, ChatOpenAI


class TestGetLLM(unittest.TestCase):
    def setUp(self):
        # Mocked settings as valid strings (for Pydantic validation)
        self.mock_settings = {
            "OPENAI_API_KEY": "valid_openai_key",  # pragma: allowlist secret
            "AZURE_OPENAI_API_KEY": "valid_azure_key",  # pragma: allowlist secret
            "AZURE_OPENAI_ENDPOINT": "https://valid.azure.endpoint",
            "AZURE_OPENAI_FAST_MODEL": "azure-fast-model",
            "AZURE_OPENAI_MODEL": "azure-default-model",
            "AZURE_OPENAI_REASONING_MODEL": "azure-reasoning-model",
            "AZURE_OPENAI_FAST_DEPLOYMENT_NAME": "azure-fast-deployment",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "azure-default-deployment",
            "AZURE_OPENAI_REASONING_DEPLOYMENT_NAME": "azure-reasoning-deployment",
            "AZURE_OPENAI_API_VERSION": "v1",
            "OPENAI_FAST_MODEL": "openai-fast-model",
            "OPENAI_MODEL": "openai-default-model",
            "OPENAI_REASONING_MODEL": "openai-reasoning-model",
        }

    @patch("template_langgraph_project.helpers.llm.settings")
    def test_azure_openai_fast_model(self, mock_settings):
        # Azure mock configuration
        mock_settings.AZURE_OPENAI_API_KEY = self.mock_settings["AZURE_OPENAI_API_KEY"]
        mock_settings.AZURE_OPENAI_ENDPOINT = self.mock_settings[
            "AZURE_OPENAI_ENDPOINT"
        ]
        mock_settings.AZURE_OPENAI_FAST_MODEL = self.mock_settings[
            "AZURE_OPENAI_FAST_MODEL"
        ]
        mock_settings.AZURE_OPENAI_FAST_DEPLOYMENT_NAME = self.mock_settings[
            "AZURE_OPENAI_FAST_DEPLOYMENT_NAME"
        ]
        mock_settings.AZURE_OPENAI_API_VERSION = self.mock_settings[
            "AZURE_OPENAI_API_VERSION"
        ]

        llm = get_llm(mode="fast")
        self.assertIsInstance(llm, AzureChatOpenAI)
        self.assertEqual(llm.deployment_name, "azure-fast-deployment")

    @patch("template_langgraph_project.helpers.llm.settings")
    def test_openai_default_model(self, mock_settings):
        # OpenAI-specific mock configuration
        mock_settings.OPENAI_API_KEY = self.mock_settings["OPENAI_API_KEY"]
        mock_settings.OPENAI_MODEL = self.mock_settings["OPENAI_MODEL"]

        # Exclude Azure settings to ensure OpenAI is prioritized
        mock_settings.AZURE_OPENAI_API_KEY = None
        mock_settings.AZURE_OPENAI_ENDPOINT = None
        mock_settings.AZURE_OPENAI_MODEL = None
        mock_settings.AZURE_OPENAI_FAST_MODEL = None
        mock_settings.AZURE_OPENAI_API_VERSION = None

        llm = get_llm(mode="default")

        self.assertIsInstance(llm, ChatOpenAI)

        # Check correct OpenAI model is assigned
        self.assertEqual(llm.model_name, "openai-default-model")


if __name__ == "__main__":
    unittest.main()
