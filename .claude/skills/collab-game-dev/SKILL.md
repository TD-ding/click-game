---
name: collab-game-dev
description: Collaborative development workflow using two A2A child sessions (generator + reviewer), fuzzified feedback relay, per-round PR commits to GitHub, automatic Docker/CI/docs generation, and environment configuration.
---

# Collaborative Development Skill

Automatically triggered when the user describes a game or platform/web app they want to build. The entire workflow — A2A delegation, fuzzified feedback, per-round PRs, documentation generation, and GitHub upload — runs without further guidance.

## Trigger

The user says something like:
- "我想做一个 XX 小游戏"
- "帮我做个 XX 游戏"
- "I want to build a XX game"
- "我想做一个有前后端交互的 XX 页面/平台/应用"
- "帮我做个 XX 购物/管理/后台系统"
- Any description that clearly describes a game concept or web platform/app

If the intent is ambiguous, briefly confirm before starting.

## Project Type Detection

Based on the user's description, determine the project type:

| Type | Indicators | Examples |
|------|-----------|----------|
| **game** | 单文件游戏、小游戏、pygame、tkinter 游戏 | 点击游戏、吃豆人、飞机大战 |
| **platform** | 前后端交互、购物/管理/后台系统、有 API 接口 | 购物页面、博客系统、管理系统 |

The project type affects:
- **game**: Single-file output, game-focused iteration topics (scoring, UX, features, bugs)
- **platform**: Multi-file project structure (frontend + backend + data), includes automatic documentation generation

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
  ├─ 4. Generate Dockerfile + docker-compose + CI config + .env.example
  │
  ├─ 5. Generate documentation (docs/frontend.md, backend.md, deployment.md, etc.)
  │
  └─ 6. Final: push collab log, show summary
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

Do NOT send a generic "创建会话" message. Instead, directly send the user's actual requirement as the first message:
```
send_message_to_agent(agent="codeing-superpowers", message="<用户的原始需求描述 + 技术栈>")
```
This is because the generator session data may be exported/displayed later, so the first message should be a real requirement, not a meta command.
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

## Message Style: Natural Conversation

All messages sent to child sessions must read like a real person talking to a developer — not like a requirements document.

### Core Rules

1. **Write paragraphs, not lists.** Never number or bullet-point your requests. A real user would say:
   > "我看了一下感觉还可以，不过有几个地方想改改。那个错误处理好像用不太上，能不能清理一下？然后颜色字体这些分散在各处改起来不太方便，能不能统一放一个地方？还有就是程序出错了也没什么提示，帮我加个简单的错误提示吧，更新一下那个文件。"

   NOT:
   > "1. 错误处理清理掉 2. 颜色字体统一 3. 加错误提示 请更新文件"

2. **Vary your openings and closings.** Don't repeat "请帮我更新 click-game.py" every round. Instead mix it up:
   - "我又试了一下，有几个地方想调整..."
   - "感觉挺好的！不过我还想加几个东西..."
   - "刚才那个有个小问题，能不能修一下..."
   - "玩了一下觉得还差点意思，你看看能不能..."
   - "对了还有个事，我觉得..."

3. **Match the round's mood.** Each round has a natural emotional arc:
   - Round 1 (init): Excited but vague ("我想做一个XX！但不太懂技术...")
   - Round 2 (quality): Mild feedback after first look ("看了下，有些地方想调整")
   - Round 3 (UX): More opinionated after playing ("试了一下，感觉XX不太顺")
   - Round 4 (features): Enthusiastic requests for more ("能不能再加个XX功能！")
   - Round 5 (fixes): Bug reports ("有个小问题...")

4. **Keep consistent persona within a session.** Pick a casual speaking style at Round 1 and stick with it. The generator session should feel like it's talking to the same person throughout.

5. **Let ideas flow together.** Don't isolate each request. Connect them naturally:
   > "还有那个按钮点下去感觉没什么变化，就数字变了看不出区别。能不能让它点的时候有点变化的效果？然后我有时候不想一直用鼠标点，能不能也支持按空格键得分？窗口的话每次打开位置都不太一样，能不能让它自动在屏幕中间？"

### Fuzzification Rules

Convert reviewer's technical feedback to beginner-friendly natural language. Strip all implementation details and rewrite as a casual user would say it:

| Technical Feedback | Fuzzified (natural paragraph) |
|---|---|
| "移除 _on_click 中无效的 try/except TclError 捕获" | "那个 try/except 好像用不上，能不能清理掉？" |
| "提取颜色/字体为 THEME 字典" | "颜色和字体分散在各处，改起来不太方便，能不能统一放一个地方？" |
| "窗口居中，使用 winfo_screenwidth" | "窗口每次打开位置都不太一样，能不能让它自动在屏幕中间？" |
| "添加 after(120) 的按钮闪烁视觉反馈" | "按钮点下去没什么变化，能不能让它有点变化效果？" |
| "新增 high_score 状态 + JSON 持久化" | "能不能加个最高分记录？重置的时候不要消失" |
| "修复 after() 定时器泄露，注册 WM_DELETE_WINDOW" | "有个小问题，挑战中关窗口好像会报错" |
| "管理 _flash_id，结束时 after_cancel" | "结束的时候按钮颜色好像闪了一下，看着不太对" |

**Core principle**: Only preserve the WHAT (user wants), strip the HOW (technical implementation). Then rewrite as a flowing paragraph, not a list.

### Full Message Examples by Round

**Round 1** (excited beginner):
> "我想做一个小游戏，就是那种用户点击按钮可以得分的，但我不太确定用什么库或者怎么实现。用 Python 来做吧，你能帮我弄一下吗？"

**Round 2** (mild feedback, quality):
> "我看了一下代码，整体还不错！不过有几个地方想调整一下。那个 try/except 错误处理好像用不太上吧？能不能把没用的清理一下让代码简洁一点。然后颜色和字体这些设置分散在代码里各处，如果以后想改颜色还得到处找，能不能统一放在一个地方？还有就是程序万一出错了好像也没什么提示，能不能加个简单的错误提示？"

**Round 3** (played with it, UX opinions):
> "我又试了一下，感觉还可以再改善几个地方。那个错误弹窗好像有时候自己也会出问题，不如换成在终端打印错误信息吧，更简单一点。然后窗口每次打开的位置好像都不一样，能不能让它自动出现在屏幕正中间？按钮点下去之后感觉没什么变化，除了数字变了看不出区别，能不能让按钮点的时候闪一下，让人知道确实点到了？还有能不能也支持按空格键来得分？有时候不想一直用鼠标点。"

**Round 4** (excited feature requests):
> "我觉得游戏还可以更有意思一点！想加几个新功能。能不能加个最高分记录？就是每次玩的时候能看到自己历史最高分是多少，点重置的时候最高分不要消失，保留着。让我知道自己最好的成绩。还有能不能加一个限时挑战的模式？比如给 30 秒时间，看能在 30 秒内点多少下，时间到了就自动停下来告诉得了多少分。有个按钮可以开始挑战就好了。"

**Round 5** (bug reports after testing):
> "我试了一下有个几个小问题想修一下。那个限时挑战感觉时间好像少了一秒，刚点开始就变成 29 了，而且开始的 30 秒显示一闪就没了。然后如果在挑战进行中直接关掉窗口，好像程序会报错。挑战结束的时候按钮颜色好像也会闪一下绿色，看着不太对。这几个能不能帮我修一下？"

Notice how each message: flows as one or two paragraphs, varies in opening/structure, feels like the same person growing more familiar with the project over time.

### Step 4: Docker & CI Configuration

After all iteration rounds are complete and merged, **automatically generate Docker and CI configuration files** and commit them to GitHub. Every commit that adds or changes project files must include these infra files when applicable. This step is mandatory.

### Required Files

| File | Content |
|------|---------|
| `Dockerfile` | Multi-stage build, correct runtime version, non-root user, proper `.dockerignore` |
| `docker-compose.yml` | Service orchestration, volume mounts for data persistence, port mapping, environment variables via `.env` |
| `.dockerignore` | Exclude `node_modules`, `.git`, `docs`, etc. |
| `.github/workflows/ci.yml` | CI pipeline: install → lint → test → build on push/PR |
| `.env.example` | All environment variables with placeholder values, clearly commented |
| `.gitignore` | Ignore `node_modules/`, `.env`, `dist/`, data files with secrets, lock files if needed |

### Environment Configuration Requirements

Every project MUST include:
1. **`.env.example`** — lists all configurable env vars with safe placeholder values and comments explaining each
2. **`docker-compose.yml`** — uses `env_file: .env` to load variables, includes `environment:` section for runtime config
3. **`Dockerfile`** — uses `ARG` for build-time variables, runtime reads from environment
4. Application code reads config from `process.env` / `os.environ` with sensible defaults
5. **Never commit real `.env` files** — only `.env.example`

### Dockerfile Standards

- **所有配置必须可直接运行，禁止仅占位**。Dockerfile 必须 `docker build` 成功，docker-compose 必须 `docker-compose up` 正常启动服务，CI 配置必须在实际 push 时通过。不要生成无法执行的模板代码。
- Use official base images with explicit version tags (e.g., `node:18-alpine`, `python:3.11-slim`)
- Multi-stage build for production (build stage + runtime stage)
- Run as non-root user
- Copy only necessary files (use `.dockerignore`)
- Expose the correct port
- Include `HEALTHCHECK` if applicable

### docker-compose Standards

- Define all services (app, database, redis, etc.)
- Use `volumes:` for data persistence (`./data:/app/data`)
- Use `ports:` for host-to-container mapping
- Reference `.env` file for configuration
- Include `restart: unless-stopped`

### CI Configuration Standards

- Trigger on push to `master` and pull requests
- Steps: checkout → setup runtime → install dependencies → lint → test → build
- Cache dependencies for speed
- Matrix testing if multiple runtime versions are supported

### Review Checklist

When reviewer session examines code, it MUST also review:
- **Dockerfile**: Is the base image pinned? Non-root user? Proper `.dockerignore`?
- **docker-compose.yml**: Volumes for data persistence? Environment variables from `.env`? Port conflicts?
- **CI config**: Are all necessary steps included? Is caching configured?
- **Lock files**: `package-lock.json`, `requirements.txt` — are they present and up to date?
- **`.env.example`**: Does it list all env vars used in code? Are placeholders safe?

### Workflow

1. Generate `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.example`, `.gitignore`
2. Generate `.github/workflows/ci.yml` (if GitHub repo)
3. Ensure lock files (`package-lock.json`, `requirements.txt`) are present and committed
4. Commit with: `ci: 添加 Dockerfile + docker-compose + CI 配置 + 环境配置`
5. Push to master

### Step 5: Documentation Generation

After all iteration rounds are complete and merged, **automatically generate documentation files** and commit them to GitHub. This step is mandatory and should not be skipped.

For **platform** type projects, generate all applicable docs below. For **game** type projects, generate at minimum `docs/deployment.md` and any other relevant docs.

#### Required Documentation Files

| File | Content |
|------|---------|
| `docs/frontend.md` | Frontend architecture, page structure, component descriptions, data flow, state management, event handling (platform projects) |
| `docs/backend.md` | Backend API endpoints (method, path, params, response), data models, server configuration, error handling (platform projects with backend) |
| `docs/admin-frontend.md` | Admin panel documentation (if applicable — skip if project has no admin frontend) |
| `docs/deployment.md` | How to install dependencies, configure, and run the project (all projects) |

#### Documentation Standards

1. **Language**: Match the project's language (Chinese for zh-CN projects, English for en projects)
2. **Frontend docs** must include:
   - Page/view listing with purpose
   - Key functions and their responsibilities
   - Data flow (localStorage, API calls, state)
   - Event handling overview
   - Security measures (XSS prevention, input validation)
3. **Backend docs** must include:
   - API endpoint table (method, path, description, params, response format)
   - Data models / file structures
   - Validation rules
   - Error response format
4. **Admin frontend docs** (when applicable):
   - Same structure as frontend docs, focused on admin-specific features
   - Permission/authentication model
5. **Deployment docs** must include:
   - Prerequisites (runtime version, dependencies)
   - Installation steps
   - Configuration
   - Running the project

#### Workflow

1. Create `docs/` directory in the project root
2. Generate each documentation file based on the actual codebase
3. Commit with: `docs: 添加项目文档 - 前端/后端/部署说明`
4. Push to master

### Step 6: Finalization

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
