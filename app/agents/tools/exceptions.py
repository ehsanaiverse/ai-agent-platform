"""
Custom exceptions for the Tool Framework.

These exceptions are intentionally framework-specific so that callers
can distinguish tool-related failures from generic Python exceptions.
"""


class ToolError(Exception):
    """
    Base exception for all tool-related errors.
    """

    pass


class ToolNotFoundError(ToolError):
    """
    Raised when a requested tool does not exist in the registry.
    """

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' is not registered.")


class DuplicateToolRegistrationError(ToolError):
    """
    Raised when attempting to register a tool with a name
    that already exists in the registry.
    """

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        super().__init__(
            f"Tool '{tool_name}' is already registered."
        )


class InvalidToolError(ToolError):
    """
    Raised when an object cannot be registered as a tool.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)