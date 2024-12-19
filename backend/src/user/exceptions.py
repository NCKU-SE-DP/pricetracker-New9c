class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class InvalidAccessTokenError(AuthenticationError):
    def __init__(self):
        self.message = "Invalid user access token."
        super().__init__(self.message)

class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        self.message = "Incorrect username or password."
        super().__init__(self.message)
