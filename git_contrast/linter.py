from abc import ABC, abstractmethod


class LinterResult:

    def __init__(self, number_of_issues=None):
        if number_of_issues:
            self.number_of_issues = number_of_issues
        else:
            self.number_of_issues = {}

    def __add__(self, other):
        return self.zip(other, int.__add__)

    def __sub__(self, other):
        return self.zip(other, int.__sub__)

    def zip(self, other, operation):
        # TODO: use built-in zip function
        issues = set(self.number_of_issues.keys())
        issues = issues.union(set(other.number_of_issues.keys()))
        number_of_issues = {}
        for issue in issues:
            pre = (self.number_of_issues[issue] if
                   issue in self.number_of_issues.keys() else 0)
            post = (other.number_of_issues[issue] if
                    issue in other.number_of_issues.keys() else 0)
            number_of_issues[issue] = operation(pre, post)
        return LinterResult(number_of_issues)

    def __neg__(self):
        return LinterResult({issue: -self.number_of_issues[issue]
                             for issue in self.number_of_issues.keys()})


class Linter(ABC):

    @abstractmethod
    def lint(self, filename: str) -> LinterResult:
        pass
