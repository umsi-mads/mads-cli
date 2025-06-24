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


class PathFinder:
    """A class to search across multiple paths

    Given either an environment variable name, or a list of paths, provide access
    methods to search for files across all of them."""

    __slots__ = ("paths",)

    paths: list[Path]

    def __init__(self, paths: str | list[str] | list[Path]):
        if isinstance(paths, str):
            import os

            paths = os.environ.get(paths.replace("$", ""), ".").split(":")

        self.paths = [Path(p) for p in paths]

    def __repr__(self) -> str:
        return f"PathFinder({', '.join([str(p) for p in self.paths])})"

    def __rich_repr__(self):
        for path in self.paths:
            yield str(path)

    def find(self, name: str) -> Path:
        """Find a file within the paths, or raise an error if it's not found"""

        if path := self.get(name):
            return path

        raise FileNotFoundError(
            f"Could not find '{name}'. Searched within the following paths:\n"
            + "\n".join(["  - " + str(p) for p in self.paths])
        )

    def get(self, name: str) -> Path | None:
        """Find a file within the paths, or return None if it's not found"""

        for path in self.paths:
            path = path.joinpath(name)
            if path.exists():
                return path

        return None

    def __truediv__(self, other: str) -> Path:
        """Find files as if the finder was a Path: finder / 'file.txt'"""

        return self.find(other)
