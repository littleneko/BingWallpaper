"""Provides a utility to inject environment variables into argparse definitions.
Currently requires explicit naming of env vars to check for"""

# https://gist.github.com/orls/51525c86ee77a56ad396

import argparse
import os


# Courtesy of http://stackoverflow.com/a/10551190 with env-var retrieval fixed
class EnvDefault(argparse.Action):
    """An argparse action class that auto-sets missing default values from env
    vars. Defaults to requiring the argument."""

    def __init__(self, env_var, required=False, default=None, **kwargs):
        if env_var and env_var in os.environ:
            var = os.environ[env_var]
            if len(var) > 0:
                default = var
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


# functional sugar for the above
def env_default(env_var):
    def wrapper(**kwargs):
        return EnvDefault(env_var, **kwargs)

    return wrapper
