from typing import Generator, Iterable
from .base import Modifier
from .style import Styler

class GridHandler(Modifier):
    def __init__(self, n: int = 1, direction: str = COLUMN, *stylers: Styler):
        """Modifier that distributes the children of a container across N blocks.

        :param n: Number of blocks to create. Values lower than 1 are treated as 1.
        :param direction: Direction of each created block (`ROW` or `COLUMN`).
        :param stylers: Stylers applied to the blocks and to the children placed in them.
        """
        self.n = max(1, n)
        self.direction = direction
        self.stylers = stylers
        self.parent_stylers: Iterable[Styler] = []

    def arrange(self, children: list, *parent_stylers: Styler) -> list[Box]:
        """Entry point that builds the blocks and distributes the children across them.

        :param children: Widgets to be distributed, in order, across the blocks.
        :param parent_stylers: Stylers inherited from the container that owns this handler.
        :return: The blocks, already holding their children and styled.
        """
        self.parent_stylers = parent_stylers
        for s in (*self.parent_stylers, *self.stylers):
            s.reset()
        blocks = []
        for i in range(self.n):
            block = Box(children=self._get_children_at(index=i, children=children))
            # Apply styles inherited from parent block
            apply_styles(as_parent=False, widget=block, stylers=self.parent_stylers)
            # Apply own styles overwriting inherited ones when conflicting
            apply_styles(as_parent=True, widget=block, stylers=self.stylers)
            block.style.direction = self.direction
            blocks.append(block)
        return blocks

    def _get_children_at(self, index: int, children: list[Widget]) -> list[Widget]:
        """Selects the children of block `index` (every N-th widget) and styles each one.

        :param index: Index of the block that will receive the children.
        :param children: All widgets being distributed.
        :return: The widgets that belong to the block.
        """
        subset = children[index :: self.n]
        for child in subset:
            apply_styles(as_parent=False, widget=child, stylers=self.stylers)
        return subset
