# Multi-Agent Game Studio — the "Human-Bus" approach

A **multi-agent system (MAS)** that builds a small desktop game — with **no API keys and no cost**.

Instead of running agents through a framework, **each agent is a Claude Code chat session that
adopts a role** from a Markdown file in [`roles/`](roles/). The repo's [`workspace/`](workspace/)
folder is the shared **blackboard**. **You are the message bus**: when one agent finishes, it prints
a small copy-paste **HANDOFF** block; you open a new chat and paste it, and a fresh context window
picks up as the next agent.

This is a real MAS — specialized roles, orchestrator-worker routing, shared memory, agent-to-agent
messaging, and a QA→Programmer feedback loop — and because every "agent" is Claude Code, each one
has **real tools**: it can read/write files, **run the game**, and search the web while in character.

## How it works

```
You: "Let's build a game. Theme: <your theme>"   ──►  [chat 1] Orchestrator
                                                          │ prints a HANDOFF block
   you paste it into a new chat ───────────────────────►  [chat 2] Business Analyst
                                                          │ HANDOFF
                                                     ...   Designer → Artist → Writer → Level Designer
                                                          │ HANDOFF
                                                     ──►  [chat n] Programmer  (writes & runs the game)
                                                          │ HANDOFF
                                                     ──►  QA Tester  ──FAIL──► back to Programmer
                                                                      ──PASS──► Orchestrator → DONE
```

- **`CLAUDE.md`** is auto-loaded in every chat. It tells Claude how to pick its role (from the
  `Role:` line in a pasted handoff, or default to the Orchestrator) and how to hand off.
- **`workspace/`** is the shared blackboard, **scoped into per-role folders** so each agent loads only
  what it needs (see [`workspace/README.md`](workspace/README.md) for the map):
  `shared/` (brief, backlog board, handoffs — read by everyone), and one folder per role —
  `requirements/`, `design/` (the GDD), `art/`, `story/`, `levels/`, `qa/` — each holding that role's
  spec + a `history.md`. `archive/` keeps frozen history out of the way; `game/` is the actual game.
  This structure is owned by the **Manager** role.

## The roles

| Role | Turns ... into ... |
|------|--------------------|
| Orchestrator (Producer) | a theme into a plan; routes everyone; declares done |
| Business Analyst | the theme into testable requirements |
| Lead Game Designer | requirements into a Game Design Document |
| Artist | the GDD into a placeholder-art spec (palette + shapes) |
| Writer | the GDD into title + on-screen copy |
| Level Designer | the GDD into spawn rules + difficulty curve |
| Programmer | all the specs into the modular `workspace/game/` package (pygame-ce) |
| QA Tester | the build into a PASS/FAIL by actually running it |
| Manager | a chaotic workspace into a scoped, low-overhead knowledge base (off-pipeline) |

## Setup (one time)

Requires **Python 3.14** (the `.venv` here is built with it).

```powershell
# If you ever need to recreate the env:
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt   # just pygame-ce
```

No `.env`, no API key — the agents are chat sessions, not API calls.

## Run the studio (the fun part)

1. **Start a chat** in this repo and say: *"Let's build a game. Theme: `<your one-line theme>`."*
   Claude becomes the **Orchestrator**, records your theme in `workspace/shared/brief.md`, and prints
   a **HANDOFF** block.
2. **Open a new chat**, paste the block. That chat becomes the next agent, does its job, writes its
   artifact, and prints the next HANDOFF.
3. **Repeat** down the pipeline until the Programmer produces the game and QA passes it.
4. **Play it:**
   ```powershell
   .\.venv\Scripts\python.exe workspace\game\main.py
   ```

Watch [`workspace/shared/handoffs.md`](workspace/shared/handoffs.md) fill up — that's the agents'
"conversation", and the whole point: seeing a multi-agent system collaborate.

## Tips

- Lost the thread? Start a chat and ask the **Orchestrator** "what's next?" — it reads
  `workspace/shared/backlog.md` and tells you who works next.
- Workspace feeling cluttered or the docs getting huge? Start a chat as the **Manager**
  (`Role: manager`) and ask it to reorganize — it scopes the knowledge base and realigns the roles.
- You can run several roles in sequence yourself, but the intended experience is **one role per chat**
  (separate context windows), with you carrying the handoffs.
- The game is deliberately tiny: one screen, keyboard-only, placeholder shapes. That's a feature.
