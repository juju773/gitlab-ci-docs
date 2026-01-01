from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    """
    A class representing a gitlab-ci Stage

    ...
    Attributes
    ----------
    name : str
        The name of the stage
    """

    name: str
