class LLMClientInitializeException(Exception):
    def __init__(
        self,
        message: str = "Failed to initialize LLM client",
    ):
        self.message = message
        super().__init__(self.message)

class EvaluationFailure(ValueError):
    def __init__(
        self,
        message: str = "Failed to evaluate the relevance of the news title with the prompt",
    ):
        self.message = message
        super().__init__(self.message)
