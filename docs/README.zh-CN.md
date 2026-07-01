# Vibe Coding Context Engineering 中文说明

Vibe Coding Context Engineering 是一套面向 Codex 的 AI 编程工作流工程化模板。它把 Vibe Coding 工作流落成项目规则、Codex hooks、确定性验收脚本、可复用 skill，以及可安装的本地 Codex plugin。

目标不是让 AI “更会聊天”，而是让 AI 辅助开发在长任务中可恢复、可约束、可验证。

## 这个项目解决什么

它把 AI 编程过程拆成几层：

- `docs/`：稳定的人类设计上下文，例如 PRD、验收标准、架构决策、运行手册。
- `.context/`：动态 AI 工作状态，例如当前计划、状态、验收记录、scratchpad 摘要。
- `.codex/`：Codex 项目级 hooks，用于生命周期约束。
- `.agents/skills/`：项目内可复用 skill，用来指导 Codex 怎么按这个工作流做事。
- `plugins/`：可安装的 Codex plugin，用来跨项目分发 skill、hooks 和脚手架。

一句话：`skill` 是能力和流程，`plugin` 是这套能力的安装包。

## 主要能力

- 项目级 `AGENTS.md`，保存长期有效的工作契约。
- `.codex/hooks/`，对危险命令、验证新鲜度、压缩前检查点等做生命周期约束。
- `scripts/vibe/`，提供上下文结构检查、秘密扫描、验证记录、插件检查和完整验收。
- `.agents/skills/vibe-coding-3/`，提供 Vibe Coding 工作流的 Codex skill。
- `plugins/vibe-coding/`，提供可安装的 Codex plugin。
- `.github/workflows/vibe-verify.yml`，在 GitHub Actions 上跑完整验证。

## 快速开始

克隆仓库：

```bash
git clone https://github.com/AetherX-Technologies/vibe-coding-context-engineering.git
cd vibe-coding-context-engineering
```

运行完整本地验证：

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

如果你的 Codex 工作区使用 RTK，可以用：

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full
```

## 安装本地 Codex Plugin

把本仓库加入 Codex 本地插件 marketplace：

```bash
codex plugin marketplace add /absolute/path/to/vibe-coding-context-engineering
```

安装插件：

```bash
codex plugin add vibe-coding@local-vibe-coding
```

然后开启新的 Codex 线程，显式调用 skill：

```text
Use $vibe-coding-3 to initialize or operate this Vibe Coding workflow workspace.
```

插件更新、重新安装、hook 审查和脚手架冒烟测试见：

[docs/runbooks/vibe-plugin-installation.md](runbooks/vibe-plugin-installation.md)

## 给其他项目安装脚手架

可以把 Vibe Coding 工作流脚手架安装到另一个目标目录：

```bash
python3 plugins/vibe-coding/skills/vibe-coding-3/scripts/install_project_scripts.py --target /path/to/target-project
```

验证目标项目：

```bash
python3 /path/to/target-project/scripts/vibe/verify_all.py --root /path/to/target-project --profile phase1
```

## 验收方式

主要本地验收命令：

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

如果需要记录当前本地验收证据：

```bash
python3 scripts/vibe/verify_all.py --root . --profile full --record
python3 scripts/vibe/check_verification_freshness.py --root .
```

CI 会运行完整验证，但不会写入本地验收记录。

## 注意事项

- hooks 是工程约束，不是安全审计的替代品。
- `.context/` 是动态工作状态；公开仓库只保留最小可恢复状态。
- 插件安装后建议开启新 Codex 线程测试，因为 plugin/skill 更新通常需要新的加载边界。
- 运行时 hooks 应调用项目本地 `.codex/hooks/` 和 `scripts/vibe/`，不要依赖 plugin cache 里的脚本。

## 许可证

本项目使用 MIT License。详见仓库根目录的 `LICENSE`。
