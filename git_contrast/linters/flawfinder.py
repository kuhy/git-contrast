import json
import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class FlawfinderLinter(Linter):
    """Class that is responsible for running the flawfinder linter (C/C++)."""

    @property
    def name(self):
        return "flawfinder"

    @property
    def needs_checkout(self):
        return False

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("flawfinder --sarif " + filename)
        run = json.loads(output)["runs"][0]
        for parsed_issue in run["results"]:
            issue_name = (next(filter(lambda rule: (rule["id"] ==
                                                    parsed_issue["ruleId"]),
                                      run["tool"]["driver"]["rules"]))["name"]
                          ).replace("/", "-")
            issue = Issue(issue_name, self.name,
                          parsed_issue["level"])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
