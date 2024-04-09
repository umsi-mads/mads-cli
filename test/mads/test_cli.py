"""Test the CLI interface"""

from mads import cli
from mads.environ import Git


def test_determine_tag(capsys):
    """Test that the help message works"""

    cli.main(["docker", "tag"])

    git = Git()
    expected = {
        "main": "latest",
        "master": "latest",
        "beta": "beta",
        None: "dev",
    }.get(git.branch, "dev")
    assert capsys.readouterr().out == f"{expected}\n"


def test_determine_tag_default(capsys):
    """Test that the help message works"""

    cli.main(["docker", "tag", "--default", "beta"])

    git = Git()
    expected = {
        "main": "latest",
        "master": "latest",
        "beta": "beta",
        None: "beta",
    }.get(git.branch, "beta")
    assert capsys.readouterr().out == f"{expected}\n"
