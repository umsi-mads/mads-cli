"""
The CLI interface for MADS builds.
"""

import sys

from .args import parser


def main(argv=sys.argv[1:]):
    """The CLI interface for MADS builds"""

    parsed = parser.parse_args(argv)
    parsed.func(parsed)
