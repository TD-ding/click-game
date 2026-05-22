---
name: collab-dev
description: General-purpose collaborative development workflow using two A2A child sessions (generator + reviewer), fuzzified feedback relay, per-round PR commits to GitHub, automatic Docker/CI/docs generation, and environment configuration. Supports web apps, APIs, tools, platforms, and more.
---

# Collaborative Development Skill

Automatically triggered when the user describes a software project they want to build (non-game). The entire workflow — A2A delegation, fuzzified feedback, per-round PRs, and GitHub upload — runs without further guidance.

## Trigger

The user describes a software project that is NOT a game. For example:
- "我想做一个 XX 网页" / "帮我做个 XX 网站"
- "我想做一个聊天软件"
- "帮我写一个 XX API"
- "我想做一个 XX 工具"
- "I want to build a XX app"
- Any description of a non-game software project

If the intent is ambiguous, briefly confirm before starting. If it's a game, defer to the `collab-game-dev` skill instead.

## Workflow Overview

```
User: "我想做一个XX"
  │
  ├─ 0. Confirm scope & tech stack (if not obvious)
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

## Step 0: Scope & Tech Stack

Before starting, determine the project parameters. If the user didn't specify:

1. **Project type**: Infer from description (web app, CLI tool, API server, browser extension, etc.)
2. **Tech stack**: Ask briefly if not obvious. Default to reasonable choices:
   - Frontend: HTML/CSS/JS (or React/Vue if user mentions framework)
   - Backend: Python Flask/FastAPI, Node.js Express
   - Full-stack: combine above
   - CLI/tool: Python
   - Don't overthink — pick something and go
3. **File structure**: Single file for simple projects, multi-file for larger ones
4. **Confirm with user** in one short message: "好的，我来帮你做一个 XX，用 [tech stack]，可以吗？"

## Step 1: Repository Setup

1. Create a project directory under the workspace: `<project-name>/`
2. Create `README.md` with project name, brief description, placeholder for dev process table.
3. Inside the project dir: `git init`, set user config, initial commit.
4. `gh repo create <project-name> --public --source=. --push`.
5. If `gh` is not authenticated, ask user for token and run `echo "<token>" | gh auth login --with-token`.

## Step 2: Create Two A2A Child Sessions

Use `mcp__agent-cloud-delegation__send_message_to_agent` with agent `codeing-superpowers` twice:

**Session A — Generator** (generation/modification):

Do NOT send a generic "创建会话" message. Instead, directly send the user's actual requirement as the first message:
```
send_message_to_agent(agent="codeing-superpowers", message="<用户的原始需求描述 + 确认的技术栈>")
```
This is because the generator session data may be exported/displayed later, so the first message should be a real requirement, not a meta command.
Save `contextId` and `taskId` as `gen_contextId` and `gen_taskId`.

**Session B — Reviewer** (optimization/review):
```
send_message_to_agent(agent="codeing-superpowers", message="创建代码审查/优化建议会话")
```
Save `contextId` and `taskId` as `rev_contextId` and `rev_taskId`.

**Important**: All subsequent interactions with these sessions must use `continue_agent_task` with the saved `contextId` and `taskId` to maintain conversation continuity.

## Step 3: Iteration Loop

Run up to **5 rounds**. Each round follows this pattern:

### Round N: Generate/Modify

1. **Create feature branch**: `git checkout -b <type>/round<N>-<slug>` from latest master
   - Round 1: `feat/round1-init`
   - Round 2: `refactor/round2-code-quality`
   - Round 3: `feat/round3-ux`
   - Round 4: `feat/round4-features`
   - Round 5: `fix/round5-bugs`
2. **Send to Generator** via `continue_agent_task(gen_contextId, gen_taskId, <message>)`
   - Round 1: Forward the user's original input + confirmed tech stack
   - Round 2+: Forward the **fuzzified** feedback from previous reviewer round
3. **Write the generated code** to project files
4. **Commit + Push**: `git add . && git commit -m "<conventional-commit>" && git push -u origin <branch>`
5. **Create PR**: `gh pr create --base master --head <branch> --title "第<N>轮: <type> - <title>" --body "<PR body>"`
   - PR body must include: **模糊化输入** section + **改动** section + **迭代链路** section
6. **Merge PR**: `gh pr merge <N> --merge --delete-branch`
7. **Sync local**: `git checkout master && git pull`

### Round N: Review (skip for Round 1, or run in parallel)

1. **Send code to Reviewer** via `continue_agent_task(rev_contextId, rev_taskId, <message>)`
   - Include the latest code content or instruct reviewer to read from shared workspace
2. **Receive feedback** (code quality, UX, features, bugs, security)
3. **Fuzzify feedback** — convert technical suggestions into beginner-friendly language:
   - Remove all technical terms (middleware, CORS, CSRF, DOM, etc.)
   - Use casual, natural language ("页面打开有点慢" instead of "缺少资源懒加载")
   - Keep only the improvement intent, not implementation details
   - Split into batches if too many suggestions

## Message Style: Natural Conversation

All messages sent to child sessions must read like a real person talking to a developer — not like a requirements document.

### Core Rules

1. **Write paragraphs, not lists.** Never number or bullet-point your requests. A real user would say:
   > "我看了一下感觉还可以，不过有几个地方想改改。那个页面加载的时候有点慢，能不能优化一下？然后配色看着不太舒服，能不能换个颜色？还有就是那个表单提交之后没什么反馈，能不能加个提示？"

   NOT:
   > "1. 优化加载速度 2. 换配色 3. 加表单提示 请更新文件"

2. **Vary your openings and closings.** Don't repeat "请帮我更新 XX" every round. Instead mix it up:
   - "我看了一下，有几个地方想调整..."
   - "感觉挺好的！不过我还想加几个东西..."
   - "刚才那个有个小问题，能不能修一下..."
   - "用了一下觉得还差点意思，你看看能不能..."
   - "对了还有个事，我觉得..."

3. **Match the round's mood.** Each round has a natural emotional arc:
   - Round 1 (init): Excited but vague ("我想做一个XX！")
   - Round 2 (quality): Mild feedback after first look ("看了下，有些地方想调整")
   - Round 3 (UX): More opinionated after using ("试了一下，感觉XX不太顺")
   - Round 4 (features): Enthusiastic requests for more ("能不能再加个XX功能！")
   - Round 5 (fixes): Bug reports ("有个小问题...")

4. **Keep consistent persona within a session.** Pick a casual speaking style at Round 1 and stick with it.

5. **Let ideas flow together.** Don't isolate each request. Connect them naturally:
   > "还有那个登录页面，输完密码按回车没反应，非得点按钮才行，能不能加上？然后注册成功之后能不能自动跳转到登录页？不用用户自己点过去。"

### Fuzzification Rules

Convert reviewer's technical feedback to beginner-friendly natural language. Strip all implementation details and rewrite as a casual user would say it:

| Technical Feedback | Fuzzified (natural paragraph) |
|---|---|
| "添加 CORS middleware 配置" | "接口好像跨域访问不了，能不能处理一下？" |
| "输入校验用正则替换手动检查" | "那个输入框好像什么都能输进去，能不能加个验证？" |
| "添加 loading 状态和骨架屏" | "页面加载的时候一片空白，能不能加个加载中的提示？" |
| "用 localStorage 持久化用户设置" | "我改的那些设置刷新页面就没了，能不能保存住？" |
| "修复 XSS 漏洞，转义用户输入" | "输入框里输入特殊字符好像会出问题" |
| "响应式布局，添加 media query" | "手机上看排版有点乱，能不能适配一下？" |
| "错误处理加 try/catch + 用户提示" | "网络不好的时候操作了没什么反应，也不知道成功没" |
| "提取重复的 API 调用为公共函数" | "代码里好多重复的，能不能整理一下？" |

**Core principle**: Only preserve the WHAT (user wants), strip the HOW (technical implementation). Then rewrite as a flowing paragraph, not a list.

### Full Message Examples by Round

**Round 1** (excited beginner):
> "我想做一个待办事项的网页应用，就是那种可以添加任务、标记完成、删除任务的。用 HTML 和 JavaScript 来做吧，就一个单页面就行，你能帮我弄一下吗？"

**Round 2** (mild feedback, quality):
> "我看了一下代码，整体还不错！不过有几个地方想调整一下。那个代码里好多重复的地方，看起来有点乱，能不能整理一下？然后颜色和字体这些设置分散在各处，如果以后想改颜色还得到处找，能不能统一放在一个地方？还有就是程序万一出错了好像也没什么提示，能不能加个简单的错误提示？"

**Round 3** (used it, UX opinions):
> "我又用了一下，感觉还可以再改善几个地方。添加任务的时候输入框按回车没反应，非得点按钮才行，能不能加上？然后任务太多的时候往下滚看着有点累，能不能让已完成的任务有个折叠或者隐藏的功能？还有那个删除按钮点完直接就没了，能不能加个确认？有时候手滑点错了就找不回来了。"

**Round 4** (excited feature requests):
> "我觉得还可以更好用一点！想加几个新功能。能不能加个搜索功能？任务多了以后找起来不方便。然后能不能给任务分个类或者加个标签？比如工作、生活、学习之类的。还有能不能加一个拖拽排序的功能？想把重要的任务拖到最上面。"

**Round 5** (bug reports after testing):
> "我试了一下有几个小问题想修一下。那个搜索好像中文输入法的时候会搜到一半就触发了，用拼音的过程中就出结果了。然后拖拽排序在手机上好像不太好用，拖不动。还有那个标签删除之后再添加同名标签会报错。这几个能不能帮我修一下？"

## Step 4: Docker & CI Configuration

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

## Step 5: Documentation Generation

After all iteration rounds are complete and merged, **automatically generate documentation files** and commit them to GitHub. This step is mandatory and should not be skipped.

### Required Documentation Files

| File | Content |
|------|---------|
| `docs/frontend.md` | Frontend architecture, page structure, component descriptions, data flow, state management, event handling |
| `docs/backend.md` | Backend API endpoints (method, path, params, response), data models, server configuration, error handling |
| `docs/admin-frontend.md` | Admin panel documentation (if applicable — skip if project has no admin frontend) |
| `docs/deployment.md` | How to install dependencies, configure, and run the project |

### Documentation Standards

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
   - Prerequisites (Node.js version, Python version, etc.)
   - Installation steps
   - Configuration
   - Running the server

### Workflow

1. Create `docs/` directory in the project root
2. Generate each documentation file based on the actual codebase
3. Commit with: `docs: 添加项目文档 - 前端/后端/部署说明`
4. Push to master

## Step 6: Finalization

1. **Update README**: Update `README.md` with full feature list and 5-round iteration table.
2. **Push collab log**: Write `collab-log.md` with full iteration records and push to master.
3. **Show summary**: Display git log, PR list, repo URL.
4. **Security note**: If user provided a GitHub token in chat, remind them to revoke and regenerate it.

## PR Title and Commit Message Convention

- **Round 1**: `feat: 初始版本 - <description>`
- **Round 2**: `refactor: 代码质量优化 (第2轮)`
- **Round 3**: `feat: 用户体验优化 (第3轮)`
- **Round 4**: `feat: 功能增强 (第4轮)`
- **Round 5**: `fix: Bug修复 (第5轮)`
- **Final**: `docs: 添加协作开发日志 - 完整迭代记录与模糊化反馈`

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
- If code output is truncated: request remaining parts using `continue_agent_task`
- If generator times out: retry with a shorter/simpler message, or fix trivial issues directly in main session

## Multi-file Projects

For projects with multiple files (web apps, APIs, etc.):

1. Tell the generator the file structure upfront
2. Request code file by file if needed (to avoid truncation)
3. Each file is written separately to the project directory
4. Git add all changed files per round

Common structures:
- **Frontend (vanilla)**: `index.html`, `style.css`, `script.js`
- **Frontend (React)**: standard create-react-app or Vite structure
- **Backend (Python)**: `app.py`, `requirements.txt`, templates dir
- **Full-stack**: combine above in appropriate structure
- **CLI tool**: single Python/Node file

## Fuzzification Examples by Domain

### Web Frontend
| Technical | Fuzzified |
|---|---|
| 添加 CSS transition 动画 | "那个切换有点生硬，能不能平滑一点？" |
| localStorage 存储状态 | "刷新之后数据就没了，能不能保存住？" |
| 响应式设计 media query | "手机上看排版有点乱" |
| 表单验证 required + pattern | "那个输入框什么都能填" |
| 无障碍 aria-label | "屏幕阅读器好像读不出来" |

### Backend API
| Technical | Fuzzified |
|---|---|
| 添加分页参数 | "数据太多了一次性加载好慢" |
| JWT token 认证 | "能不能加个登录功能？" |
| 错误响应统一格式 | "报错的时候提示乱七八糟的" |
| 添加日志记录 | "出问题了不知道哪里出错" |
| 数据库连接池 | "人多了就卡住了" |

### Chat / Real-time
| Technical | Fuzzified |
|---|---|
| WebSocket 消息推送 | "消息要刷新才能看到新的" |
| 消息去重 dedup | "同一条消息出现了两次" |
| 断线重连 reconnect | "网络断了一下就再也收不到消息了" |
| 消息队列 buffer | "消息太多的时候页面会卡" |
