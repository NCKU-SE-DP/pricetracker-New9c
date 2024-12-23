class CrawlerException(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DomainMismatchException(CrawlerException):
    """Exception raised for URLs whose domain does not match the news website's domain."""

    def __init__(
        self,
        url: str,
        message: str = "URL's domain does not match the news website's domain"):
        self.url = url
        self.message = message
        super().__init__(self.message)


class ParseException(CrawlerException):
    """Exception raised for errors during parsing."""
    def __init__(
        self,
        url: str,
        message: str = "An error occurred during parsing",
    ):
        self.url = url
        self.message = message
        super().__init__(self.message)


class ExtractionException(CrawlerException):
    """Exception raised for errors during extraction."""
    def __init__(
        self,
        url: str,
        message: str = "An error occurred during extraction",
    ):
        self.url = url
        self.message = message
