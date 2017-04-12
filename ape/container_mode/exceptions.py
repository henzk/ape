

class EquationGeneratorException(Exception):
    """
    Base exception for errors occuring during equation generation.
    """

class FileDoesNotExistError(EquationGeneratorException):
    """
    Indicates that a file (equation or config) does not exist on disk.
    """