from mads.environ.git import Git


def test_artifact_tag_main_branch():
    g = Git(branch="main")

    assert g.branch == "main"

    # On the main branch, the default behavior is to return "latest"
    assert g.artifact_tag() == "latest"

    # If using a prefix, the main branch behavior includes no suffix
    assert g.artifact_tag("feature") == "feature"

    # If use_branch, prefer the branch name over "latest"
    assert g.artifact_tag(use_branch=True) == "main"

    # If use_branch and a prefix, include the branch name instead of omitting
    assert g.artifact_tag("feature", use_branch=True) == "feature"


def test_artifact_tag_feature_branch():
    g = Git(branch="feature/123")

    assert g.branch == "feature/123"

    # On a feature branch, the default behavior is to return "dev"
    assert g.artifact_tag() == "dev"

    # If using a prefix, the feature branch behavior includes the prefix
    assert g.artifact_tag("feature") == "feature-dev"

    # If use_branch, prefer the branch name over "dev"
    assert g.artifact_tag(use_branch=True) == "feature/123"

    # If use_branch and a prefix, include the branch name instead of omitting
    assert g.artifact_tag("feature", use_branch=True) == "feature-feature/123"
