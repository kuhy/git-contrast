from enum import Enum, auto


class IssueType(Enum):

    FORMAT = auto()
    DOCUMENTATION = auto()


class Issue(Enum):

    def __init__(self, issue_type: IssueType, description: str):
        self.issue_type = issue_type
        self.description = description

    LINE_TOO_LONG = IssueType.FORMAT, "Line too long"
    MISSING_CLASS_DOCSTRING = IssueType.DOCUMENTATION, "Missing class docstring"
    MISSING_FUNCTION_DOCSTRING = IssueType.DOCUMENTATION, "Missing function or method docstring"
