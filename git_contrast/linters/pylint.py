import json
import subprocess

from git_contrast import Issue, IssueCategory
from git_contrast import Linter, LinterResult


class PylintLinter(Linter):
    categories = {
        "convention": IssueCategory.CONVENTION,
        "refactor": IssueCategory.HINT,
        "warning": IssueCategory.WARNING,
        "error": IssueCategory.ERROR,
        "fatal": IssueCategory.ERROR
    }

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("pylint --output-format=json " + filename)
        for parsed_issue in json.loads(output):
            issue = Issue(parsed_issue["symbol"], "Pylint",
                          PylintLinter.categories[parsed_issue["type"]])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
