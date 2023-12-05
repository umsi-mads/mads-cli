"""Test the CLI interface"""

from mads import cli


def test_determine_tag(capsys):
    """Test that the help message works"""

    cli.main(["docker", "tag"])
    assert capsys.readouterr().out == "dev\n"


def test_determine_tag_default(capsys):
    """Test that the help message works"""

    cli.main(["docker", "tag", "--default", "beta"])
    assert capsys.readouterr().out == "beta\n"
