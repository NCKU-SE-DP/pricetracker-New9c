import abc
from pydantic import BaseModel, Field
import aisuite as ai
from enum import Enum

class RelevanceEvaluation(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

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
    client: ai.Client = ...
    @abc.abstractmethod
    def _generate(self, prompt: PromptPassingInterface) -> str:
        """
        Generate response based on prompt.
        :param prompt:
        :return:
        """
        return NotImplemented
