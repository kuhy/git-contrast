from abc import ABC, abstractmethod
from git_contrast import Issue


class LinterResult:

    def __init__(self, number_of_issues=None):
        if number_of_issues:
            self.number_of_issues = number_of_issues
        else:
            self.number_of_issues = {issue: 0 for issue in Issue}

    def __add__(self, other):
        number_of_issues = {issue: self.number_of_issues[issue] + other.number_of_issues[issue]
                            for issue in Issue}
        return LinterResult(number_of_issues)

    def __sub__(self, other):
        number_of_issues = {issue: self.number_of_issues[issue] - other.number_of_issues[issue]
                            for issue in Issue}
        return LinterResult(number_of_issues)

    def __neg__(self):
        return LinterResult({issue: -self.number_of_issues[issue] for issue in Issue})


class Linter(ABC):

    @abstractmethod
    def lint(self, filename: str) -> LinterResult:
        pass
