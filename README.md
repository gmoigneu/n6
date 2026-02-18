# Number 6

> *"I'm not a number, I'm a free man!"* — but she is.

Number 6 is a personal AI-powered CLI assistant, named in honor of Caprica Six from *Battlestar Galactica*. It handles a mix of everyday tasks: some are pure code utilities, others leverage an LLM under the hood.

## Install

```bash
uv sync
```

Or install globally with [uv tool](https://docs.astral.sh/uv/concepts/tools/):

```bash
uv tool install .
```

## Configuration

Set your API keys via env vars or `~/.n6.toml`:

```toml
# ~/.n6.toml
anthropic_api_key = "sk-ant-..."
zai_api_key = "..."
```

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude (Anthropic) backend |
| `ZAI_API_KEY` | GLM-5 (Z.AI) backend |

## Usage

```bash
n6 --help

# Ask Claude (default)
n6 ask "Summarize the latest news on fusion energy"

# Ask GLM-5 via Z.AI
n6 ask "Translate this to French: hello world" --backend glm

# Pipe input
echo "explain this code" | n6 ask -
```

## LLM Backends

| Backend | Flag | Model |
|---|---|---|
| Claude (Anthropic) | `--backend claude` | `claude-sonnet-4-6` |
| GLM-5 (Z.AI) | `--backend glm` | `glm-5` |

Override the model with `--model <name>`.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
