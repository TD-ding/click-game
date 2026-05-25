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

### Step 4: Lint, Tests, Docker & CI Configuration

After all iteration rounds are complete and merged, **automatically generate lint config, unit tests, Docker and CI configuration files** and commit them to GitHub. This step is mandatory and directly maps to the repo 验收标准.

#### 4.1 Lint 配置（验收项：Lint 检查通过）

每个项目必须配置 Linter，确保零 Error 级别违规：

| 语言 | Linter | 配置文件 | 额外依赖 |
|------|--------|----------|----------|
| JavaScript/Node.js | ESLint (flat config) | `eslint.config.js` | `npm install --save-dev eslint globals` |
| Python | flake8 或 ruff | `.flake8` 或 `pyproject.toml` | `pip install flake8` |

**ESLint 配置要求**：
- 使用 ESLint v9+ flat config 格式（`eslint.config.js`），不使用 `.eslintrc.json`
- **必须按文件类型拆分配置**：
  - `server.js`：使用 `globals.node` 环境，`sourceType: 'commonjs'`
  - `public/**/*.js`：使用 `globals.browser` 环境，`sourceType: 'script'`，`no-undef` 设为 `off`（浏览器 API 不需全部声明）
  - `test/**/*.js`：使用 `globals.node` + `globals.jest`，`sourceType: 'commonjs'`
- 必须包含规则：`no-unused-vars`, `eqeqeq`（强制 `===`）, `no-var`, `prefer-const`, `no-dupe-keys`, `no-empty`, `no-unreachable`
- 在 `package.json` 中添加 `"lint": "eslint server.js public/*.js"` 脚本
- **本地验证**：运行 `npx eslint server.js public/*.js` 确保 **零 error 输出**后再提交

#### 4.2 单元测试（验收项：单元测试完整性）

每个项目必须包含可运行的单元测试：

**Node.js 项目**：
- 安装：`npm install --save-dev jest supertest`
- 测试目录：`test/`
- `package.json` 添加 `"test": "jest --forceExit --detectOpenHandles"`
- 服务端代码必须 `module.exports = app` 且 `app.listen()` 仅在 `require.main === module` 时执行
- 测试内容必须覆盖：
  - 核心业务逻辑（注册/登录/CRUD）
  - 输入验证（正常路径 + 异常路径）
  - 权限控制（未登录、非管理员）
  - 有意义的断言（检查 status code、response body 字段）
- 运行 `npm test` 确保全部通过

**Python 项目**：
- 使用 `pytest`，测试目录 `tests/`
- 测试覆盖核心函数和游戏逻辑

**游戏项目（单文件 Python）**：
- 至少编写游戏核心逻辑的单元测试（得分计算、状态转换、边界条件）
- 测试目录 `tests/`，文件名 `test_<game>.py`

#### 4.3 代码注释（验收项：代码中关键逻辑有注释）

在生成代码时和 Step 4 完成后，确保核心业务模块有注释：
- 每个功能分组添加注释说明
- 关键业务逻辑（认证、状态管理、得分计算）添加注释说明 WHY
- 配置常量添加注释说明用途
- 验收标准：sota 模型抽查通过率 > 80%

#### 4.4 Docker & CI 配置文件

| File | Content |
|------|---------|
| `Dockerfile` | Multi-stage build, correct runtime version, non-root user, proper `.dockerignore` |
| `docker-compose.yml` | Service orchestration, volume mounts for data persistence, port mapping, environment variables via `.env` |
| `.dockerignore` | Exclude `node_modules`, `.git`, `docs`, etc. |
| `.github/workflows/ci.yml` | CI pipeline: install → lint → test → health check on push/PR |
| `.env.example` | All environment variables with placeholder values, clearly commented |
| `.gitignore` | Ignore `node_modules/`, `.env`, `dist/`, data files with secrets |

#### Environment Configuration Requirements

Every project MUST include:
1. **`.env.example`** — lists all configurable env vars with safe placeholder values and comments
2. **`docker-compose.yml`** — uses `env_file: .env` to load variables
3. **`Dockerfile`** — uses `ARG` for build-time variables, runtime reads from environment
4. Application code reads config from `process.env` / `os.environ` with sensible defaults
5. **Never commit real `.env` files** — only `.env.example`

#### Dockerfile Standards

- **所有配置必须可直接运行，禁止仅占位**
- Use official base images with explicit version tags
- Run as non-root user
- Include `HEALTHCHECK` if applicable

#### CI Configuration Standards（关键：路径必须正确）

- Trigger on push to `master` and pull requests
- Steps: checkout → setup runtime → install → lint → test → health check
- Cache dependencies for speed
- **路径注意**：CI 在项目仓库内运行，文件在仓库根目录。**禁止**添加 `working-directory` 指向子目录，除非项目确实是 monorepo
- CI 必须包含 `npm run lint` 和 `npm test` 步骤

#### Workflow

1. 配置 Linter（`eslint.config.js` 或 `.flake8`）
2. 编写单元测试（`test/` 或 `tests/`）
3. 补充核心代码注释
4. 生成 `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.example`, `.gitignore`
5. 生成 `.github/workflows/ci.yml`（路径正确，包含 lint + test 步骤）
6. Ensure lock files (`package-lock.json`, `requirements.txt`) are present and committed
7. **本地验证**：运行 `npm run lint` 和 `npm test` 确保通过
8. Commit with: `feat: 添加 lint 配置 + 单元测试 + Docker/CI 配置 + 环境配置`
9. Push to master

### Step 5: Documentation Generation

After all iteration rounds are complete and merged, **automatically generate documentation files** and commit them to GitHub. This step is mandatory and should not be skipped.

For **platform** type projects, generate all applicable docs below. For **game** type projects, generate at minimum `docs/deployment.md` and any other relevant docs.

#### Required Documentation Files

| File | Content |
|------|---------|
| `docs/frontend.md` | Frontend architecture, page structure, component descriptions, data flow, state management, event handling (platform projects) |
| `docs/backend.md` | Backend API endpoints (method, path, params, response format, authentication, error codes), data models, server configuration (platform projects with backend) |
| `docs/admin-frontend.md` | Admin panel documentation (if applicable — skip if project has no admin frontend) |
| `docs/deployment.md` | How to install dependencies, configure, and run the project. Must include: runtime version, system dependencies, environment variables, third-party services |

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
