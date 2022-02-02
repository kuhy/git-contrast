from enum import Enum, auto
import json
import os
import tempfile
from typing import Optional

import click
from click import echo, secho, style
import git

from git_contrast import Linter, LinterResult
from git_contrast.linters import PylintLinter


linters = {
    '.py': PylintLinter()
}


def get_linter(filename: str) -> Optional[Linter]:
    file_extension = os.path.splitext(filename)[1]
    return linters.get(file_extension)


def lint_diff(linter: Linter, diff_item, diff_type):
    if diff_type is DiffType.MODIFIED:
        with tempfile.NamedTemporaryFile() as file1:
            with tempfile.NamedTemporaryFile() as file2:
                diff_item.a_blob.stream_data(file1)
                diff_item.b_blob.stream_data(file2)
                file1.flush()
                file2.flush()
                return(linter.lint(file1.name), linter.lint(file2.name))
    elif diff_type is DiffType.DELETED:
        with tempfile.NamedTemporaryFile() as file1:
            diff_item.a_blob.stream_data(file1)
            file1.flush()
            return(linter.lint(file1.name), LinterResult())
    elif diff_type is DiffType.ADDED:
        with tempfile.NamedTemporaryFile() as file2:
            diff_item.b_blob.stream_data(file2)
            file2.flush()
            return(LinterResult(), linter.lint(file2.name))


def print_linter_result(result_pre: LinterResult, result_post: LinterResult):
    no_change = True
    issues = set(result_pre.number_of_issues.keys())
    issues = issues.union(set(result_post.number_of_issues.keys()))
    for issue in issues:
        pre = (result_pre.number_of_issues[issue] if
               issue in result_pre.number_of_issues.keys() else 0)
        post = (result_post.number_of_issues[issue] if
                issue in result_post.number_of_issues.keys() else 0)
        if pre != post:
            no_change = False
            secho("    {: <60}  {: >4}   -> {: >4}".format(issue.symbolic_name,
                                                           pre, post),
                  fg=('green' if post < pre else 'red'))
    if no_change:
        secho("    No change in quality detected.")


def print_linter_result_json(result_pre: LinterResult,
                             result_post: LinterResult,
                             number_of_files):
    results = {}
    issues = set(result_pre.number_of_issues.keys())
    issues = issues.union(set(result_post.number_of_issues.keys()))
    for issue in issues:
        pre = (result_pre.number_of_issues[issue] if
               issue in result_pre.number_of_issues.keys() else 0)
        post = (result_post.number_of_issues[issue] if
                issue in result_post.number_of_issues.keys() else 0)
        if issue.linter not in results.keys():
            results[issue.linter] = {}
        results[issue.linter][issue.symbolic_name] = {"pre": pre, "post": post,
                                                      "type": issue.category}
    echo(json.dumps(dict({"results": results}, **number_of_files)))


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class DiffType(str, Enum):
    MODIFIED = "modified"
    DELETED = "deleted"
    ADDED = "added"


@click.command()
@click.option("--output-format", type=click.Choice(OutputFormat),
              default=OutputFormat.TEXT)
@click.argument('commit_range', nargs=-1)
def cli(output_format, commit_range):
    repo = git.Repo(os.getcwd())

    # TODO: improve arguments validity checking
    hashes = repo.git.rev_parse(*commit_range).split('\n')
    commit1 = repo.commit(hashes[0])
    commit2 = repo.commit(hashes[1])
    diff_index = commit1.diff(commit2)

    results_pre_sum = LinterResult()
    results_post_sum = LinterResult()

    number_of_files = {DiffType.MODIFIED.value: 0, DiffType.DELETED.value: 0,
                       DiffType.ADDED.value: 0}

    for diff_item in diff_index:
        if diff_item.a_blob and diff_item.b_blob and (diff_item.a_blob !=
                                                      diff_item.b_blob):
            diff_type = DiffType.MODIFIED
        elif diff_item.deleted_file:
            diff_type = DiffType.DELETED
        elif diff_item.new_file:
            diff_type = DiffType.ADDED
        else:
            continue

        number_of_files[diff_type.value] += 1

        linter = get_linter(diff_item.a_path)
        if not linter:
            continue

        (result_pre, result_post) = lint_diff(linter, diff_item, diff_type)

        results_pre_sum += result_pre
        results_post_sum += result_post

        key = diff_type.value + "_" + linter.name
        number_of_files[key] = 1 if key not in number_of_files else (
            number_of_files[key] + 1)

        if output_format != OutputFormat.TEXT:
            continue

        if diff_type is DiffType.MODIFIED:
            if diff_item.renamed:
                echo('File ' + style(diff_item.a_path, bold=True) +
                     ' was modified and renamed to ' + style(diff_item.b_path, bold=True) + ':')
            else:
                echo('File ' + style(diff_item.a_path, bold=True) + ' was modified:')
        elif diff_type is DiffType.DELETED:
            echo('File ' + style(diff_item.a_path, bold=True) + ' was deleted:')
        elif diff_type is DiffType.ADDED:
            echo('File ' + style(diff_item.b_path, bold=True) + ' was added:')

        print_linter_result(result_pre, result_post)
        echo()

    if output_format == OutputFormat.TEXT:
        echo()
        secho('Overall change in quality:', bold=True, underline=True)
        print_linter_result(results_pre_sum, results_post_sum)
    elif output_format == OutputFormat.JSON:
        print_linter_result_json(results_pre_sum, results_post_sum,
                                 number_of_files)


if __name__ == '__main__':
    cli()
