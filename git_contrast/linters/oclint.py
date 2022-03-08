import json
import subprocess
import tempfile

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class OCLintLinter(Linter):

    @property
    def name(self):
        return "OCLint"

    @property
    def needs_checkout(self):
        return True

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        with tempfile.NamedTemporaryFile() as f:
            subprocess.getoutput("oclint --report-type=json -o {} "
                                 "--max-priority-1=999999 "
                                 "--max-priority-2=999999 "
                                 "--max-priority-3=999999 {}"
                                 .format(f.name, filename))
            output = f.read()
        for parsed_issue in json.loads(output)["violation"]:
            issue = Issue(parsed_issue["rule"].replace(' ', '-'), self.name,
                          parsed_issue["category"])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
