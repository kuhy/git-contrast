import subprocess

from git_contrast import Issue
from git_contrast import Linter, LinterResult


class CppcheckLinter(Linter):

    @property
    def name(self):
        return "Cppcheck"

    @property
    def needs_checkout(self):
        return True

    def lint(self, filename: str) -> LinterResult:
        number_of_issues = {}
        output = subprocess.getoutput("cppcheck -q -f --enable=all "
                                      "--suppress=missingInclude "
                                      "--suppress=unusedFunction "
                                      "--suppress=unmatchedSuppression "
                                      "--template='{id} {severity}' " +
                                      filename)
        for line in output.splitlines():
            parsed_issue = line.split(' ')
            issue = Issue(parsed_issue[0], self.name, parsed_issue[1])
            if issue in number_of_issues.keys():
                number_of_issues[issue] = number_of_issues[issue] + 1
            else:
                number_of_issues[issue] = 1
        return LinterResult(number_of_issues)
