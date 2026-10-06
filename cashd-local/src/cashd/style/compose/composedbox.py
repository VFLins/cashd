import toga
from .mod.base import Modifier
from .mod.style import Styler


class ComposedBox(toga.Box):
    def __init__(self, *modifiers: Modifier, **kwargs):
        """Box whose layout is described declaratively through modifiers.

        :param modifiers: Modifiers (stylers and at most one grid handler) that
            define the styling and arrangement of this box and its children.
        :param kwargs: Regular `toga.Box` arguments. `children` is kept as the
            list of widgets that the modifiers will arrange.
        """
        raw_children = kwargs.pop("children", [])
        self._raw_children = list(raw_children)
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]

        super().__init__(**kwargs)
        self.rebuild()

    def add(self, *children: toga.Widget):
        """Appends widgets to this box and rebuilds its layout.

        :param children: Widgets to be added at the end.
        """
        if not children:
            return
        self._raw_children.extend(children)
        self.rebuild()

    def add_at(self, index: int, *children: toga.Widget):
        """Inserts widgets at a given position and rebuilds the layout.

        :param index: Position where the widgets will be inserted.
        :param children: Widgets to be inserted.
        """
        if not children:
            return
        self._raw_children[index:index] = children
        self.rebuild()

    def remove(self, *children: toga.Widget):
        """Removes widgets from this box and rebuilds its layout.

        :param children: Widgets to be removed. They must be children of this box.
        """
        if not children:
            return
        for child in self._raw_children:
            self._raw_children.remove(child)
        self.rebuild()

    def replace_children(self, *children: toga.Widget):
        """Replaces all current children with the given widgets and rebuilds the
        layout.

        :param children: Widgets that become the only children of this box. Passing
            no widgets leaves the box empty.
        """
        self._raw_children = list(children)
        self.rebuild()

    def replace_modifiers(self, *modifiers: Modifier):
        """Replaces the modifiers of this box and rebuilds its layout.

        :param modifiers: New modifiers that define the layout.
        """
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]
        self.rebuild()

    @property
    def grid_handler(self) -> GridHandler | None:
        """The grid handler among the modifiers, or `None` when there is none."""
        try:
            return [m for m in self._modifiers if isinstance(m, GridHandler)][0]
        except IndexError:
            return None

    @property
    def stylers(self) -> list[Styler]:
        """The stylers among the modifiers."""
        return [m for m in self._modifiers if isinstance(m, Styler)]

    def rebuild(self):
        """Rebuilds it's layout."""
        # Restart iterable stylers so every rebuild gives the same result
        for s in self.stylers:
            s.reset()

        # Reapply own styling
        apply_styles(as_parent=True, widget=self, stylers=self.stylers)

        # Delete widgets keeping references
        self.style.visibility = HIDDEN
        self.refresh()
        try:
            for child in list(self.children):
                super().remove(child)
            if not self._raw_children:
                return

            # Add widgets from references
            if self.grid_handler is not None:
                containers = self.grid_handler.arrange(
                    self._raw_children, *self.stylers
                )
                for c in containers:
                    super().add(c)
            else:
                for child in self._raw_children:
                    apply_styles(as_parent=False, widget=child, stylers=self.stylers)
                    super().add(child)
        finally:
            # Always restore visibility, even when empty or when an error occurs
            self.style.visibility = VISIBLE


def apply_styles(as_parent: bool, widget: toga.Widget, stylers: list[Styler]):
    """Apply multiple styles to a Widget without removing widget's non-conflicting
    styles.

    :param as_parent: Boolean indicating if this `widget` should use parent styles.
    :param widget: A `toga.Widget` that will get the styles.
    :param stylers: Stylers holding styles that will be passed on to the widget.
    """
    kw = dict()
    for s in stylers:
        if as_parent:
            s.apply_parent(kw)
        else:
            s.apply_child(kw)
    for k, v in kw.items():
        setattr(widget.style, k, v)


def get_container(*args, **kwargs) -> ComposedBox:
    """Shortcut that creates a `ComposedBox`.

    :param args: Modifiers passed on to the `ComposedBox`.
    :param kwargs: Keyword arguments passed on to the `ComposedBox`.
    """
    return ComposedBox(*args, **kwargs)
