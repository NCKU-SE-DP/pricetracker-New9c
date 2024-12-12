import aisuite as ai
from .template.base import LLMClientTemplate
class OpenAIClient(LLMClientTemplate):
    def __init__(self, api_key: str):
        super().__init__(api_key)
    def _initialize_client(self):
        self.client = ai.Client({"openai": {"api_key": self.api_key}})
        # self.model = "openai:gpt-4o"
        self.model = "openai:gpt-4o-mini"
