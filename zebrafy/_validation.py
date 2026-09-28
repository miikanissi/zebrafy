########################################################################################
#
#    Author: Miika Nissi
#    Copyright 2026 Miika Nissi (https://miikanissi.com)
#
#    This file is part of zebrafy
#    (see https://github.com/miikanissi/zebrafy).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################################

"""Dataclass fields that validate their values on assignment."""

# 1. Standard library imports:
import dataclasses
from collections.abc import Callable, Sequence
from typing import Any

# 2. Known third party imports:

# 3. Local imports in the relative form:

_TYPE_NAMES = {
    bool: "a boolean",
    bytes: "a bytes object",
    int: "an integer",
    str: "a string",
}


class Validated:
    """Mixin for dataclasses that validates fields created by ``validated_field``."""

    def __setattr__(self, name: str, value: Any) -> None:
        field = self.__dataclass_fields__.get(name)  # type: ignore[attr-defined]
        if field is not None and "validate" in field.metadata:
            value = field.metadata["validate"](value)
        super().__setattr__(name, value)


def validated_field(
    default: Any,
    label: str,
    types: type | tuple[type, ...],
    *,
    type_name: str | None = None,
    optional: bool = False,
    allow_empty: bool = False,
    minimum: int | None = None,
    maximum: int | None = None,
    choices: Sequence[Any] | None = None,
    normalize: Callable[[Any], Any] | None = None,
    kw_only: bool = True,
    repr: bool = True,
) -> Any:
    """
    Create a dataclass field that is validated whenever it is assigned.

    :param default: Default value, or ``dataclasses.MISSING`` for a required field.
    :param label: Name of the field in error messages.
    :param types: Accepted type or types. Booleans are never accepted as integers.
    :param type_name: Description of the accepted types in error messages.
    :param optional: Accept ``None``.
    :param allow_empty: Accept empty bytes and strings.
    :param minimum: Smallest accepted value.
    :param maximum: Largest accepted value.
    :param choices: Accepted values.
    :param normalize: Function applied to the value before checking ``choices``.
    :param kw_only: Make the field keyword-only in ``__init__``.
    :param repr: Include the field in ``repr()``.
    :returns: A dataclass field.
    """
    accepted = types if isinstance(types, tuple) else (types,)
    if type_name is None:
        type_name = _TYPE_NAMES[accepted[0]]

    def validate(value: Any) -> Any:
        if value is None and optional:
            return None
        if value is None or (
            not allow_empty and isinstance(value, (bytes, str)) and not value
        ):
            raise ValueError(f"{label} cannot be empty.")
        if not isinstance(value, accepted) or (
            isinstance(value, bool) and bool not in accepted
        ):
            raise TypeError(f"{label} must be {type_name}. {type(value)} was given.")
        if normalize is not None:
            value = normalize(value)
        if minimum is not None and value < minimum:
            raise ValueError(f"{label} must be at least {minimum}. {value} was given.")
        if maximum is not None and value > maximum:
            raise ValueError(f"{label} must be at most {maximum}. {value} was given.")
        if choices is not None and value not in choices:
            allowed = ", ".join(f'"{choice}"' for choice in choices)
            raise ValueError(f"{label} must be one of {allowed}. {value} was given.")
        return value

    return dataclasses.field(
        default=default,
        kw_only=kw_only,
        repr=repr,
        metadata={"validate": validate},
    )
