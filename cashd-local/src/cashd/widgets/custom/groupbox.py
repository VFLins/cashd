from __future__ import annotations
from collections.abc import Iterable

import toga
from toga.style import Pack, TogaApplicator


class GroupBox(toga.Widget):
    """Container nativo com uma moldura opcionalmente titulada.

    Args:
        title: Texto exibido na moldura. ``None`` cria uma moldura sem título.
        children: Widgets que serão colocados dentro da moldura.
        id: Identificador do widget.
        style: Estilo Pack.
        kwargs: Propriedades de estilo adicionais.
    """

    _MIN_WIDTH = 0
    _MIN_HEIGHT = 0

    def __init__(
        self,
        title: str | None = None,
        children: Iterable[toga.Widget] | None = None,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        super().__init__(
            id=id,
            style=style,
            **kwargs,
        )

        self.title = title

        self._children = []
        if children is not None:
            self.add(*children)

    def _create(self):
        """Cria a implementação específica do backend."""

        backend = toga.backend

        if backend == "toga_gtk":
            from .gtk.groupbox import GroupBoxImpl

            return GroupBoxImpl(interface=self)

        if backend == "toga_winforms":
            from .winforms.groupbox import GroupBoxImpl

            return GroupBoxImpl(interface=self)

        raise NotImplementedError(
            f"GroupBox não possui implementação para o backend: {backend}"
        )

    @property
    def title(self) -> str | None:
        return getattr(self, "_title", None)

    @title.setter
    def title(self, title: str | None):
        self._title = title
        self._impl.set_title(title)
