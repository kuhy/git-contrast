import json
import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class PylintLinter(Linter):
    """Class that is responsible for running the Pylint linter (Python)."""

    @property
    def name(self):
        return "Pylint"

    @property
    def needs_checkout(self):
        return False

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("pylint --output-format=json " + filename)
        for parsed_issue in json.loads(output):
            issue = Issue(parsed_issue["symbol"], self.name,
                          parsed_issue["type"])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
