from pathlib import Path


def find_upwards(name: str) -> Path | None:
    """
    Given a name to look for, traverse from pwd upwards until we find it.
    If it's not present, return None.
    """

    path = Path.cwd()
    while path != Path("/"):
        if path.joinpath(name).exists():
            return path.joinpath(name)
        path = path.parent

    return None


def current_repo() -> str:
    """Return the name of the current git repository. If we're not in one, return $PWD"""

    repo = find_upwards(".git")
    if repo:
        return repo.parent.name
    else:
        return Path.cwd().name
