# strands-loop-guard

A community plugin for [Strands Agents](https://strandsagents.com) that stops an agent that asks for the same tool calls again.

[![PyPI](https://img.shields.io/pypi/v/strands-loop-guard)](https://pypi.org/project/strands-loop-guard/)
[![CI](https://github.com/serenearyal/strands-loop-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/serenearyal/strands-loop-guard/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/serenearyal/strands-loop-guard/blob/main/LICENSE)

## The problem

Sometimes a model asks for exactly the same batch of tool calls it already made: same tools, same inputs.
The results are already in the conversation, so the repeat spends a full cycle for nothing.
A model that has started to circle often repeats again, until the turn limit or the token limit stops it.
A turn limit caps the damage, but it cannot tell a useful cycle from a wasted one.

`LoopGuard` notices the repeat.
On the first repeat it adds a short note under the tool results, where the model reads them.
On the second repeat it ends the turn.

## Install

```bash
pip install strands-loop-guard
```

It needs `strands-agents` 1.51.0 or later and Python 3.10 or later.

## Usage

```python
from strands import Agent
from strands_loop_guard import LoopGuard

agent = Agent(tools=[get_sensor_series, read_live], plugins=[LoopGuard(ignore={"read_live"})])
result = agent("Is my O2 sensor bad?")
```

To read what the guard saw, pass your own `invocation_state` dict and read it after the call:

```python
state = {}
agent("Is my O2 sensor bad?", invocation_state=state)
guard = LoopGuard.state(state)  # LoopGuardState(hits=..., stopped=..., ...) or None
```

## Options

All options are keyword-only.

| Option | Default | Meaning |
|--------|---------|---------|
| `nudge_after` | `1` | Repeats before the guard adds the note to the tool-result turn. |
| `stop_after` | `2` | Repeats before the guard ends the turn. `None` adds notes only and never stops. |
| `nudge` | `DEFAULT_NUDGE` | The note text. `{tools}` expands to the names of the repeated tools. |
| `stop` | `DEFAULT_STOP` | The final assistant text when the guard ends the turn. `{tools}` expands the same way. |
| `ignore` | `()` | Names of tools whose calls never count, for example a live reading or a clock that the model asks again on purpose. A batch of only these tools is never a repeat. |

A repeat is counted per invocation: each new call to the agent starts from zero.

## How it works

On `BeforeToolsEvent` the guard makes a signature of the batch: the tool names and inputs of each `toolUse` block, sorted, so call order and tool use ids do not matter.
If an earlier batch in the same invocation had the same signature, it counts a repeat in `invocation_state`; a batch that a per-tool interrupt splits is counted once.
On `AfterToolsEvent` it appends the note as a text block to the tool-result message, or it sets `end_turn`, so the run ends with `stop_reason == "end_turn"` and the `stop` text as the final message.
It uses only these two public hooks and never edits the assistant message, so it works with any model provider.

## In production

The guard comes from the AI mechanic in the ScanMyCar app, which runs a tool loop over a car owner's logged drives (sensor series, stored codes, freeze frames).
It has run there since September 2026.
In one week, 11 of 90 runs asked for a batch they had already asked for at least once, and the guard stopped 3 chat runs.
In one of those chats the model sent the same failing call again word for word; the note is what broke that loop.

## Background

This package started as a feature request for the Strands SDK: [strands-agents/harness-sdk#4262](https://github.com/strands-agents/harness-sdk/issues/4262).
The maintainers suggested shipping it as a community plugin.

This is a community package.
It is not an official Strands Agents package and is not maintained by the Strands team.

## Development

```bash
pip install hatch
hatch run prepare   # format, lint, type check, tests
```

The tests drive a real `strands.Agent` through its event loop with a scripted model and real `@tool` functions.

## License

Apache 2.0. See [LICENSE](https://github.com/serenearyal/strands-loop-guard/blob/main/LICENSE).
