import argparse
import os


class IsFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isfile(values):
            parser.error("The '{}' file '{}' does not exist".format(self.dest, values))
        setattr(namespace, self.dest, values)


class MinInt(argparse.Action):
    def __init__(self, option_strings, dest, min_int=0, **kwargs):
        self.min_int = min_int
        super(MinInt, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values < self.min_int:
            parser.error("The minimum value for '{}' is '{}'".format(self.dest, self.min_int))
        setattr(namespace, self.dest, values)
