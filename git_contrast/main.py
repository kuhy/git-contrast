from enum import Enum
import json
import os
import tempfile
from typing import Optional

import click
from click import echo, secho, style
import git

from git_contrast import Linter, LinterResult, Issue
from git_contrast.linters import PylintLinter


linters = {
    '.py': PylintLinter()
}


def get_linter(filename: str) -> Optional[Linter]:
    file_extension = os.path.splitext(filename)[1]
    return linters.get(file_extension)


def print_linter_result(result_pre: LinterResult, result_post):
    no_change = True
    for issue in Issue:
        pre = result_pre.number_of_issues[issue]
        post = result_post.number_of_issues[issue]
        if pre != post:
            no_change = False
            secho("    {: <60} {: >4}   -> {: >4}".format(issue.description, pre, post),
                  fg=('green' if post < pre else 'red'))
    if no_change:
        secho("    No change in quality detected.")


def print_linter_result_json(result_pre: LinterResult, result_post):
    results = {}
    for issue in Issue:
        pre = result_pre.number_of_issues[issue]
        post = result_post.number_of_issues[issue]
        results[issue.name] = {"pre": pre, "post": post}
    print(json.dumps(results))


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


@click.command()
@click.option("--output-format", type=click.Choice(OutputFormat),
              default=OutputFormat.TEXT)
@click.argument('commit_range', nargs=-1)
def cli(output_format, commit_range):
    repo = git.Repo(os.getcwd())

    # TODO improve arguments validity checking
    hashes = repo.git.rev_parse(*commit_range).split('\n')
    commit1 = repo.commit(hashes[0])
    commit2 = repo.commit(hashes[1])
    diff_index = commit1.diff(commit2)

    results_pre_sum = LinterResult()
    results_post_sum = LinterResult()
    for diff_item in diff_index:
        linter = get_linter(diff_item.a_path)
        if not linter:
            continue
        result_pre = None
        result_post = None
        if diff_item.a_blob and diff_item.b_blob and diff_item.a_blob != diff_item.b_blob:
            if output_format == OutputFormat.TEXT and diff_item.renamed:
                echo('File ' + style(diff_item.a_path, bold=True) +
                     ' was modified and renamed to ' + style(diff_item.b_path, bold=True) + ':')
            elif output_format == OutputFormat.TEXT:
                echo('File ' + style(diff_item.a_path, bold=True) + ' was modified:')
            with tempfile.NamedTemporaryFile() as file1:
                with tempfile.NamedTemporaryFile() as file2:
                    diff_item.a_blob.stream_data(file1)
                    diff_item.b_blob.stream_data(file2)
                    file1.flush()
                    file2.flush()
                    result_pre = linter.lint(file1.name)
                    result_post = linter.lint(file2.name)
        elif diff_item.deleted_file:
            if output_format == OutputFormat.TEXT:
                echo('File ' + style(diff_item.a_path, bold=True) + ' was deleted:')
            with tempfile.NamedTemporaryFile() as file1:
                diff_item.a_blob.stream_data(file1)
                file1.flush()
                result_pre = linter.lint(file1.name)
                result_post = LinterResult()
        elif diff_item.new_file:
            if output_format == OutputFormat.TEXT:
                echo('File ' + style(diff_item.b_path, bold=True) + ' was added:')
            with tempfile.NamedTemporaryFile() as file2:
                diff_item.b_blob.stream_data(file2)
                file2.flush()
                result_pre = LinterResult()
                result_post = linter.lint(file2.name)
        if output_format == OutputFormat.TEXT:
            print_linter_result(result_pre, result_post)
            echo('')
        results_pre_sum += result_pre
        results_post_sum += result_post

    if output_format == OutputFormat.TEXT:
        echo('')
        secho('Overall change in quality:', bold=True, underline=True)
        print_linter_result(results_pre_sum, results_post_sum)
    elif output_format == OutputFormat.JSON:
        print_linter_result_json(results_pre_sum, results_post_sum)


if __name__ == '__main__':
    cli()
