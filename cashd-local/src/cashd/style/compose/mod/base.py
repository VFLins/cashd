from typing import Any
import toga


class Modifier:
    """Generic class for layout/style modifiers."""

    def __init__(
        self,
        parent_style: dict[str, Any] | None = None,
        child_style: dict[str, Any] | None = None,
    ):
        """Modifier that allows for applying a single style to one or multiple widgets.

        :param parent_style: Style applied to the widget that receives this modifier.
        :param child_style: Style applied to the widget's children, when possible.
        """
        self.parent_style = parent_style or {}
        self.child_style = child_style or {}

    def reset(self):
        """Resets any internal state, so the next rebuild starts from a clean state.
        Static stylers hold no state, so this does nothing by default.
        """

    def apply_parent(self, style_dict: dict):
        """Adds the parent style to a style dictionary.

        :param style_dict: Dictionary that receives the parent style values.
        """
        style_dict.update(self.parent_style)

    def apply_child(self, style_dict: dict):
        """Adds the child style to a style dictionary.

        :param style_dict: Dictionary that receives the child style values.
        """
        style_dict.update(self.child_style)


class StyleManager:
    """Generic class for `Modifier` applicators."""

    @staticmethod
    def apply_to_parent(widget: toga.Widget, stylers: list[Modifier]):
        """Apply multiple styles to a Widget without removing non-conflicting styles.

        :param widget: A `toga.Widget` that will get the styles.
        :param stylers: Stylers holding styles that will be passed on to the widget.
        """
        kw = dict()
        for s in stylers:
            s.apply_parent(kw)
        for k, v in kw.items():
            setattr(widget.style, k, v)

    @staticmethod
    def apply_to_child(widget: toga.Widget, stylers: list[Modifier]):
        """Apply multiple styles to a Widget's children without removing non-conflicting
        styles.

        :param widget: A `toga.Widget` that will get the styles.
        :param stylers: Stylers holding styles that will be passed on to the widget.
        """
        kw = dict()
        for s in stylers:
            s.apply_child(kw)
        for k, v in kw.items():
            setattr(widget.style, k, v)
