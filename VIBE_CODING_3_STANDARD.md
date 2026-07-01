# Vibe Coding 3.0：基于上下文工程、验证门禁与文件系统外脑的 Agentic Development 范式

> 状态：工作草案  
> 日期：2026-07-01  
> 主题：Vibe Coding 开发新范式、Context Engineering（上下文工程）、Agentic Development（智能体式开发）、Skill 化落地  
> 目标：把当前关于 Vibe Coding 2.0 是否落后、如何升级、是否写成 Skill、方案 B/C 边界等所有记录与思考沉淀为一个统一文档。

---

## 0. 核心结论

原始的 **Vibe Coding 2.0** 没有落后，它的主干仍然成立：

```text
清晰 PRD + 文件系统外脑 + AI 自主规划 + 观测遮蔽 + 追加式记忆
```

但截至 2026-07-01，它已经不够完整。它更像是一个“个人 AI 编程工作流”，还没有升级为一个可验证、可审计、可恢复、可并行协作的工程体系。

新的方向应该是：

```text
Vibe Coding 3.0
= Spec-first Development（规范优先开发）
+ Filesystem Context OS（文件系统上下文操作系统）
+ Verification Gates（验证门禁）
+ Agent Isolation（智能体隔离）
+ Context Budget Discipline（上下文预算纪律）
+ Telemetry-driven Improvement（遥测驱动优化）
```

一句话：

```text
Vibe Coding 2.0 解决的是“AI 如何不忘”。
Vibe Coding 3.0 解决的是“AI 如何可靠交付”。
```

---

## 1. 原始 Vibe Coding 2.0 的有效部分

### 1.1 `.context/` 与 `docs/` 生命周期分离是正确的

原始设计中：

```text
docs/       = 低频静态区，人类设计区
.context/   = 高频动态区，AI 工作区
```

这个判断仍然正确。

更准确地说：

```text
docs/      = stable human-facing design context（稳定的人类设计上下文）
.context/  = dynamic AI working memory（动态 AI 工作记忆）
```

这符合 2026 年 Context Engineering（上下文工程）的核心思想：不要把所有信息都塞进上下文窗口，而是让模型通过文件系统按需读取。

---

### 1.2 Progressive Disclosure（渐进式加载）仍然正确

原始设计要求 AI 先读：

```text
docs/architecture/INDEX.md
```

再根据任务读取相关子文档。这个方向仍然正确。

但建议升级为更明确的 **Read Contract（读取契约）**：

```markdown
## Read Contract

### Always Read
- `CLAUDE.md`
- `docs/PRD.md`
- `.context/plan.md`
- `.context/state.json` if exists

### Read By Task Type
- Auth task → `docs/requirements/auth.md` + `docs/architecture/security.md`
- DB task → `docs/architecture/database.md` + relevant ADRs
- UI task → `docs/architecture/frontend.md` + screenshots
- Deployment task → `docs/architecture/deployment.md`

### Do Not Read Unless Needed
- Full logs in `.context/scratchpads/`
- Historical agent transcripts
- Old metrics
```

这样可以从“建议读取”升级成“可执行的上下文路由规则”。

---

### 1.3 Observation Masking（观测遮蔽）仍然正确

原始设计将测试日志、构建日志、API 响应等长输出放入：

```text
.context/scratchpads/
```

这是正确的。长输出如果直接进入对话，会污染上下文窗口，导致 Lost-in-Middle（中间遗忘）和注意力稀释。

但建议补充 **summary sidecar（摘要旁车文件）**：

```text
.context/scratchpads/
├── test-2026-07-01-1430-auth.log
└── test-2026-07-01-1430-auth.summary.md
```

摘要示例：

```markdown
# Test Summary: Auth

## Command
`npm test -- auth`

## Result
FAILED

## Key Signal
- 19 passed
- 2 failed

## Failed Cases
1. `auth.test.ts:42` — JWT expiry validation failed
2. `auth.test.ts:67` — refresh token blacklist not applied

## Suspected Root Cause
Redis mock does not persist blacklist across test cases.

## Next Action
Fix Redis test fixture, then rerun auth test only.
```

AI 以后恢复上下文时，只读 `.summary.md`，不读完整日志。

---

### 1.4 Append-only Memory（追加式记忆）方向正确

`.context/memory.jsonl` 适合保存跨会话重要信息。

但它不应该变成“压缩后的聊天记录”。需要明确分层：

```text
.context/memory.jsonl        # 动态项目记忆
docs/decisions/              # 稳定架构决策
docs/gotchas.md              # 已知坑
docs/runbooks/               # 可重复操作手册
```

建议规则：

| 信息类型 | 放哪里 |
|---|---|
| 临时进度 | `.context/plan.md` |
| 当前状态 | `.context/state.json` |
| 一次命令输出 | `.context/scratchpads/` |
| 跨会话技术记忆 | `.context/memory.jsonl` |
| 架构选择原因 | `docs/decisions/ADR-xxx.md` |
| 可重复操作步骤 | `docs/runbooks/*.md` |
| 踩坑经验 | `docs/gotchas.md` 或 Skill |

---

## 2. Vibe Coding 2.0 的不足

### 2.1 过度依赖 `plan.md`，缺少机器可读状态

`plan.md` 适合人类和 AI 阅读，但不适合自动化恢复。

建议增加：

```text
.context/state.json
```

示例：

```json
{
  "current_goal": "implement JWT authentication",
  "phase": "implementation",
  "active_task": "auth-login-api",
  "blocked": false,
  "last_verified_at": "2026-07-01T14:30:00+08:00",
  "last_green_command": "npm test -- auth",
  "dirty_files": [
    "src/auth/login.ts",
    "tests/auth/login.test.ts"
  ],
  "next_action": "implement refresh token blacklist"
}
```

`plan.md` 负责解释，`state.json` 负责恢复。

---

### 2.2 缺少 Verification Loop（验证闭环）

这是 Vibe Coding 2.0 最大短板。

2026 年 Agentic Coding（智能体式编码）的关键原则之一：

> 不要只告诉 AI 做什么，要给 AI 一个它能自己运行的 pass/fail 检查。

每个任务应该有：

```markdown
## Verification Contract

### Required Commands
- `npm test -- auth`
- `npm run lint`
- `npm run typecheck`

### Success Criteria
- All auth tests pass
- No type errors
- Login API returns access token + refresh token
- Expired token returns 401
```

验证结果追加到：

```text
.context/verification.jsonl
```

示例：

```jsonl
{"time":"2026-07-01T14:30:00+08:00","command":"npm test -- auth","status":"failed","summary":"19 passed, 2 failed","details":".context/scratchpads/test-2026-07-01-1430-auth.log"}
{"time":"2026-07-01T15:10:00+08:00","command":"npm test -- auth","status":"passed","summary":"21 passed","details":".context/scratchpads/test-2026-07-01-1510-auth.log"}
```

---

### 2.3 缺少 Gates（门禁）

Vibe Coding 2.0 的流程基本是：

```text
PRD → plan → implement → test
```

建议升级为：

```text
Pre-flight Gate → Plan Gate → Implementation Gate → Verification Gate → Review Gate → Commit Gate
```

推荐门禁模型：

| Gate | 中文 | 用途 | 失败时 |
|---|---|---|---|
| Pre-flight Gate | 前置门禁 | 检查 PRD、环境、依赖、分支状态 | 停止，补齐前置条件 |
| Plan Gate | 计划门禁 | 检查 plan 是否覆盖验收标准 | 修订 plan |
| Implementation Gate | 实现门禁 | 检查是否按任务改动 | 修复实现 |
| Verification Gate | 验证门禁 | 跑测试、lint、build | 继续修复 |
| Review Gate | 审查门禁 | fresh agent/code review | 修订 |
| Commit Gate | 提交门禁 | git diff、测试全绿、记录 ADR | commit |

---

### 2.4 多 Agent 协作机制不足

原始 `.context/agents/` 只有雏形。建议明确角色：

```text
orchestrator      # 主控 agent，负责计划与门禁
implementer       # 实现 agent
verifier          # 验证 agent，专门跑测试和复现
reviewer-spec     # 规格审查 agent
reviewer-quality  # 质量审查 agent
researcher        # 调研 agent
documenter        # 文档 agent
```

关键原则：

```text
实现者不能审查自己。
```

推荐流程：

```text
Implementer → Spec Reviewer → Quality Reviewer → Verifier
```

---

### 2.5 缺少 Context Budget Discipline（上下文预算纪律）

Vibe Coding 2.0 提到了 Lost-in-Middle，但没有具体执行规则。

建议使用四档上下文健康状态：

| 状态 | 上下文使用 | 行为 |
|---|---:|---|
| PEAK | 0-30% | 正常探索 |
| GOOD | 30-50% | 减少大文件读取 |
| DEGRADING | 50-70% | 只读摘要，主动 checkpoint |
| POOR | 70%+ | 停止新任务，写 checkpoint，重开会话 |

加入：

```text
.context/checkpoints/
```

示例：

```text
.context/checkpoints/checkpoint-2026-07-01-1530.md
```

内容：

```markdown
# Context Checkpoint

## Current Goal
Implement JWT authentication.

## Completed
- User model
- Password hashing
- Login API validation

## Current State
- Login API token signing in progress
- Refresh token blacklist not implemented

## Last Green
`npm test -- auth:password` passed

## Next Action
Implement `createAccessToken()` and `createRefreshToken()`

## Important Files
- `src/auth/token.ts`
- `tests/auth/token.test.ts`
- `docs/requirements/auth.md`
```

---

### 2.6 缺少 ADR（Architecture Decision Record，架构决策记录）

重大决策不应该只写进 `.context/memory.jsonl`。

应该写入：

```text
docs/decisions/ADR-001-use-jwt-refresh-token.md
```

示例：

```markdown
# ADR-001: Use JWT access token and Redis-backed refresh token blacklist

## Status
Accepted

## Date
2026-07-01

## Context
We need stateless authentication for API calls while supporting logout and token revocation.

## Decision
Use short-lived JWT access tokens and Redis-backed refresh token blacklist.

## Alternatives Considered

### Server-side sessions
Pros:
- Easy revocation
Cons:
- Requires centralized session store for all requests

### Long-lived JWT only
Pros:
- Simple
Cons:
- Cannot revoke safely after logout

## Consequences
- Redis becomes required for auth flows
- Tests must include Redis mock or test container
- Token expiry must be covered by unit tests
```

`.context/memory.jsonl` 适合提醒 AI，ADR 适合让项目长期可理解。

---

## 3. 推荐方案：Vibe Coding 3.0 Project Standard

### 3.1 推荐目录结构

```text
project/
├── CLAUDE.md
├── AGENTS.md                         # 可选：多 agent 行为规则
│
├── docs/
│   ├── PRD.md                        # 产品目标、用户故事、范围边界
│   ├── acceptance.md                 # 验收标准，必须可测试
│   ├── glossary.md                   # 术语表
│   │
│   ├── requirements/
│   │   ├── auth.md
│   │   ├── payment.md
│   │   └── notification.md
│   │
│   ├── architecture/
│   │   ├── INDEX.md                  # 架构地图，渐进式加载入口
│   │   ├── backend.md
│   │   ├── frontend.md
│   │   ├── database.md
│   │   ├── security.md
│   │   └── deployment.md
│   │
│   ├── decisions/                    # ADRs
│   │   ├── ADR-001-use-postgres.md
│   │   └── ADR-002-use-redis-session.md
│   │
│   ├── runbooks/                     # 可重复操作步骤
│   │   ├── local-dev.md
│   │   ├── release.md
│   │   └── incident-debugging.md
│   │
│   └── gotchas.md                    # 已知坑
│
├── .context/
│   ├── plan.md                       # 人类/AI 可读计划
│   ├── state.json                    # 机器可读当前状态
│   ├── memory.jsonl                  # 追加式动态记忆
│   ├── verification.jsonl            # 测试/构建/验证记录
│   ├── metrics.jsonl                 # token、耗时、失败率、迭代次数
│   │
│   ├── checkpoints/
│   │   └── checkpoint-2026-07-01-1530.md
│   │
│   ├── scratchpads/
│   │   ├── test-2026-07-01-1430-auth.log
│   │   └── test-2026-07-01-1430-auth.summary.md
│   │
│   └── agents/
│       ├── orchestrator.md
│       ├── implementer.md
│       ├── verifier.md
│       ├── reviewer-spec.md
│       ├── reviewer-quality.md
│       └── handoffs/
│           └── auth-api-contract.json
│
└── scripts/
    ├── verify.sh                     # 本地验证入口
    ├── summarize-log.py              # 日志摘要生成
    └── clean-scratchpads.sh          # 清理旧日志
```

小项目可以简化为：

```text
project/
├── CLAUDE.md
├── docs/
│   └── PRD.md
└── .context/
    ├── plan.md
    └── scratchpads/
```

---

## 4. 推荐新版 `CLAUDE.md` 模板

```markdown
# AI Vibe Coding 3.0 Rules

你是一个高级 AI 工程师，负责在本项目中执行 Spec-first、Verification-gated、Context-disciplined 的 AI 开发流程。

核心原则：

1. 先理解边界，再写代码。
2. 计划必须持久化。
3. 长输出必须遮蔽。
4. 每个实现必须有可运行验证。
5. 重大决策必须写 ADR。
6. 上下文快满时必须 checkpoint。
7. 实现者不能审查自己。

---

## 1. Context Loading Rules

### Always Read First

开始复杂任务前，读取：

- `docs/PRD.md`
- `docs/acceptance.md` if exists
- `docs/architecture/INDEX.md` if exists
- `.context/plan.md` if exists
- `.context/state.json` if exists
- 最近 10 条 `.context/memory.jsonl` if exists

### Progressive Disclosure

只读取当前任务强相关文档。

Examples:

- Auth task → `docs/requirements/auth.md`, `docs/architecture/security.md`
- Database task → `docs/architecture/database.md`, relevant ADRs
- Frontend task → `docs/architecture/frontend.md`
- Deployment task → `docs/architecture/deployment.md`

不要一次性读取整个 `docs/`。

---

## 2. Planning Rules

复杂任务必须维护 `.context/plan.md`。

`plan.md` 必须包含：

- Current Goal
- Acceptance Criteria
- Task List
- Current Task
- Blockers
- Technical Decisions
- Verification Commands
- Next Action

任务状态使用：

- ✅ Done
- 🚧 In Progress
- ⏳ Pending
- ⛔ Blocked

每完成一个逻辑模块，更新 `.context/plan.md`。

---

## 3. Machine-readable State

复杂任务必须维护 `.context/state.json`。

Example:

```json
{
  "current_goal": "implement authentication",
  "phase": "implementation",
  "active_task": "login-api",
  "blocked": false,
  "last_green_command": "npm test -- auth",
  "next_action": "implement refresh token blacklist"
}
```

`plan.md` 面向人类和 AI，`state.json` 面向恢复和自动化。

---

## 4. Verification-gated Development

每个代码任务必须有 Verification Contract。

Example:

```markdown
## Verification Contract

### Commands
- `npm test -- auth`
- `npm run typecheck`
- `npm run lint`

### Success Criteria
- All auth tests pass
- No type errors
- Login returns access token and refresh token
- Expired token returns 401
```

不要在未验证时声称完成。

验证结果追加到 `.context/verification.jsonl`：

```json
{"time":"2026-07-01T14:30:00+08:00","command":"npm test -- auth","status":"passed","summary":"21 passed","details":".context/scratchpads/test-2026-07-01-1430-auth.log"}
```

---

## 5. Observation Masking

超过 50 行的命令输出必须写入 `.context/scratchpads/`。

命名格式：

```text
type-YYYY-MM-DD-HHMM-topic.ext
```

Examples:

```text
test-2026-07-01-1430-auth.log
build-2026-07-01-1500-web.log
api-2026-07-01-1510-payment-response.json
```

每个长日志必须生成摘要文件：

```text
test-2026-07-01-1430-auth.summary.md
```

对话中只返回：

- command
- status
- short summary
- failed cases
- details file path

---

## 6. Memory Rules

`.context/memory.jsonl` 只记录跨会话有价值的信息。

允许记录：

- decision
- bugfix
- config
- gotcha
- performance
- dependency

格式：

```json
{"date":"2026-07-01","type":"decision","tags":["#auth","#redis"],"summary":"Use Redis-backed refresh token blacklist for logout support","files":["src/auth/token.ts","docs/decisions/ADR-002-use-redis-refresh-blacklist.md"]}
```

不要记录：

- 普通进度
- 临时 todo
- 大段日志
- 已解决但无复用价值的小问题

重大架构决策必须写入 `docs/decisions/ADR-xxx.md`，不能只放在 memory。

---

## 7. Gate Model

复杂任务必须经过以下 gates：

### Pre-flight Gate

开始前检查：

- PRD exists
- acceptance criteria exists or can be inferred
- git status known
- dependencies installable
- verification commands known

失败：停止并补齐前置条件。

### Plan Gate

实现前检查：

- plan covers acceptance criteria
- task breakdown is clear
- verification commands exist

失败：修订 plan。

### Implementation Gate

实现时检查：

- only touch relevant files
- no scope creep
- update tests with code

失败：修正实现。

### Verification Gate

结束前必须运行验证命令。

失败：继续修复，不得声称完成。

### Review Gate

重要改动必须由 fresh reviewer 或第二 agent 审查。

审查顺序：

1. Spec compliance review
2. Code quality review

### Commit Gate

提交前检查：

- tests pass
- diff reviewed
- ADR updated if needed
- memory updated if needed
- no large scratchpad files accidentally committed

---

## 8. Multi-agent Rules

如果使用多个 agent：

- Orchestrator owns plan and gates.
- Implementer writes code.
- Verifier runs tests and reproduces bugs.
- Spec reviewer checks requirement compliance.
- Quality reviewer checks maintainability, security, and edge cases.

实现者不能审查自己。

Agent 之间通过 `.context/agents/handoffs/` 交接文件，不通过口头转述。

---

## 9. Context Budget Discipline

上下文使用分四档：

| Tier | Usage | Behavior |
|---|---:|---|
| PEAK | 0-30% | normal exploration |
| GOOD | 30-50% | prefer summaries |
| DEGRADING | 50-70% | checkpoint soon |
| POOR | 70%+ | stop new work, write checkpoint |

当上下文变重时，写入：

```text
.context/checkpoints/checkpoint-YYYY-MM-DD-HHMM.md
```

checkpoint 必须包含：

- current goal
- completed work
- current state
- last green command
- important files
- next action

---

## 10. Telemetry

每个开发 session 可追加 `.context/metrics.jsonl`：

```json
{"session":"2026-07-01-auth","tasks_completed":3,"verification_runs":8,"failed_runs":5,"scratchpad_files":6,"review_cycles":2}
```

用 metrics 评估：

- 哪些任务最容易失败
- 哪类日志最多
- review cycles 是否过多
- token 使用是否下降
- 测试修复速度是否提升

---

## 11. Cleanup

Bug 解决后：

- 保留 summary
- 删除无价值的大日志
- 重大经验写入 memory 或 docs/gotchas.md
- 重大决策写 ADR
```

---

## 5. 推荐 `.context/plan.md` 模板

```markdown
# Context Plan

## Current Goal

实现用户认证功能：注册、登录、JWT access token、refresh token、Redis blacklist、登出。

## Acceptance Criteria

- [ ] 用户可以注册
- [ ] 用户可以登录
- [ ] 登录返回 access token + refresh token
- [ ] access token 15 分钟过期
- [ ] refresh token 7 天过期
- [ ] 登出后 refresh token 进入 Redis blacklist
- [ ] 过期 token 返回 401
- [ ] 单元测试覆盖率 >80%

## Current Phase

Implementation

## Task List

### ✅ Done

- [x] Define User model
- [x] Implement password hashing

### 🚧 In Progress

- [ ] Implement login API
  - Status: request validation done
  - Next: JWT signing
  - Verification: `npm test -- auth/login`

### ⏳ Pending

- [ ] Implement refresh token flow
- [ ] Implement logout blacklist
- [ ] Add auth middleware
- [ ] Add integration tests

### ⛔ Blocked

None

## Verification Contract

### Commands

- `npm test -- auth`
- `npm run typecheck`
- `npm run lint`

### Last Green

None yet

## Technical Decisions

- JWT secret from `JWT_SECRET`
- Access token expiry: 15m
- Refresh token expiry: 7d
- Redis stores refresh token blacklist

## Relevant Files

- `src/auth/login.ts`
- `src/auth/token.ts`
- `src/middleware/auth.ts`
- `tests/auth/login.test.ts`

## Next Action

Implement `signAccessToken()` and `signRefreshToken()`.
```

---

## 6. 推荐 `.context/state.json` 模板

```json
{
  "schema_version": "1.0",
  "current_goal": "implement user authentication",
  "phase": "implementation",
  "active_task": "login-api-token-signing",
  "blocked": false,
  "blocker": null,
  "last_green_command": null,
  "last_failed_command": "npm test -- auth/login",
  "last_verification_file": ".context/scratchpads/test-2026-07-01-1430-auth.summary.md",
  "next_action": "implement signAccessToken and signRefreshToken",
  "important_files": [
    "src/auth/login.ts",
    "src/auth/token.ts",
    "tests/auth/login.test.ts"
  ],
  "updated_at": "2026-07-01T14:30:00+08:00"
}
```

---

## 7. 推荐 `.context/memory.jsonl` 规范

建议字段：

```jsonl
{"date":"2026-07-01","type":"decision","scope":"project","confidence":0.9,"tags":["#auth","#jwt"],"summary":"Use short-lived JWT access token and Redis-backed refresh token blacklist","files":["docs/decisions/ADR-002-auth-token-strategy.md","src/auth/token.ts"]}
{"date":"2026-07-01","type":"gotcha","scope":"test","confidence":0.8,"tags":["#redis","#test"],"summary":"Redis mock must persist blacklist across test cases or logout tests produce false positives","files":["tests/fixtures/redis.ts"]}
```

字段说明：

| 字段 | 用途 |
|---|---|
| `date` | 日期 |
| `type` | decision / bugfix / config / gotcha / performance / dependency |
| `scope` | project / module / test / deployment |
| `confidence` | 0-1，避免把猜测当事实 |
| `tags` | grep 检索 |
| `summary` | 简短事实 |
| `files` | 相关文件 |

---

## 8. 推荐 scratchpad 规范

长日志与摘要必须成对出现：

```text
.context/scratchpads/
├── test-2026-07-01-1430-auth.log
├── test-2026-07-01-1430-auth.summary.md
├── build-2026-07-01-1500-web.log
└── build-2026-07-01-1500-web.summary.md
```

摘要模板：

```markdown
# Scratchpad Summary

## Type
test

## Command
`npm test -- auth`

## Status
failed

## Key Output
- 19 passed
- 2 failed

## Failure Points
1. `auth.test.ts:42` — expected 401, got 200
2. `auth.test.ts:67` — refresh token was not blacklisted

## Likely Cause
Logout handler does not write refresh token jti to Redis.

## Next Step
Implement blacklist write in `src/auth/logout.ts`.

## Full Log
`.context/scratchpads/test-2026-07-01-1430-auth.log`
```

---

## 9. 人类与 AI 的新角色分工

原始表述：

```text
人类从“微观包工头”变成“产品经理 + 架构师”
```

建议升级为：

```text
人类 = Product Boundary Owner + Taste Owner + Risk Owner
AI = Planner + Implementer + Verifier + Documenter
```

中文：

```text
人类 = 产品边界负责人 + 品味负责人 + 风险负责人
AI = 计划者 + 实现者 + 验证者 + 文档维护者
```

人类重点提供：

1. 边界：什么不做
2. 验收：怎么证明做完
3. 品味：什么方案更优雅
4. 风险：哪些地方不能错
5. 取舍：性能、成本、时间、复杂度之间怎么选

AI 负责：

1. 代码探索
2. 实施计划
3. 编码实现
4. 测试验证
5. 文档更新
6. 状态维护

---

## 10. 方案 B 与方案 C 的边界

这是当前讨论中最重要的澄清。

---

### 10.1 方案 B：工程化 Agent OS

方案 B 是 **在单个项目内部使用的工作方式**。

它回答的问题是：

> 一个项目内部应该怎么组织 AI 开发上下文？

方案 B 的内容包括：

```text
project/
├── CLAUDE.md
├── docs/
│   ├── PRD.md
│   ├── acceptance.md
│   ├── architecture/
│   ├── decisions/
│   ├── runbooks/
│   └── gotchas.md
│
└── .context/
    ├── plan.md
    ├── state.json
    ├── memory.jsonl
    ├── verification.jsonl
    ├── metrics.jsonl
    ├── scratchpads/
    ├── checkpoints/
    └── agents/
```

以下内容属于方案 B：

- `.context/plan.md`
- `.context/state.json`
- `.context/memory.jsonl`
- `.context/verification.jsonl`
- `.context/metrics.jsonl`
- `.context/scratchpads/`
- `.context/checkpoints/`
- `.context/agents/`
- `docs/acceptance.md`
- `docs/decisions/ADR-xxx.md`
- `docs/runbooks/`
- `docs/gotchas.md`
- gates（门禁）
- verification contract（验证契约）
- context budget discipline（上下文预算纪律）
- multi-agent handoff（多 agent 交接）

一句话：

```text
方案 B = Vibe Coding 作为“项目内开发规范”
```

或者：

```text
方案 B 是操作系统。
```

---

### 10.2 方案 C：把方案 B 封装成可复用 Skill

方案 C 是 **跨项目复用的方式**。

它回答的问题是：

> 我不想每个项目重新复制粘贴这套方法，能不能让 Hermes / Claude / Codex 自动知道怎么初始化和执行？

方案 C 的内容包括：

```text
skills/vibe-coding/
├── SKILL.md
├── templates/
├── references/
└── scripts/
```

以下内容属于方案 C：

- `skills/vibe-coding/SKILL.md`
- `templates/CLAUDE.md.template`
- `templates/plan.md.template`
- `templates/state.json.template`
- `templates/ADR.md.template`
- `references/gates.md`
- `references/context-budget.md`
- `references/memory-policy.md`
- `scripts/init-vibe-project.py`
- `scripts/summarize-scratchpad.py`
- `scripts/clean-scratchpads.py`

一句话：

```text
方案 C = Vibe Coding 作为“Hermes/Claude/Codex 可调用的 skill”
```

或者：

```text
方案 C 是安装器 + 使用手册 + 可复用封装。
```

---

### 10.3 上一轮内容分类

| 内容 | 属于 B 还是 C |
|---|---|
| 新版项目目录结构 `project/docs/.context` | B |
| `.context/plan.md` 模板 | B |
| `.context/state.json` 模板 | B |
| `.context/memory.jsonl` 规范 | B |
| `.context/verification.jsonl` | B |
| scratchpad summary 机制 | B |
| gates 机制 | B |
| 多 agent 角色划分 | B |
| context checkpoint | B |
| telemetry 机制 | B |
| `CLAUDE.md` 项目模板 | B，也可以被 C 收进 templates |
| `skills/vibe-coding/` 目录 | C |
| `SKILL.md` frontmatter | C |
| `templates/`、`references/`、`scripts/` 包结构 | C |
| 初始化脚本 `init-vibe-project.py` | C |
| 把方法论跨项目复用 | C |

总结：

```text
B = 这套方法在一个项目里怎么运转
C = 把这套方法打包成 skill，方便所有项目复用
```

---

## 11. 是否应该写成 Skill？

结论：

```text
应该，但不要把所有内容都塞进 SKILL.md。
```

更准确地说：

```text
Vibe Coding 应该做成一个 workflow skill（工作流技能）
+ project scaffold（项目脚手架）
+ templates（模板）
+ references（细则）
+ optional scripts（可选脚本）
```

---

### 11.1 为什么适合写成 Skill

一个方法适合写成 Skill，通常满足以下条件：

| 条件 | Vibe Coding 是否满足 |
|---|---|
| 会重复使用 | 是，多项目都会用 |
| 容易被错误路由 | 是，容易和普通计划、README、CLAUDE.md 混淆 |
| 需要明确边界 | 是，它不是写代码本身，而是 AI 开发操作系统 |
| 有可复用流程/checklist | 是，PRD、plan、scratchpad、memory、verification、ADR |
| 未来可能团队复用 | 是，适合团队标准化 |

因此它不是“一篇文档”，而是典型的 **Production-level Skill（生产级技能）**。

但第一版不要过重，建议从：

```text
Scaffold（脚手架型） → Production（生产型）
```

逐步升级。

---

### 11.2 Skill 不应该承担什么

Skill 不应该保存项目特定状态。

不要把这些放进 Skill：

- 某个项目的 PRD
- 某个项目的计划
- 某个项目的测试日志
- 某个项目的架构决策
- 某个项目的 `.context/memory.jsonl`

这些应该放在项目里。

Skill 只保存可复用方法。

---

## 12. Skill、CLAUDE.md、项目文件之间的关系

### 12.1 Skill 是跨项目方法论

```text
skills/vibe-coding/SKILL.md
```

回答：

> 当用户说“用 Vibe Coding 管理这个项目”时，AI 应该怎么做？

它是全局的、可复用的。

---

### 12.2 `CLAUDE.md` 是项目本地规则

```text
project/CLAUDE.md
```

回答：

> 在这个具体项目里，AI 应该遵守哪些规则？

它是项目专属的。

---

### 12.3 二者关系

```text
vibe-coding skill
    ↓ 生成/指导
project/CLAUDE.md
    ↓ 约束
具体项目里的 AI 开发行为
```

也就是：

```text
Skill = 生成规则的规则
CLAUDE.md = 项目执行规则
```

---

### 12.4 内容归属表

| 内容 | 放哪 |
|---|---|
| Vibe Coding 方法论 | `skills/vibe-coding/SKILL.md` |
| 标准项目结构 | `skills/vibe-coding/references/project-structure.md` |
| CLAUDE.md 模板 | `skills/vibe-coding/templates/CLAUDE.md.template` |
| 当前项目规则 | `project/CLAUDE.md` |
| 当前项目 PRD | `project/docs/PRD.md` |
| 当前项目计划 | `project/.context/plan.md` |
| 当前项目状态 | `project/.context/state.json` |
| 当前项目日志 | `project/.context/scratchpads/` |
| 当前项目架构决策 | `project/docs/decisions/` |
| 初始化脚本 | `skills/vibe-coding/scripts/init-vibe-project.py` |
| 清理脚本 | `skills/vibe-coding/scripts/clean-scratchpads.py` |

一句话：

```text
可复用的放 skill。
项目特定的放 project。
机器生成的动态状态放 .context。
长期稳定设计放 docs。
```

---

## 13. 可参考的已有 Skill

### 13.1 `writing-plans`

适合参考：

- 如何把复杂任务拆成可执行计划
- 如何写 implementation plan（实施计划）
- 如何定义验证步骤
- 如何让执行者不需要猜

Vibe Coding 的 `.context/plan.md` 可以借鉴它。

---

### 13.2 `subagent-driven-development`

适合参考：

- 多 agent 协作
- implementer / reviewer 分离
- spec compliance review（规格符合性审查）
- code quality review（代码质量审查）
- gates taxonomy（门禁分类）
- context budget discipline（上下文预算纪律）

Vibe Coding 3.0 的 gates、多 agent、context budget 基本可以以它为参照。

---

### 13.3 `documentation-and-adrs`

适合参考：

- ADR（Architecture Decision Record，架构决策记录）怎么写
- 哪些决策需要文档化
- 文档应该记录 why，而不是只记录 what
- README、API 文档、gotchas 如何治理

Vibe Coding 的 `docs/decisions/`、`docs/runbooks/`、`docs/gotchas.md` 可以参考它。

---

### 13.4 `hermes-skill-operations`

适合参考：

- Hermes Skill 的安装、验证、linked files 如何组织
- `SKILL.md` + `references/` + `templates/` + `scripts/` 的包结构
- 如何验证 Skill 可加载

如果后续创建 `vibe-coding` Skill，这个是操作参考。

---

### 13.5 `yao-meta-skill`

适合参考：

- 如何从方法论抽象成 Skill
- Skill 该不该创建
- Skill 应该是 Scaffold / Production / Library / Governed 哪种级别
- 如何避免 Skill 膨胀

Vibe Coding 适合先做成 **Production Skill**，未来如果团队广泛使用，再升级成 **Library Skill**。

---

## 14. 推荐 Skill 目录结构

完整结构：

```text
skills/vibe-coding/
├── SKILL.md
├── templates/
│   ├── CLAUDE.md.template
│   ├── AGENTS.md.template
│   ├── plan.md.template
│   ├── state.json.template
│   ├── memory.jsonl.example
│   ├── verification.jsonl.example
│   ├── metrics.jsonl.example
│   ├── ADR.md.template
│   └── scratchpad-summary.md.template
│
├── references/
│   ├── project-structure.md
│   ├── context-loading.md
│   ├── gates.md
│   ├── context-budget.md
│   ├── memory-policy.md
│   ├── observation-masking.md
│   ├── multi-agent-handoff.md
│   ├── verification-contract.md
│   └── migration-guide-v2-to-v3.md
│
└── scripts/
    ├── init-vibe-project.py
    ├── summarize-scratchpad.py
    └── clean-scratchpads.py
```

第一版可以更轻：

```text
skills/vibe-coding/
├── SKILL.md
├── templates/
│   ├── CLAUDE.md.template
│   ├── plan.md.template
│   ├── state.json.template
│   └── ADR.md.template
└── references/
    ├── gates.md
    ├── context-budget.md
    └── project-structure.md
```

---

## 15. 第一版 `vibe-coding/SKILL.md` 草案

```markdown
---
name: vibe-coding
description: Use when initializing or operating an AI-assisted software project with filesystem-backed context, persistent planning, scratchpad log masking, verification gates, ADRs, and optional multi-agent development. Trigger when the user asks for Vibe Coding, AI coding workflow setup, context engineering for a code project, Claude/Codex project rules, or reusable agentic development conventions.
version: 0.1.0
metadata:
  tags:
    - vibe-coding
    - context-engineering
    - agentic-development
    - ai-coding
    - planning
    - verification
    - multi-agent
---

# Vibe Coding

## Purpose

This skill defines a reusable AI-assisted software development workflow based on:

- filesystem-backed context
- progressive disclosure
- persistent planning
- observation masking
- verification gates
- append-only project memory
- architecture decision records
- optional multi-agent isolation

Use it to initialize or operate projects where AI agents perform sustained coding work.

## When To Use

Use this skill when the user wants to:

- initialize a new AI-assisted coding project
- improve Claude Code / Codex / Cursor project rules
- prevent AI context loss during long development sessions
- create `.context/` working memory for a project
- design a repeatable Vibe Coding workflow
- set up PRD-driven, verification-gated development
- coordinate multiple coding agents

## When Not To Use

Do not use this skill for:

- one-line code edits
- simple Q&A about programming
- writing a standalone README only
- pure research with no coding workflow
- temporary experiments that do not need persistent project context

## Core Model

Vibe Coding separates stable human intent from dynamic AI working state.

```text
docs/      = stable human-facing design context
.context/  = dynamic AI working memory
scripts/   = deterministic helpers
```

The default formula is:

```text
Vibe Coding =
clear PRD
+ acceptance criteria
+ filesystem context
+ persistent plan
+ scratchpad masking
+ verification gates
+ decision records
+ context checkpoints
```

## Standard Project Structure

Create or maintain:

```text
project/
├── CLAUDE.md
├── docs/
│   ├── PRD.md
│   ├── acceptance.md
│   ├── requirements/
│   ├── architecture/
│   │   └── INDEX.md
│   ├── decisions/
│   ├── runbooks/
│   └── gotchas.md
│
└── .context/
    ├── plan.md
    ├── state.json
    ├── memory.jsonl
    ├── verification.jsonl
    ├── metrics.jsonl
    ├── scratchpads/
    ├── checkpoints/
    └── agents/
```

For small projects, only require:

```text
CLAUDE.md
docs/PRD.md
.context/plan.md
.context/scratchpads/
```

## Operating Procedure

### 1. Pre-flight

Before complex work:

1. Inspect project structure.
2. Read `CLAUDE.md`.
3. Read `docs/PRD.md`.
4. Read `docs/acceptance.md` if present.
5. Read `docs/architecture/INDEX.md` if present.
6. Read `.context/plan.md` and `.context/state.json` if present.
7. Check recent `.context/memory.jsonl` entries.

If key files are missing, create them from templates or ask only when the missing information changes the design.

### 2. Plan

Maintain `.context/plan.md` with:

- current goal
- acceptance criteria
- task list
- current task
- blockers
- verification commands
- technical decisions
- next action

Maintain `.context/state.json` for machine-readable recovery state.

### 3. Implement

Work in small slices.

For each task:

1. Identify relevant requirement and architecture files.
2. Add or update tests first when possible.
3. Implement minimal code.
4. Avoid unrelated file changes.
5. Update plan and state.

### 4. Mask Observations

If command output exceeds 50 lines:

1. Write full output to `.context/scratchpads/`.
2. Create a paired summary file.
3. Return only the summary and file path in the conversation.

Use timestamped names:

```text
test-YYYY-MM-DD-HHMM-topic.log
test-YYYY-MM-DD-HHMM-topic.summary.md
```

### 5. Verify

Every non-trivial implementation must have a verification contract.

Record verification events in `.context/verification.jsonl`.

Do not report completion unless the required checks pass or the blocker is explicitly reported.

### 6. Document Decisions

Use ADRs for significant decisions:

```text
docs/decisions/ADR-001-short-title.md
```

Use `.context/memory.jsonl` only for concise dynamic memory, gotchas, and cross-session facts.

### 7. Review

For important changes, use fresh review passes:

1. Spec compliance review
2. Code quality review

The implementer should not be the final reviewer.

### 8. Checkpoint

When context gets heavy or the task pauses, write:

```text
.context/checkpoints/checkpoint-YYYY-MM-DD-HHMM.md
```

Include:

- current goal
- completed work
- current state
- last green command
- important files
- next action

## Gates

Use these gates for complex work:

| Gate | Purpose |
|---|---|
| Pre-flight Gate | confirm required context and environment |
| Plan Gate | ensure plan covers acceptance criteria |
| Implementation Gate | prevent scope creep |
| Verification Gate | require tests/build/lint |
| Review Gate | require fresh review for important changes |
| Commit Gate | confirm diff, docs, ADRs, and tests before commit |

## Output Contract

When asked to initialize Vibe Coding, produce:

1. project directory structure
2. `CLAUDE.md`
3. `.context/plan.md`
4. `.context/state.json`
5. `.context/memory.jsonl`
6. `.context/verification.jsonl`
7. `docs/PRD.md`
8. `docs/acceptance.md`
9. `docs/architecture/INDEX.md`
10. optional ADR template

When asked to operate an existing project, update only the necessary files.

## References

Load linked references when needed:

- `references/project-structure.md`
- `references/gates.md`
- `references/context-budget.md`
- `references/memory-policy.md`
- `references/observation-masking.md`
- `references/multi-agent-handoff.md`
- `references/verification-contract.md`
```

---

## 16. 推荐推进路线

不要一上来就做完整方案 C。

推荐三步：

### Step 1：先定义方案 B 的标准项目结构

输出：

```text
Vibe Coding 3.0 Project Standard
```

内容：

- 核心理念
- 项目结构
- 文件职责
- gates
- memory 策略
- verification 策略
- 多 agent 策略

这是方案 B 的标准文档。

---

### Step 2：提取模板

从标准文档中提取：

```text
CLAUDE.md.template
plan.md.template
state.json.template
ADR.md.template
scratchpad-summary.md.template
```

这一步开始进入方案 C。

---

### Step 3：创建 Skill

创建：

```text
skills/vibe-coding/SKILL.md
```

第一版只负责：

- 判断何时启用
- 创建项目结构
- 复制模板
- 指导开发循环
- 指导验证和记录

不要一开始就写 scripts。等手工流程稳定后再自动化。

---

## 17. 原文建议调整点

### 17.1 弱化具体模型版本

原文提到：

```text
Claude 4.6 opus、gpt-5.3-codex
```

建议改成：

```text
在 2026 年，新一代 agentic coding models（智能体式编码模型）具备更强的自主规划、工具调用和长程执行能力。
```

不要让方法论绑定到具体模型版本。

---

### 17.2 “AI 自己维护状态”需要加约束

原文：

```text
AI 自己维护状态
```

建议改成：

```text
AI 自己维护状态，但状态必须可审计、可恢复、可验证。
```

否则 AI 会写出漂亮但不可信的 plan。

---

### 17.3 “Bug 解决后主动删除日志”要谨慎

建议改成：

```text
Bug 解决后删除 full log，但保留 summary 和 verification record。
```

否则会失去调试历史。

---

### 17.4 “零 schema”建议改成“轻 schema”

完全零 schema 早期舒服，但中后期容易混乱。

建议改成：

```text
轻 schema：文件系统负责组织，人类可读 Markdown 负责解释，JSONL 负责机器可读事件。
```

也就是：

```text
Markdown for reasoning
JSONL for events
Logs for raw observations
ADR for durable decisions
```

---

## 18. 最终定位

最清晰的定位：

```text
方案 B 是操作系统。
方案 C 是安装器 + 使用手册 + 可复用封装。
```

或者：

```text
方案 B = Vibe Coding 作为“项目内开发规范”
方案 C = Vibe Coding 作为“Hermes/Claude/Codex 可调用的 Skill”
```

因此推荐路径是：

```text
先把方案 B 定成标准，
再把标准封装成方案 C 的 Skill。
```

不要反过来。

如果先写 Skill，但方案 B 的规则还没稳定，Skill 会很快变成臃肿且难维护的“方法论垃圾桶”。

---

## 19. 最终推荐

当前最合理的下一步不是马上写一堆脚本，而是先沉淀一个稳定的：

```text
Vibe Coding 3.0 Project Standard
```

然后再从它提取：

```text
skills/vibe-coding/
├── SKILL.md
├── templates/
└── references/
```

最终目标：

```text
Vibe Coding 不是单篇文章。
它应该成为一个可复用的 AI 开发操作系统规范，
并最终被封装成 Skill。
```
