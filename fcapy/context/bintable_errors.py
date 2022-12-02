from dataclasses import dataclass
from typing import Any


@dataclass
class UnmatchedTypeError(ValueError):
    row_idx: int

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same type. '
            f'The problem is with the row #{self.row_idx}'
        ])
        return msg


@dataclass
class UnmatchedLengthError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same length. ',
            f'The problem is with the row #{self.row_idx}' if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class NotBooleanValueError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f"All values in each row should be of type bool.",
            f"The problem is with the row #{self.row_idx}" if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class UnknownDataTypeError(TypeError):
    unknown_type: type

    def __str__(self):
        msg = '\n'.join([
            "Dont know how to process the given `data`. ",
            "Acceptable types of data: List[List[bool]], npt.NDArray[bool], List[fbarray]. ",
            f"The given type: {self.unknown_type}"
        ]).strip()
        return msg


@dataclass
class UnknownAxisError(TypeError):
    unknown_axis: Any
    known_axes: set = frozenset({None, 0, 1})

    def __str__(self):
        msg = '\n'.join([
            f"Unknown `axis` value passed: {self.unknown_axis}. ",
            f"Supported values are: {self.known_axes}"
        ]).strip()
        return msg
