"""
All configurations for pysvgview
"""


from pytconf import Config, ParamCreator


class ConfigDummy(Config):
    """
    Parameters for nothing
    """
    doit = ParamCreator.create_bool(
        help_string="actually perform the actions?",
        default=True,
    )
