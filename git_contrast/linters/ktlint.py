import json
import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class KtlintLinter(Linter):
    """Class that is responsible for running the ktlint linter (Kotlin)."""

    @property
    def name(self):
        return "ktlint"

    @property
    def needs_checkout(self):
        return False

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("ktlint --reporter=json  " + filename)
        output = ' '.join([line for line in output.split('\n')
                           if not line[0].isdigit()])
        files = json.loads(output)
        if len(files) != 0:
            for parsed_issue in files[0]["errors"]:
                issue = Issue(parsed_issue["rule"], self.name, None)
                if issue in number_of_issues.keys():
                    number_of_issues[issue] = number_of_issues[issue] + 1
                else:
                    number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
