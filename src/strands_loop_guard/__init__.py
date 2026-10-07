"""Loop guard plugin for Strands Agents: stop an agent that repeats a tool batch.

The first repeat of a tool batch gets a note inside the tool-result turn,
where the model reads its results. The second repeat ends the turn.

Example:
    ```python
    from strands import Agent
    from strands_loop_guard import LoopGuard

    agent = Agent(tools=[get_sensor_series], plugins=[LoopGuard()])
    agent("Is my O2 sensor bad?")
    ```
"""

from strands_loop_guard.plugin import DEFAULT_NUDGE, DEFAULT_STOP, LoopGuard, LoopGuardState, batch_signature

__all__ = [
    "DEFAULT_NUDGE",
    "DEFAULT_STOP",
    "LoopGuard",
    "LoopGuardState",
    "batch_signature",
]
