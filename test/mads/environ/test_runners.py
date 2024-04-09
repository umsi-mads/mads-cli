from mads.environ.runners import LocalRunner, GitHubActions, CodeBuild, Runner


def test_runner_selects_github(env):
    env["GITHUB_ACTIONS"] = "true"
    assert Runner.current == GitHubActions


def test_runner_selects_codebuild(env):
    env["CODEBUILD_BUILD_ID"] = "123"
    assert Runner.current == CodeBuild


def test_runner_selects_local(env):
    env.pop("GITHUB_ACTIONS", None)
    env.pop("CODEBUILD_BUILD_ID", None)
    assert Runner.current == LocalRunner


def test_local_runner():
    """Test the local runner"""
    runner = LocalRunner()

    assert runner.name == "local"


def test_github_actions(env):
    """Test the GitHub Actions runner"""

    env.update(
        {
            "GITHUB_ACTIONS": "true",
            "GITHUB_RUN_ID": "123",
            "GITHUB_REPOSITORY": "umsi-mads/mads-cli",
            "GITHUB_REF_NAME": "main",
            "GITHUB_EVENT_NAME": "push",
        }
    )
    runner = GitHubActions()

    assert runner.name == "github"
    assert runner.run_id == "123"
    assert runner.repo == "mads-cli"
    assert runner.ref == "main"
    assert runner.event == "push"
    assert (
        runner.url
        == "https://github.com/umsi-mads/mads-cli/actions/runs/123/attempts/1"
    )


# def test_codebuild():
#     """Test the CodeBuild runner"""

#     runner = CodeBuild()

#     assert runner.name == "codebuild"
