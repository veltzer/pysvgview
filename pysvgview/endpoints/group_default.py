"""
The default group of operations that pysvgview has
"""

from pytconf import register_endpoint, register_function_group, get_free_args

import pysvgview.version
from pysvgview.svg_view import view_svgs

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pysvgview commands"


def register_group_default():
    """
    register the name and description of this group
    """
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
)
def version() -> None:
    """
    Print version
    """
    print(pysvgview.version.VERSION_STR)


@register_endpoint(
    group=GROUP_NAME_DEFAULT,
    allow_free_args=True,
)
def view() -> None:
    """
    view svgs
    """
    view_svgs(get_free_args())
