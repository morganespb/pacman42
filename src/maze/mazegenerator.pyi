# mazegenerator.pyi
class MazeGenerator:
    def __init__(
        self,
        size: tuple[int, int] = ...,
        perfect: bool = ...,
        seed: int = ...,
    ) -> None: ...

    @property
    def maze(self) -> list[list[int]]: ...
