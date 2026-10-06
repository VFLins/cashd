from typing import Any, Generator, Iterable

from .base import Modifier


class Styler(Modifier):
    def __repr__(self):
        _repr = "<Styler"
        if getattr(self, "parent_style", False):
            _repr = _repr + f" parent_style={self.parent_style}"
        if getattr(self, "child_style", False):
            _repr = _repr + f" child_style={self.child_style}"
        return _repr + ">"


class IterableStyler(Styler):
    def __init__(
        self,
        parent_style: dict[str, Iterable[Any]] | None = None,
        child_style: dict[str, Iterable[Any]] | None = None,
    ):
        """Modifier that allows for applying a list of styles iteratively to one or
        multiple widgets.

        :param parent_style: Style applied to the widget that receives this modifier.
        :param child_style: Style applied to the widget's children, when possible.
        """
        super().__init__(parent_style, child_style)
        self.parent_gen = self._get_parent_gen()
        self.child_gen = self._get_child_gen()

    def apply_parent(self, style_dict: dict):
        """Adds the next parent style in the cycle to a style dictionary.

        :param style_dict: Dictionary that receives the parent style values.
        """
        kw = next(self.parent_gen)
        style_dict.update(kw)

    def apply_child(self, style_dict: dict):
        """Adds the next child style in the cycle to a style dictionary.

        :param style_dict: Dictionary that receives the child style values.
        """
        kw = next(self.child_gen)
        style_dict.update(kw)

    def reset(self):
        """Restarts both cycles, so the next widget receives the first values again."""
        self.parent_gen = self._get_parent_gen()
        self.child_gen = self._get_child_gen()

    def _get_parent_gen(self) -> Generator[dict, None, None]:
        index = 0
        while True:
            yield {
                k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
                for k, v in self.parent_style.items()
            }
            index = index + 1

    def _get_child_gen(self) -> Generator[dict, None, None]:
        index = 0
        while True:
            yield {
                k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
                for k, v in self.child_style.items()
            }
            index = index + 1

