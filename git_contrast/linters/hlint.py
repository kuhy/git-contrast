import json
import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class HlintLinter(Linter):

    @property
    def name(self):
        return "HLint"

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("hlint --cpp-simple --json " + filename)
        for parsed_issue in json.loads(output):
            issue = Issue(parsed_issue["hint"].replace(' ', '-'), self.name,
                          parsed_issue["severity"])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
