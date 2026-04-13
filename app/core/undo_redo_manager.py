import json

from config import MAX_UNDO_STEPS


class UndoRedoManager:
    def __init__(self, max_steps: int = MAX_UNDO_STEPS):
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._max_steps = max_steps

    def clear(self) -> None:
        """Полная очистка стеков"""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def push(self, state: dict) -> None:
        """Сохраняет новое состояние и очищает стек redo."""
        for node in state["nodes"].values():
            node["selected"] = False

        if self._undo_stack and json.dumps(state, ensure_ascii=False) == json.dumps(self._undo_stack[-1],
                                                                                    ensure_ascii=False):
            return

        self._redo_stack.clear()
        self._undo_stack.append(state)
        if len(self._undo_stack) > self._max_steps:
            self._undo_stack.pop(0)

    def undo(self) -> dict | None:
        """Возвращает предыдущее состояние."""
        if not self._undo_stack:
            return None
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1]

    def redo(self) -> dict | None:
        """Возвращает следующее состояние."""
        if not self._redo_stack:
            return None
        next_state = self._redo_stack.pop()
        self._undo_stack.append(next_state)
        return next_state

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 1

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0
