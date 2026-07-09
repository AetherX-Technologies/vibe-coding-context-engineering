# Codex Hook + Skill Governance Plan for Vibe Coding 3.0

> 状态：工作草案  
> 日期：2026-07-01  
> 目标：把 Vibe Coding 3.0 落到 Codex 可执行的 hook、skill、脚本门禁和联合审查流程上。  
> 结论：先做 B+，不要一开始做完整 C。

本文是设计与审查文档，不是未来的 `SKILL.md`。正式 skill 应只保留触发描述、核心流程和 reference 导航；本文件中的长解释、审查日志和风险表不应直接复制进 skill。

---

## 1. 核心判断

当前最合适的落地形态不是“只写一个 skill”，也不是马上封成完整 plugin，而是：

```text
B+ =
repo-scoped operating standard
+ workflow skill
+ Codex hooks
+ deterministic verification scripts
+ external review skills
```

原因：

- 方案 B 解决“一个项目里怎么可靠运转”。
- 方案 C 解决“怎么跨项目安装和分发”。
- Codex hook 可以做生命周期约束，但不能替代项目文档、skill、脚本和验收记录。
- Skill 可以教 Codex 怎么工作，但不能单独承担强制门禁。
- 强约束应尽量落在脚本和 hook 上，软流程落在 skill 和 `AGENTS.md` 上。

所以推荐顺序是：

```text
先把 B+ 稳定为项目标准
再把稳定部分抽成 repo/user skill
最后才封装为 plugin
```

---

## 2. 文件与职责边界

| 层 | 文件或目录 | 职责 | 是否项目特定 |
|---|---|---|---|
| 项目规则 | `AGENTS.md` | 持久项目约束、读取契约、验收要求、命令习惯 | 是 |
| Codex 配置 | `.codex/config.toml` | sandbox、approval、MCP、feature 开关、hooks inline 备选 | 是 |
| Codex hooks | `.codex/hooks.json` | 生命周期事件到脚本的绑定 | 是 |
| Hook 脚本 | `.codex/hooks/*.py` 或 `.codex/hooks/*.sh` | 机械检查、阻断、追加上下文、Stop continuation | 是 |
| 工作流 skill | `.agents/skills/vibe-coding-3/SKILL.md` | Vibe Coding 操作流程、触发边界、资源导航 | 可复用 |
| Skill references | `.agents/skills/vibe-coding-3/references/*.md` | gates、memory、context budget、hook policy 等细则 | 可复用 |
| 项目确定性脚本 | `scripts/vibe/*.py` 或 `scripts/vibe/*.sh` | hook 实际调用的验收、日志摘要、状态检查、secret 扫描 | 是，可按项目适配 |
| Skill 脚本 | `.agents/skills/vibe-coding-3/scripts/*.py` | 初始化、复制模板、生成项目 hook 和脚本 | 可复用 |
| 动态工作区 | `.context/` | plan、state、verification、scratchpads、checkpoints | 是 |
| 稳定文档 | `docs/` | PRD、acceptance、architecture、ADR、runbooks、gotchas | 是 |
| 分发包 | `plugins/vibe-coding/` 或独立仓库 | 稳定后封装 skills、hooks、MCP、模板 | 否，后续阶段 |

边界规则：

- 可复用方法放 skill。
- 当前项目事实放 `docs/` 和 `.context/`。
- 机器强制检查放 hook 和 scripts。
- 跨项目分发等稳定后再做 plugin。

---

## 3. Codex Hook 官方行为约束

Codex hook 必须按 Codex 官方事件模型实现，不能套用 Claude Code 的 hookify 文件格式。

### 3.1 发现位置

Codex 会在活动配置层附近发现 hooks：

- `~/.codex/hooks.json`
- `~/.codex/config.toml`
- `<repo>/.codex/hooks.json`
- `<repo>/.codex/config.toml`

已安装 plugin 也可以携带 hook。项目本地 hook 只有在项目 `.codex/` 层被信任后才会运行。

同一层同时存在 `hooks.json` 和 inline `[hooks]` 时会合并并警告。项目内优先只选一种，推荐：

```text
.codex/hooks.json
```

### 3.2 事件选择

本方案只使用第一阶段必要事件：

| 事件 | 用途 |
|---|---|
| `UserPromptSubmit` | 在用户请求进入模型前追加任务路由、读取契约、风险提醒 |
| `PreToolUse` | 在 Bash、apply_patch、MCP 工具执行前阻断高风险操作 |
| `PostToolUse` | 在工具执行后识别失败、追加开发上下文、要求继续修复 |
| `PreCompact` | 压缩前要求写入状态摘要或 checkpoint |
| `Stop` | 回答结束前检查验证门禁，必要时让 Codex 自动继续一轮 |

第二阶段再考虑：

- `SessionStart`：加载项目状态摘要。
- `SubagentStart` / `SubagentStop`：多 agent 审查时控制交接和继续条件。
- `PermissionRequest`：对需要审批的操作做 allow/deny 策略。

### 3.3 输入输出协议

每个 command hook 都会在 `stdin` 收到一个 JSON 对象，常见字段包括：

- `session_id`
- `transcript_path`
- `cwd`
- `hook_event_name`
- `model`

`PreToolUse` 和 `PostToolUse` 还会包含：

- `turn_id`
- `tool_name`
- `tool_use_id`
- `tool_input`
- `tool_response`，仅 `PostToolUse`

`Bash` 和 `apply_patch` 的主要输入在 `tool_input.command`。文件编辑通过 `apply_patch` 时，matcher 可以写 `apply_patch`、`Edit` 或 `Write`，但输入里的 `tool_name` 仍可能是 `apply_patch`。

输出约束：

- `PreToolUse` 可以返回 `permissionDecision: "deny"` 阻断工具调用，也可以用 exit code `2` 并向 `stderr` 写阻断原因。
- `PostToolUse` 的 block 不能撤销已经执行的工具副作用，只能替换工具结果并把反馈交还给模型继续处理。
- `UserPromptSubmit` 的 matcher 当前不会生效，所有配置都会触发；普通 stdout 会作为额外 developer context。
- `Stop` 退出 `0` 时必须输出 JSON；返回 `decision: "block"` 不是拒绝本轮，而是创建一条 continuation prompt 让 Codex 继续。
- `Stop` hook 必须检查 `stop_hook_active`，避免无限 continuation。
- `PreCompact` 可以用 `continue: false` 阻止压缩。

限制：

- Hook 不能拦截所有外部行为；对部分 shell、WebSearch 或非 shell 非 MCP 工具的覆盖并不完整。
- Hook 命令会并发运行；多个 hook 之间不能依赖执行顺序。
- 非托管 command hook 需要被用户审查和信任后才会运行。

### 3.4 Hook 脚本定位规则

官方建议 repo-local hook 从 git root 解析脚本路径，因为 Codex 可能从子目录启动。但 Vibe Coding 初始化阶段可能还不是 git 仓库，所以不能只依赖 `git rev-parse --show-toplevel`。

推荐所有项目 hook 使用“git root 优先，cwd fallback”的定位方式：

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
/usr/bin/python3 "$ROOT/.codex/hooks/pre_tool_use_policy.py"
```

在 `.codex/hooks.json` 里可写成：

```json
{
  "type": "command",
  "command": "sh -lc 'ROOT=\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)\"; /usr/bin/python3 \"$ROOT/.codex/hooks/pre_tool_use_policy.py\"'",
  "timeout": 30,
  "statusMessage": "Checking Bash command"
}
```

脚本内部也要读取 `stdin` JSON 里的 `cwd`，不要把当前进程目录、git root 和项目 root 混为一谈。

---

## 4. 推荐 Hook 策略

### 4.1 `UserPromptSubmit`: 任务路由

职责：

- 按 prompt 判断任务类型。
- 输出追加上下文，而不是默认阻断。
- 给模型提示该读哪些文件、该用哪些 skill、该跑哪些 gates。

建议行为：

| Prompt 信号 | 追加上下文 |
|---|---|
| “实现”、“修 bug”、“改代码” | 先读 `AGENTS.md`、`docs/PRD.md`、`.context/plan.md`，建立 Verification Contract |
| “设计”、“架构”、“取舍” | 检查是否需要 ADR；可使用 `ecc:council` 或 ADR skill |
| “hook”、“Codex 配置”、“skill” | 使用 `$openai-docs` 核对 Codex 官方行为 |
| “上线”、“提交”、“PR” | 使用 `ecc:verification-loop`、`ecc:security-review` |

只在 prompt 明显包含密钥、要求破坏性操作或绕过安全规则时阻断。

### 4.2 `PreToolUse: Bash`: 命令门禁

职责：

- 阻断高风险命令。
- 提醒或阻断未走项目命令约束的 shell 命令。
- 对 git destructive 操作要求用户明确授权。

第一阶段阻断：

- `rm -rf /`
- `git reset --hard`
- `git checkout -- .`
- `chmod 777`
- `curl ... | sh`
- 直接向 `.env`、key、token 文件写入秘密。

本仓库额外规则：

- 普通 shell 命令必须用 `rtk` 前缀。
- 调试 hook 本身时可允许 raw command，但必须在阻断原因里说明例外。

`rtk` 规则适用边界：

- 只约束 Codex 通过 `Bash` 工具发起的普通项目命令。
- 不约束 hook command 自身，因为 hook command 由 `.codex/hooks.json` 配置执行。
- 不约束 `apply_patch`、MCP 工具、Codex 内部工具或非 shell 工具。
- 允许 `rtk proxy <cmd>` 作为“保留原始输出但计入使用”的显式例外。
- 如果命令是 `sh -lc` 包装器，hook 应检查包装器内部的实际命令，而不是只看最外层 `sh`。

### 4.3 `PreToolUse: apply_patch`: 文件门禁

职责：

- 阻断 secrets 写入。
- 阻断对生成日志、scratchpad 原始输出、`.env` 的危险编辑。
- 对架构规则改动提醒补 ADR。

建议阻断：

- 新增 `sk-...`、`ghp_...`、`github_pat_...`、`AKIA...`
- 新增私钥块。
- 修改 `.env`、`.pem`、`.key` 等敏感文件，除非用户显式要求且文件在允许列表。

secret scan 要支持例外：

- 允许 `tests/fixtures/`、`docs/examples/` 中明显假的短 token，但必须匹配 allowlist 注释或文件级 allowlist。
- 不扫描 lock file、二进制文件、压缩包和大型生成文件。
- 对命中结果默认阻断；只有 allowlist 记录和示例标记同时存在时才降级为 warning。

建议追加上下文：

- 改 `AGENTS.md`、`.codex/hooks.json`、`.agents/skills/**/SKILL.md` 时，提醒运行对应审查 skill。
- 改 `docs/architecture/**` 或核心规则时，提醒检查 ADR。

### 4.4 `PostToolUse`: 失败反馈

职责：

- 识别 build/test/lint/typecheck 失败。
- 把失败摘要作为 additional context 返回给模型。
- 要求先修失败，不要继续扩大范围。
- 记录实际可用的项目验证命令，而不是假设所有项目都有同名脚本。

注意：

- `PostToolUse` 不能撤销已经发生的副作用。
- 对失败命令应记录到 `.context/verification.jsonl`，长输出写 `.context/scratchpads/` 并生成 `.summary.md`。

验证命令发现顺序：

1. 读取 `AGENTS.md` 中显式声明的验证命令。
2. 读取 `.context/plan.md` 的 Verification Contract。
3. 按项目文件推断：`package.json` scripts、`pyproject.toml`、`Cargo.toml`、`go.mod`、`Makefile`。
4. 如果仍不能确定，Stop hook 应要求 Codex 报告“无法验证，因为缺少可识别命令”，而不是假装通过。

### 4.5 `PreCompact`: 压缩前保存状态

职责：

- 检查 `.context/state.json` 和 `.context/plan.md` 是否存在。
- 如果基础状态缺失，返回 `continue: false`，要求先恢复基础状态。
- 如果基础状态存在，写入一个从 `.context/state.json` 和最新 verification
  记录派生的最小 auto checkpoint。

注意：

- `PreCompact` 不应该尝试替模型生成完整叙事 checkpoint；hook 脚本只能写机械派生的最小状态摘要。
- auto checkpoint 的事实来源只应是 `.context/state.json`、`.context/plan.md`
  指针和 `.context/verification.jsonl` 最新记录。
- 不能把不稳定 transcript 当作长期事实来源。

最低要求：

```text
.context/state.json
.context/plan.md
.context/checkpoints/checkpoint-YYYY-MM-DD-HHMM.md
```

### 4.6 `Stop`: 验收兜底

职责：

- 在 Codex 准备结束前检查当前任务是否满足验收门禁。
- 如果发现改了代码但没有验证记录，返回 continuation prompt。
- 如果已经处于 stop continuation 中，只提示一次，避免循环。
- 只接受和当前改动绑定的验证证据，不能用旧的 green run 充当本轮验收。

第一阶段检查：

- 工作区是否有代码改动。
- `.context/verification.jsonl` 是否有本轮相关记录。
- 上一次验证是否失败。
- 是否承诺“完成”但没有证据。
- 最近一次通过的验证是否晚于最后一次文件修改。
- 最近一次通过的验证是否覆盖当前 changed-files fingerprint。

验证记录必须包含足够字段让 hook 做 freshness 判断：

```json
{
  "time": "2026-07-01T16:40:00+08:00",
  "session_id": "codex-session-id",
  "turn_id": "codex-turn-id",
  "command": "npm test -- auth",
  "status": "passed",
  "changed_files": ["src/auth/token.ts", "tests/auth.test.ts"],
  "changed_files_fingerprint": "sha256:...",
  "summary": "21 passed",
  "details": ".context/scratchpads/test-2026-07-01-1640-auth.summary.md"
}
```

`changed_files_fingerprint` 推荐由“文件路径 + 文件内容 hash + git diff hash（如果有 git）”生成。非 git workspace 使用文件 mtime 和内容 hash。Stop hook 只接受当前 fingerprint 匹配的 passed 记录。

Stop hook 的 block 应该让 Codex继续：

```json
{
  "decision": "block",
  "reason": "Run the missing verification gate before finalizing. If verification cannot run, report the concrete blocker."
}
```

---

## 5. Workflow Skill 设计

推荐创建：

```text
.agents/skills/vibe-coding-3/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── codex-hooks.md
│   ├── gates.md
│   ├── context-budget.md
│   ├── memory-policy.md
│   ├── observation-masking.md
│   └── adr-policy.md
└── scripts/
    ├── init_vibe_project.py
    ├── generate_project_hooks.py
    └── install_project_scripts.py
```

`SKILL.md` 只放核心流程和导航，不放长篇方法论。

Frontmatter 只保留 Codex 必需字段：

```markdown
---
name: vibe-coding-3
description: Initialize or operate an AI-assisted coding project with filesystem-backed context, Codex hooks, verification gates, scratchpad log masking, ADR capture, and context-budget discipline. Use when setting up Vibe Coding, Codex project rules, AI coding workflows, or reusable context-engineering conventions for software projects.
---
```

资源拆分规则：

- `references/codex-hooks.md`：Codex hook 事件、输入输出、限制。
- `references/gates.md`：Pre-flight、Plan、Implementation、Verification、Review、Commit。
- `references/context-budget.md`：Always read、read by task、do not read unless needed。
- `references/memory-policy.md`：`.context/memory.jsonl` 准入规则。
- `references/adr-policy.md`：哪些决策需要 ADR。
- `scripts/`：初始化或安装时使用的可复用辅助逻辑，不作为项目 hook 的运行时依赖。

不要把项目的 `.context/plan.md`、日志、状态、PRD 放入 skill。

运行时边界：

- `.codex/hooks/*.py` 和 `.codex/hooks.json` 只能依赖项目内稳定路径，例如 `scripts/vibe/*.py`。
- `.agents/skills/vibe-coding-3/scripts/*.py` 可以生成或安装这些项目脚本，但不应被 `Stop`、`PreToolUse` 等 hook 直接调用。
- 这样可以避免 skill 被移动、禁用或尚未安装时，项目 hooks 失效。

---

## 6. 外部 Skill 联合审查矩阵

| 审查面 | 使用 skill | 主要问题 |
|---|---|---|
| Codex 官方一致性 | `$openai-docs` | hook 位置、事件、matcher、输入输出协议、plugin/skill 边界是否正确 |
| Skill 化边界 | `yao-meta-skill`、`$skill-creator` | 是否应该做 skill、frontmatter 是否简洁、资源拆分是否符合 progressive disclosure |
| Agent 架构 | `ecc:agent-architecture-audit` | 是否有记忆污染、伪约束、隐藏循环、工具纪律失效 |
| 验收门禁 | `ecc:verification-loop` | build/type/lint/test/security/diff 是否有闭环 |
| 安全 | `ecc:security-review` | secrets、危险命令、权限扩大、依赖和日志泄漏 |
| 上下文预算 | `ecc:context-budget` | always-read 是否过重、references 是否懒加载、MCP/skill 是否过多 |
| 决策沉淀 | `ecc:architecture-decision-records` | 长期架构选择是否进入 ADR，而不是只进 `.context` |
| 分歧决策 | `ecc:council` | B、B+、C 的路线取舍是否经过反对意见检验 |

最小审查组：

```text
$openai-docs
+ yao-meta-skill / $skill-creator
+ ecc:agent-architecture-audit
+ ecc:verification-loop
+ ecc:security-review
```

完整审查组：

```text
最小审查组
+ ecc:context-budget
+ ecc:architecture-decision-records
+ ecc:council
```

---

## 7. 实施阶段

### Phase 0: 文档定稿

产物：

- 本方案文档。
- 5 轮联合审查记录。
- 明确遗留风险。

验收：

- 文档能清楚区分 `AGENTS.md`、skill、hook、script、`.context`、ADR、plugin。
- 文档不混用 Claude hookify 和 Codex hook。
- 文档标明 Codex hook 限制。

### Phase 1: 项目内 B+ 脚手架

产物：

```text
AGENTS.md
.codex/hooks.json
.codex/hooks/*.py
scripts/vibe/*.py
.context/
docs/
```

验收：

- `/hooks` 能看到项目 hooks。
- 未信任 hook 时有清晰提醒。
- 高风险 Bash 被阻断。
- Stop hook 能阻止“未验证即完成”。

### Phase 2: Repo Skill

产物：

```text
.agents/skills/vibe-coding-3/SKILL.md
.agents/skills/vibe-coding-3/references/
.agents/skills/vibe-coding-3/scripts/
.agents/skills/vibe-coding-3/agents/openai.yaml optional
```

验收：

- Skill 描述能被正确触发。
- `SKILL.md` 小而清晰。
- 长规则在 references 中按需读取。
- 确定性逻辑在 scripts 中可执行。

### Phase 3: Plugin 化

只有 B+ 和 repo skill 稳定后再做。

产物：

```text
plugins/vibe-coding/
├── .codex-plugin/plugin.json
├── skills/
├── hooks/
├── .mcp.json optional
└── assets/ optional
```

验收：

- plugin manifest 明确 `skills` 和 `hooks`。
- hook 路径不逃逸 plugin 根目录。
- 有本地 marketplace 测试入口。

---

## 8. 验收门禁

文档级验收：

- `Codex hook` 与 `Claude hookify` 明确分离。
- 不宣称 hook 覆盖所有工具。
- 不宣称 `PostToolUse` 能撤销副作用。
- `Stop` hook 写明 continuation 和防循环。
- skill frontmatter 只保留 `name`、`description`。
- `AGENTS.md` 不塞长篇方法论。
- `.context` 不进入 skill。
- 长日志只进 scratchpad，并有 summary。
- 重大决策进入 ADR。

实施级验收：

- hook 脚本可以读取 stdin JSON。
- hook 脚本对不认识的事件 fail open，并给出可诊断日志。
- safety deny 使用 Codex 当前支持的输出形态或 exit code `2`。
- 验证结果写入 `.context/verification.jsonl`，并包含 `session_id`、`turn_id`、`changed_files`、`changed_files_fingerprint`。
- 失败输出有 `.summary.md`。
- secret scan 至少覆盖 OpenAI、GitHub、AWS、private key 和 generic credential assignment。

---

## 9. 已知风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| Hook 覆盖不完整 | 某些工具路径绕过门禁 | 把关键验收放到 Stop hook、git hook、CI 和 scripts 中 |
| Hook 并发执行 | hook 间顺序依赖失效 | 每个 hook 独立、幂等，不依赖其他 hook 先运行 |
| Stop continuation 循环 | Codex 无法结束 | 检查 `stop_hook_active`，最多继续一次 |
| Skill 过大 | 上下文预算恶化 | `SKILL.md` 只放核心流程，细则进 references |
| 伪约束 | 模型“记得规则”但没有强制执行 | 高风险规则落到 scripts/hooks/CI |
| ADR 滥用 | 文档噪音 | 只记录跨周期、跨模块、影响架构或安全的决策 |
| Plugin 过早 | 维护负担增加 | B+ 稳定后再进入 C |

---

## 10. 联合审查日志

本节记录对本文档进行的固定 5 轮审查。每轮使用同一组视角：

```text
$openai-docs
yao-meta-skill / $skill-creator
ecc:agent-architecture-audit
ecc:verification-loop
ecc:security-review
ecc:context-budget
ecc:architecture-decision-records
ecc:council
```

### Round 1

审查重点：`$openai-docs` 官方一致性。

发现：

- 初稿已经正确区分 Codex hook 与 Claude hookify。
- 初稿写了 hook 输入输出协议，但需要确认来源为 Codex hooks 官方页，而不是 ECC/Claude 经验迁移。
- 初稿没有处理“项目尚未是 git 仓库”时的 repo-local hook 路径解析。

修正：

- 增加 `3.4 Hook 脚本定位规则`。
- 明确 hook command 使用 `git rev-parse --show-toplevel || pwd`。
- 要求脚本读取 stdin JSON 的 `cwd`，不要混淆 process cwd、git root 和项目 root。

结果：通过。

### Round 2

审查重点：`yao-meta-skill` / `$skill-creator` 的 skill 化边界。

发现：

- 初稿同时列出项目级 `scripts/vibe/*` 和 skill 内 `scripts/*`，但没有明确 hook 运行时应依赖哪一个。
- 如果 hook 直接调用 skill 内脚本，skill 被移动、禁用或未安装时，项目 hooks 会失效。

修正：

- 把“确定性脚本”拆成“项目确定性脚本”和“Skill 脚本”。
- 明确 `.codex/hooks/*.py` 只能依赖项目内稳定路径，例如 `scripts/vibe/*.py`。
- 明确 skill 内 scripts 只负责初始化、复制模板、生成或安装项目脚本，不作为运行时 hook 依赖。
- 把 `agents/openai.yaml` 标为 optional，避免强制创建不必要资源。

结果：通过。

### Round 3

审查重点：`ecc:agent-architecture-audit` 的隐藏循环、伪约束、记忆污染和工具纪律。

发现：

- 初稿的 Stop hook 只检查 `.context/verification.jsonl` 是否有记录，可能误用旧 green run。
- `PreCompact` 的表述容易让人误以为 hook 能替模型生成完整 checkpoint。

修正：

- 增加 verification freshness 规则。
- 要求验证记录包含 `session_id`、`turn_id`、`changed_files`、`changed_files_fingerprint`。
- 明确 Stop hook 只接受当前 changed-files fingerprint 匹配的 passed 记录。
- 明确 `PreCompact` 只写机械派生的最小 auto checkpoint，不替模型生成完整叙事 checkpoint。

结果：通过。

### Round 4

审查重点：`ecc:verification-loop`、`ecc:security-review`、`ecc:context-budget`、`ecc:architecture-decision-records`。

发现：

- 验证命令不能假设所有项目都有 `build/test/lint/typecheck` 同名脚本。
- `rtk` 规则需要边界，否则会误拦 hook command 或非 Bash 工具。
- secret scan 需要 allowlist 机制，否则示例和测试 fixture 容易误报。
- 本文档较长，不能直接复制成 `SKILL.md`。

修正：

- 增加验证命令发现顺序：`AGENTS.md`、`.context/plan.md` Verification Contract、项目文件推断、不可识别时报告 blocker。
- 增加 `rtk` 规则适用边界：只约束 Codex Bash 普通项目命令，不约束 hook command、apply_patch、MCP、内部工具。
- 增加 secret scan allowlist 和 fixture 规则。
- 在文档开头声明：本文是设计与审查文档，不是未来 `SKILL.md`。

结果：通过。

### Round 5

审查重点：`ecc:council` 路线取舍、整体一致性和 ADR 策略。

Council 视角：

- Architect：B+ 是正确中间态；直接 plugin 化会把未稳定规则固化。
- Skeptic：hook 不是完整安全边界，不能把所有可靠性交给 hooks。
- Pragmatist：先做 repo-local `AGENTS.md`、`.codex/hooks.json`、`scripts/vibe/*` 最快能产生收益。
- Critic：最大风险是 Stop hook 循环、旧验证误判、新 skill 过重、secret scan 误报。

结论：

- 保持 B+ 路线，不提前进入完整 C。
- Plugin 化只作为 Phase 3。
- 需要在真正实施 B+ 时记录一条 ADR，题目建议为 `ADR-0001-adopt-vibe-coding-b-plus.md`，记录“为什么选择 B+ 而不是纯 skill 或立即 plugin 化”。
- 当前阶段只写方案文档，不直接创建 ADR 目录；正式实施时再写 ADR，避免文档噪音。

结果：通过。五轮内未发现需要继续修正的错误。
