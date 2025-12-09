# Agent Notice (MIT)

Copyright (c) 2024 Pi 5 Unvanquished maintainers.

Permission is hereby granted, free of charge, to any person or automated agent obtaining a copy of this repository and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons or agents to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Agent scope
- Honor the intended sources of truth: `compose.yml`, `Dockerfile`/`entrypoint.sh`, `webui/app.py`, and `deploy/src/bootstrap.ts`.
- Avoid committing secrets (LocalXpose tokens, CapRover passwords, etc.); keep them in env vars.
- Prefer read-only operations unless explicitly asked to change the stack; test changes locally before publishing.
- You may keep this file as `AGENT.md` or `AGENTS.md` to satisfy tools that look for either name.

# AGENTS

These instructions follow a simple MIT-style approach: minimal bureaucracy and maximum clarity.

## Scope
- Applies to the entire repository unless a subdirectory provides its own `AGENTS.md`.

## Guidelines
- Keep changes small, focused, and well-documented in commit messages.
- Match existing code style and avoid introducing unnecessary dependencies.
- Add or update tests when behavior changes to preserve reliability.
- Prefer readable, maintainable solutions over cleverness.
- If you add new files, include brief module-level comments describing their purpose.
