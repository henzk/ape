from __future__ import unicode_literals, print_function


class FeatureNotFound(Exception):
    """
    Raise this exception in case a feature is not represented in the feature list of the
    feature order validator.
    """
    pass


class ProductNotFound(Exception):
    """
    Raise this exception in case the given product is not found.
    """
    pass


class ContainerError(Exception):
    """
    Represents a generic SPL-Container related error.
    """


class ContainerNotFound(ContainerError):
    """
    Raise this exception in case the given container is not found.
    """
    pass
