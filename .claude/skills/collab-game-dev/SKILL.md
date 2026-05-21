---
name: collab-game-dev
description: Collaborative game development workflow using two A2A child sessions (generator + reviewer), fuzzified feedback relay, and per-round PR commits to GitHub.
---

# Collaborative Game Development Skill

Automatically triggered when the user describes a game they want to build. The entire workflow — A2A delegation, fuzzified feedback, per-round PRs, and GitHub upload — runs without further guidance.

## Trigger

The user says something like:
- "我想做一个 XX 小游戏"
- "帮我做个 XX 游戏"
- "I want to build a XX game"
- Any description that clearly describes a game concept

If the intent is ambiguous, briefly confirm before starting.

## Workflow Overview

```
User: "我想做一个XX游戏"
  │
  ├─ 1. Init Git + GitHub repo (README only)
  │
  ├─ 2. Create 2 A2A child sessions
  │     ├─ Session A: codeing-superpowers (generator)
  │     └─ Session B: codeing-superpowers (reviewer)
  │
  ├─ 3. Iteration loop (max 5 rounds):
  │     ├─ Send fuzzified request → Generator → code
  │     ├─ Forward code → Reviewer → feedback
  │     ├─ Fuzzify feedback → next round input
  │     └─ Each round: branch → commit → PR → merge
  │
  └─ 4. Final: push collab log, show summary
```

## Step-by-step Execution

### Step 1: Repository Setup

1. Create `README.md` with game name, brief description, placeholder for dev process table.
2. `git init`, set user config, initial commit.
3. `gh repo create <game-name> --public --source=. --push`.
4. If `gh` is not authenticated, ask user for token and run `echo "<token>" | gh auth login --with-token`.

### Step 2: Create Two A2A Child Sessions

Use `mcp__agent-cloud-delegation__send_message_to_agent` with agent `codeing-superpowers` twice:

**Session A — Generator** (generation/modification):
```
send_message_to_agent(agent="codeing-superpowers", message="创建游戏生成/修改会话")
```
Save `contextId` and `taskId` as `gen_contextId` and `gen_taskId`.

**Session B — Reviewer** (optimization/review):
```
send_message_to_agent(agent="codeing-superpowers", message="创建优化建议/代码审查会话")
```
Save `contextId` and `taskId` as `rev_contextId` and `rev_taskId`.

**Important**: All subsequent interactions with these sessions must use `continue_agent_task` with the saved `contextId` and `taskId` to maintain conversation continuity.

### Step 3: Iteration Loop

Run up to **5 rounds**. Each round follows this pattern:

#### Round N: Generate/Modify

1. **Create feature branch**: `git checkout -b <type>/round<N>-<slug>` from latest master
   - Round 1: `feat/round1-init`
   - Round 2: `refactor/round2-code-quality`
   - Round 3: `feat/round3-ux`
   - Round 4: `feat/round4-features`
   - Round 5: `fix/round5-bugs`
2. **Send to Generator** via `continue_agent_task(gen_contextId, gen_taskId, <message>)`
   - Round 1: Forward the user's original input verbatim + tech stack choice
   - Round 2+: Forward the **fuzzified** feedback from previous reviewer round
3. **Write the generated code** to the game file
4. **Commit + Push**: `git add <file> && git commit -m "<conventional-commit>" && git push -u origin <branch>`
5. **Create PR**: `gh pr create --base master --head <branch> --title "第<N>轮: <type> - <title>" --body "<PR body>"`
   - PR body must include: **模糊化输入** section + **改动** section + **迭代链路** section
6. **Merge PR**: `gh pr merge <N> --merge --delete-branch`
7. **Sync local**: `git checkout master && git pull`

#### Round N: Review (skip for Round 1, or run in parallel)

1. **Send code to Reviewer** via `continue_agent_task(rev_contextId, rev_taskId, <message>)`
   - Include the latest code content or instruct reviewer to read from shared workspace
2. **Receive feedback** (code quality, UX, features, bugs)
3. **Fuzzify feedback** — convert technical suggestions into beginner-friendly language:
   - Remove all technical terms (THEME dict, TclError, WM_DELETE_WINDOW, etc.)
   - Use casual, natural language ("按钮点下去没什么变化" instead of "缺少视觉反馈")
   - Keep only the improvement intent, not implementation details
   - Split into batches if too many suggestions

### Step 4: Fuzzification Rules

Convert reviewer's technical feedback to beginner-friendly language. Examples:

| Technical Feedback | Fuzzified Version |
|---|---|
| "移除 _on_click 中无效的 try/except TclError 捕获" | "那个 try/except 好像用不上，能不能清理掉？" |
| "提取颜色/字体为 THEME 字典" | "颜色和字体分散在各处，改起来不方便，能不能统一放在一个地方？" |
| "窗口居中，使用 winfo_screenwidth" | "窗口每次打开位置不一样，能不能居中？" |
| "添加 after(120) 的按钮闪烁视觉反馈" | "按钮点下去没什么变化，能不能闪一下？" |
| "新增 high_score 状态 + JSON 持久化" | "能不能加个最高分记录？重置的时候不要消失" |
| "修复 after() 定时器泄露，注册 WM_DELETE_WINDOW" | "挑战中关窗口会报错，能不能修一下？" |
| "管理 _flash_id，结束时 after_cancel" | "结束的时候按钮颜色会闪一下，不太对" |

**Core principle**: Only preserve the WHAT (user wants), strip the HOW (technical implementation).

### Step 5: Finalization

1. **Push collab log**: Commit `collab-log.md` with full iteration records to master.
2. **Show summary**: Display git log, PR list, repo URL.
3. **Security note**: If user provided a GitHub token in chat, remind them to revoke and regenerate it.

## PR Title and Commit Message Convention

- **Round 1**: `feat: 初始版本 - <description>`
- **Round 2**: `refactor: 代码质量优化 (第2轮)`
- **Round 3**: `feat: 用户体验优化 (第3轮)`
- **Round 4**: `feat: 功能增强 (第4轮)`
- **Round 5**: `fix: Bug修复 (第5轮)`
- **Final**: `docs: 添加协作开发日志 - 完整迭代记录与模糊化反馈`

Each commit message includes the fuzzified input as context.

## PR Body Template

```markdown
## 背景
<Which round, what triggered this change>

## 模糊化输入（生成会话收到的）
> '<fuzzified user-facing message>'

## 改动
- <bullet list of changes>

## 迭代链路
...→ 优化会话(审查) → **主会话模糊化** → 生成会话(本PR)
```

## Session Communication Rules

1. **Generator session** handles all code creation and modification
2. **Reviewer session** handles all code review and optimization suggestions
3. **Main session** acts as coordinator — all messages between sessions pass through main
4. **Fuzzification** always happens in main session before forwarding to generator
5. Keep `contextId` and `taskId` for each session — reuse with `continue_agent_task` for all follow-ups

## Error Handling

- If `gh` not authenticated: ask user for token
- If `codeing-superpowers` agent not found: list available agents and adapt
- If child workspace differs from main workspace: delegate file operations to child sessions, retrieve content via messages
- If PR creation fails: check branch push status and retry

## Game File Requirements

- Single runnable Python file (or as user specifies)
- Must include: game logic, scoring, display, error handling
- Code should be clean and maintainable
- Save to shared workspace accessible by both sessions
