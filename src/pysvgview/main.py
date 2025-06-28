"""
main
"""
import pylogconf.core
from pytconf import register_endpoint, get_free_args, register_main, config_arg_parse_and_launch

from pysvgview.static import DESCRIPTION, APP_NAME, VERSION_STR
from pysvgview.svg_view import view_svgs


@register_endpoint(
    allow_free_args=True,
    description="View svgs",
)
def view() -> None:
    view_svgs(get_free_args())


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
