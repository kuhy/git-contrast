from enum import Enum, auto
import tempfile
import os
import subprocess
from typing import Optional

from abc import ABC, abstractmethod
import click
from click import echo, secho, style
import git


class IssueType(Enum):

    FORMAT = auto()
    DOCUMENTATION = auto()


class Issue(Enum):

    def __init__(self, issue_type: IssueType, description: str):
        self.issue_type = issue_type
        self.description = description

    LINE_TOO_LONG = IssueType.FORMAT, "Line too long"
    MISSING_CLASS_DOCSTRING = IssueType.DOCUMENTATION, "Missing class docstring"
    MISSING_FUNCTION_DOCSTRING = IssueType.DOCUMENTATION, "Missing function or method docstring"


class LinterResult:

    def __init__(self, number_of_issues=None):
        if number_of_issues:
            self.number_of_issues = number_of_issues
        else:
            self.number_of_issues = {issue: 0 for issue in Issue}

    def __add__(self, other):
        number_of_issues = {issue: self.number_of_issues[issue] + other.number_of_issues[issue]
                            for issue in Issue}
        return LinterResult(number_of_issues)

    def __sub__(self, other):
        number_of_issues = {issue: self.number_of_issues[issue] - other.number_of_issues[issue]
                            for issue in Issue}
        return LinterResult(number_of_issues)

    def __neg__(self):
        return LinterResult({issue: -self.number_of_issues[issue] for issue in Issue})


class Linter(ABC):

    @abstractmethod
    def lint(self, filename: str) -> LinterResult:
        pass


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


linters = {
    '.py': PylintLinter()
}

def get_linter(filename: str) -> Optional[Linter]:
    file_extension = os.path.splitext(filename)[1]
    return linters.get(file_extension)


def print_linter_result(result: LinterResult):
    no_issue = True
    for issue, count in result.number_of_issues.items():
        if count != 0:
            no_issue = False
            secho("    " + issue.description + ": " + '{:+}'.format(count),
                  fg=('green' if count < 0 else 'red'))
    if no_issue:
        secho("    No change in quality detected.")


@click.command()
@click.argument('commit_range', nargs=-1)
def git_contrast(commit_range):
    repo = git.Repo(os.getcwd())

    # TODO improve arguments validity checking
    hashes = repo.git.rev_parse(*commit_range).split('\n')
    commit1 = repo.commit(hashes[0])
    commit2 = repo.commit(hashes[1])
    diff_index = commit1.diff(commit2)

    final_result = LinterResult()
    for diff_item in diff_index:
        linter = get_linter(diff_item.a_path)
        if not linter:
            continue
        result = None
        if diff_item.a_blob and diff_item.b_blob and diff_item.a_blob != diff_item.b_blob:
            if diff_item.renamed:
                echo('File ' + style(diff_item.a_path, bold=True) +
                     ' was modified and renamed to ' + style(diff_item.b_path, bold=True) + ':')
            else:
                echo('File ' + style(diff_item.a_path, bold=True) + ' was modified:')
            with tempfile.NamedTemporaryFile() as file1:
                with tempfile.NamedTemporaryFile() as file2:
                    diff_item.a_blob.stream_data(file1)
                    diff_item.b_blob.stream_data(file2)
                    file1.flush()
                    file2.flush()
                    result = linter.lint(file2.name) - linter.lint(file1.name)
        elif diff_item.deleted_file:
            echo('File ' + style(diff_item.a_path, bold=True) + ' was deleted:')
            with tempfile.NamedTemporaryFile() as file1:
                diff_item.a_blob.stream_data(file1)
                file1.flush()
                result = - linter.lint(file1.name)
        elif diff_item.new_file:
            echo('File ' + style(diff_item.b_path, bold=True) + ' was added:')
            with tempfile.NamedTemporaryFile() as file2:
                diff_item.b_blob.stream_data(file2)
                file2.flush()
                result = linter.lint(file2.name)
        print_linter_result(result)
        echo('')
        final_result = final_result + result
    echo('')
    secho('Overall change in quality:', bold=True, underline=True)
    print_linter_result(final_result)


if __name__ == '__main__':
    git_contrast()
