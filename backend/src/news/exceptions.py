class InvalidAIModelException(Exception):
    def __init__(self):
        self.message = 'Invalid AI model or misspelled. Allowed models: "open_ai", "anthropic".'
        super().__init__(self.message)
