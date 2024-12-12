from abc import ABC, abstractmethod
from typing import Optional
import json
from ..base import LLMClientBase, PromptPassingInterface, RelevanceEvaluation
from ..exceptions import EvaluationFailure
class LLMClientTemplate(LLMClientBase, ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model: str = ...
        self._initialize_client()
    #initialize client function should be abstract
    @abstractmethod
    def _initialize_client(self):
        ...
    def _generate(self, prompt: PromptPassingInterface) -> Optional[str]:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=prompt.to_dict,
            )
            return completion.choices[0].message.content
        except Exception as error:
            raise EvaluationFailure(f"An API error occurred: {error}")
    def extract_search_keywords(self, prompt: str) -> str|None:
        """
        Extract search keywords from the prompt.
        :param prompt:
        :return:
        """
        return self._generate(PromptPassingInterface(
            system_content="你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
            user_content=prompt
        ))
    def generate_summary(self, prompt: str) -> Optional[dict[str, str]]:
        """
        Generate a summary based on the prompt.
        :param prompt:
        :return:
        """
        response = self._generate(PromptPassingInterface(
            system_content='你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {"影響": "...", "原因": "..."})，並請確保返回有效 json 格式',
            user_content=prompt,
        ))
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise EvaluationFailure(f"Failed to generate a summary based on the prompt: {prompt}")
    def evaluate_relevance(self, news_title: str, prompt: str = "民生用品的價格變化") -> Optional[RelevanceEvaluation]:
        """
        Evaluate the relevance of the news title with the prompt.
        :param news_title:
        :param prompt:
        :return:
        """
        response = self._generate(PromptPassingInterface(
            system_content=f"你是一個關聯度評估機器人，請評估新聞標題是否與「{prompt}」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            user_content=news_title
        ))
        try:
            return RelevanceEvaluation(response)
        except ValueError:
            raise EvaluationFailure(f"Failed to evaluate the relevance of the news title with the prompt: {response}")
