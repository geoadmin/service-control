# basic implementation of the types of django-environ
# since this package is neither critical nor widely used and rather of simple
# nature, API wise, it intentionally contains the minimum needed to satisfy
# the type checker
import builtins
from typing import Dict, List
from _typeshed import Incomplete  # pylint: disable=import-error


class Env:

    def __init__(self) -> None:
        ...

    def __call__(
        self, var: builtins.str, cast=..., default=..., parse_default: builtins.bool = False
    ):
        ...

    def str(self, var: builtins.str, default=..., multiline: builtins.bool = ...) -> builtins.str:
        ...

    def bool(self, var: builtins.str, default=...) -> builtins.bool:
        ...

    def int(self, var: builtins.str, default=...) -> builtins.str:
        ...

    def list(self,
             var,
             cast: Incomplete | None = None,
             default=...) -> List[builtins.str | builtins.int]:
        ...

    def dict(self, var, cast=..., default=...) -> Dict[builtins.str, builtins.str | builtins.int]:
        ...
