from pathlib import Path
from typing import Type

from pipeline.task import (
    State,
    FileTask,
    WaitingException,
)

from game_parser import Parser
from game_parser.packed import PackedParser, PAK_SUFFIX
from game_parser.gam import GamParser, GAM_SUFFIX
from game_parser.rle import RLEParser, RLE_SUFFIX
from game_parser.tim import TIMParser, TIM_SUFFIX
from game_parser.grpx import GRPXParser, GRPX_SUFFIX


class MultiStageOrchestrator:
    registry: dict[str, Type[Parser]] = {}
    tasks: list[FileTask] = []

    def register_parser(self, extension: str, parser: Type[Parser]):
        self.registry[extension.lower()] = parser

    def add_task(
        self, input: Path, parent: FileTask | None = None, params: dict[str, int] = {}
    ):
        """Adds a file to be processed"""
        task = FileTask(input=input, parent=parent, params=params)
        self.tasks.append(task)

        if parent:
            parent.add_child(task)

    def get_task(self, output: Path) -> FileTask:
        for task in self.tasks:
            if task.output == output:
                return task

        raise ValueError(f"Could not find the task that created the file {output}...")

    def get_parser(self, path: Path) -> Type[Parser] | None:
        extension = path.suffix
        parser = self.registry.get(extension.lower(), None)
        return parser

    def ready_all(self):
        for task in self.tasks:
            task.ready()

    def process(self, forward: bool = False):
        is_running = True
        while is_running:
            ready_tasks = [task for task in self.tasks if task.state == State.READY]
            is_running = len(ready_tasks) > 0

            for task in ready_tasks:
                if task.is_waiting_for_children():
                    continue

                parser = self.get_parser(task.input)
                if parser is None:
                    task.finish()
                elif forward:
                    self.forward(parser, task)
                else:
                    self.reverse(parser, task)

    def forward(self, parser: Type[Parser], task: FileTask):
        try:
            task.process()

            output = parser.forward(task.input, task.params)
            task.output = output

            if isinstance(output, Path):
                outputs = [output]
            else:
                outputs = output

            for input in outputs:
                self.add_task(input, parent=task)

            task.finish()
        except WaitingException:
            pass

    def reverse(self, parser: Type[Parser], task: FileTask):
        if task.output is None:
            raise ValueError(f"Trying to reverse task {task.id} with no output...")

        try:
            task.process()

            input = parser.reverse(task.output, task.params)

            task.finish()
        except WaitingException:
            pass

        if task.input != input:
            raise Exception(
                f"Reversing task {task.id} yielded {input} but it was originaly {task.input}..."
            )


def create_orchestrator() -> MultiStageOrchestrator:
    orchestrator = MultiStageOrchestrator()

    orchestrator.register_parser(PAK_SUFFIX, PackedParser)
    orchestrator.register_parser(GAM_SUFFIX, GamParser)
    orchestrator.register_parser(RLE_SUFFIX, RLEParser)
    orchestrator.register_parser(TIM_SUFFIX, TIMParser)
    orchestrator.register_parser(GRPX_SUFFIX, GRPXParser)

    return orchestrator


if __name__ == "__main__":
    orchestrator = create_orchestrator()

    base = Path("debug")
    for path in base.glob("*.*"):
        orchestrator.add_task(path)

    orchestrator.process(forward=True)
