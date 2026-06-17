class Pruefung:
    def __init__(self, note: float) -> None:
        self._note: float = note

    @property
    def note(self) -> float:
        return self._note