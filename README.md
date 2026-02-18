# Number 6

> *"I'm not a number, I'm a free man!"* — but she is.

<p align="center">
  <img src="n6.webp" alt="Number 6" width="256" />
</p>

Number 6 is a personal AI-powered CLI assistant, named in honor of Caprica Six from *Battlestar Galactica*. It handles a mix of everyday tasks: some are pure code utilities, others call an LLM under the hood.

## Install

```bash
uv tool install --editable .
```

## Configuration

Create `~/.n6.toml` with your Z.AI API key (required for the GLM backend):

```toml
zai_api_key = "..."
```

The Claude backend uses your existing Claude Code subscription — no API key needed.

## Commands

### `n6 ask`

One-shot prompt to Claude or GLM.

```bash
n6 ask "What is the capital of France?"
n6 ask "Translate this to French: hello world" --backend glm
```

| Option | Default | Description |
|---|---|---|
| `--backend` | `claude` | `claude` or `glm` |
| `--model` | — | Override the model name |
| `--system` | — | System prompt |
| `--no-stream` | off | Disable streaming |

### `n6 summarize`

Pipe any content in, get a ~200-word summary out. Uses the GLM backend.

```bash
cat article.txt | n6 summarize
curl -s https://example.com | n6 summarize
```

### `n6 linkedin-article`

Pipe an article in, get a LinkedIn post out. Uses Claude Sonnet. Output is plain text sized for peak LinkedIn engagement (1,300–1,600 characters).

```bash
cat article.md | n6 linkedin-article
curl -s https://example.com/post | n6 linkedin-article
```

### `n6 linkedin-post`

Write a LinkedIn post from a prompt, opinion, or idea. Uses Claude Sonnet with the same voice and rules as `linkedin-article` — plain text, 1,300–1,600 characters, no emojis or hashtags.

The prompt is the core idea. Pipe in supporting material (a README, a transcript, a snippet) and it gets folded in.

```bash
n6 linkedin-post "My take on why most teams shouldn't adopt microservices"
cat README.md | n6 linkedin-post "Highlight this open source project"
n6 yt-transcript <video-id> | n6 linkedin-post "Key insight from this talk worth sharing"
```

### `n6 blog`

Recursively scans the current directory for `.md` and `.txt` files, treats them as research material, and writes `article.md` using the blog-write skill. Works with any mix of notes, YouTube transcripts, research dumps, or drafts.

```bash
cd ~/research/my-topic/
n6 blog
```

Files are listed to stderr as they're collected. The output is a single cohesive article — not a summary of each file — written to `article.md` in the working directory.

### `n6 ln2bsky`

Convert a LinkedIn post into a Bluesky thread. Each post is capped at 300 characters (Bluesky's actual limit), numbered `1/N`, `2/N`, etc. Splits at natural sentence boundaries and adapts the tone from LinkedIn-professional to Bluesky-direct.

```bash
cat linkedin-post.txt | n6 ln2bsky
n6 linkedin-post "My take on X" | n6 ln2bsky
```

### `n6 yt-transcript`

Fetch a YouTube video transcript and reformat it into readable prose using Claude. Status messages go to stderr so the output can be piped cleanly.

```bash
n6 yt-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ
n6 yt-transcript dQw4w9WgXcQ --lang fr
n6 yt-transcript dQw4w9WgXcQ > transcript.txt
n6 yt-transcript dQw4w9WgXcQ | n6 summarize
n6 yt-transcript dQw4w9WgXcQ --raw   # skip reformatting
```

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
