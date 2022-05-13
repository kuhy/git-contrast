import json
import subprocess
import tempfile

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class PMDLinter(Linter):
    """Class that is responsible for running the PMD linter (Java)."""

    @property
    def name(self):
        return "PMD"

    @property
    def needs_checkout(self):
        return False

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        with tempfile.NamedTemporaryFile() as f:
            subprocess.getoutput("pmd -R rulesets/internal/all-java.xml "
                                 "-language java -f json -r {} -d {}".format(
                                     f.name, filename))
            output = f.read()
        files = json.loads(output)["files"]
        if len(files) != 0:
            for parsed_issue in files[0]["violations"]:
                issue = Issue(parsed_issue["rule"], self.name,
                              parsed_issue["ruleset"])
                if issue in number_of_issues.keys():
                    number_of_issues[issue] = number_of_issues[issue] + 1
                else:
                    number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
