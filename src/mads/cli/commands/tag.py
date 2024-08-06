"""Generate an artifact tag based on the git environment"""

import argparse

from mads.environ.git import Git


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the environ command"""

    def run(args):
        """Run the query"""

        git = Git()

        print(
            git.artifact_tag(
                *args.prefix,
                use_branch=args.use_branch,
                default=args.default,
            )
        )

    parser.set_defaults(func=run)
    parser.add_argument("prefix", nargs="*", help="Prefix for the tag")
    parser.add_argument(
        "--use-branch",
        action="store_true",
        help="Use the branch name rather than a semantic equivalent",
        default=False,
    )

    parser.add_argument(
        "--default",
        default="dev",
        help="Default tag to use if no branch is found",
    )
