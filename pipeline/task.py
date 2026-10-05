from __future__ import annotations

import uuid
from pathlib import Path
from enum import IntEnum


class WaitingException(Exception):
    """Raised when a task is forced to go from runnig to
    waiting as other tasks have to finish first"""

    pass


class State(IntEnum):
    READY = 0
    WAITING = 1
    RUNNING = 2
    FINISHED = 3


class FileTask:
    """Represent a file that can be processed"""

    id: uuid.UUID
    state: State

    # Amount of signals needed to be ready
    awaiting: int = 0

    input: Path
    output: Path | list[Path] | None

    # Task ID of the parent for this one
    parent: FileTask | None
    children: list[FileTask]

    params: dict[str, int]

    def __init__(
        self, input: Path, parent: FileTask | None, params: dict[str, int] = {}
    ):
        self.id = uuid.uuid4()
        self.state = State.READY

        self.awaiting = 0

        self.input = input
        self.output = None

        self.parent = parent
        self.children = []

        self.params = params

    def is_waiting_for_children(self) -> bool:
        """Wait for children if required"""
        amount = sum(1 for child in self.children if child.state != State.FINISHED)
        if amount > 0:
            self.wait(amount)
            return True

        return False

    def add_child(self, child: FileTask):
        self.children.append(child)

    def ready(self):
        if self.state != State.READY and self.state != State.FINISHED:
            raise Exception(f"Tried to reset an un-finished task {self.input}...")

        self.state = State.READY

        if self.parent:
            self.parent.ready()

    def wait(self, amount: int):
        self.awaiting = amount
        self.state = State.WAITING

    def signal(self):
        if self.awaiting <= 0 or self.state != State.WAITING:
            return

        self.awaiting -= 1

        if self.awaiting <= 0:
            self.awaiting = 0
            self.state = State.READY

    def process(self):
        if self.state != State.READY:
            raise Exception(
                f"Tried to process a file task for {self.input} that was not ready..."
            )

        self.state = State.RUNNING

    def finish(self):
        self.state = State.FINISHED

        if self.parent:
            self.parent.signal()
