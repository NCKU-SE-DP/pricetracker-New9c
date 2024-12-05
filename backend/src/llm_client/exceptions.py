class LLMClientInitializeException(Exception):
    def __init__(
        self,
        message: str = "Failed to initialize LLM client",
    ):
        self.message = message
        super().__init__(self.message)
