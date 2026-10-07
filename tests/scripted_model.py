"""A scripted model: replays canned assistant messages in order.

It lets the tests drive a real ``strands.Agent`` through its real event loop
without a network call.
"""

import json
from collections.abc import AsyncGenerator, Iterable, Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from strands.models import Model
from strands.types.content import Message, Messages
from strands.types.event_loop import StopReason
from strands.types.tools import ToolSpec

T = TypeVar("T", bound=BaseModel)


class ScriptedModel(Model):
    """Answer each model call with the next message of the script."""

    def __init__(self, responses: Sequence[Message]) -> None:
        self.responses = [*responses]
        self.calls = 0

    def get_config(self) -> Any:
        return {}

    def update_config(self, **model_config: Any) -> None:
        pass

    async def structured_output(
        self, output_model: type[T], prompt: Messages, system_prompt: str | None = None, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        yield {}

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: Any | None = None,
        system_prompt_content: Any | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Any, None]:
        if self.calls >= len(self.responses):
            raise AssertionError(f"the model was called {self.calls + 1} times; the script has {len(self.responses)}")
        response = self.responses[self.calls]
        self.calls += 1
        for event in _events(response):
            yield event


def _events(message: Message) -> Iterable[dict[str, Any]]:
    stop_reason: StopReason = "end_turn"
    yield {"messageStart": {"role": "assistant"}}
    for content in message["content"]:
        if "text" in content:
            yield {"contentBlockStart": {"start": {}}}
            yield {"contentBlockDelta": {"delta": {"text": content["text"]}}}
            yield {"contentBlockStop": {}}
        if "toolUse" in content:
            stop_reason = "tool_use"
            use = content["toolUse"]
            yield {"contentBlockStart": {"start": {"toolUse": {"name": use["name"], "toolUseId": use["toolUseId"]}}}}
            yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(use["input"])}}}}
            yield {"contentBlockStop": {}}
    yield {"messageStop": {"stopReason": stop_reason}}


def tool_use(name: str, input: dict[str, Any], uid: str) -> dict[str, Any]:
    """Return a ``toolUse`` content block."""
    return {"toolUse": {"name": name, "input": input, "toolUseId": uid}}
