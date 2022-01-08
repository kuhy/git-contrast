import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class PylintLinter(Linter):
    issues = {
        'C0301': Issue.LINE_TOO_LONG,
        'C0115': Issue.MISSING_CLASS_DOCSTRING,
        'C0116': Issue.MISSING_FUNCTION_DOCSTRING
    }

    def lint(self, filename: str) -> LinterResult:
        result = LinterResult()
        output = subprocess.getoutput("pylint --msg-template='{msg_id}' " + filename)
        for line in output.split('\n'):
            key = PylintLinter.issues.get(line)
            if not key:
                continue
            result.number_of_issues[key] = result.number_of_issues[key] + 1
        return result
