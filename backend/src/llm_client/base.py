import abc
from pydantic import BaseModel, Field
from openai import OpenAI
class PromptPassingInterface(BaseModel):
    system_content: str = Field(...)
    user_content: str = Field(...)
    @property
    def to_dict(self):
        value = [
            {"role": "system", "content": f"{self.system_content}"},
            {"role": "user", "content": f"{self.user_content}"},
        ]
        return value
class LLMClientBase(metaclass=abc.ABCMeta):
    openai_client: OpenAI | None
    @abc.abstractmethod
    def _generate(self, prompt: PromptPassingInterface) -> str:
        """
        Generate response based on prompt.
        :param prompt:
        :return:
        """
        return NotImplemented
