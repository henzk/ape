from __future__ import unicode_literals, print_function


class FeatureNotFound(Exception):
    """
    Raise this exception in case a feature is not represented in the feature list of the
    feature order validator.
    """
    pass