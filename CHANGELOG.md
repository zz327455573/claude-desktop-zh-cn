# 更新记录

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与
[语义化版本](https://semver.org/lang/zh-CN/)。版本号对应适配的 Claude Desktop 版本。

## 每个版本包含的信息

- 适配的 Claude Desktop 版本
- react-intl 词条总数与覆盖数
- 本轮新增/废弃的词条量
- 修复的问题

---

## [v2.9939.2] - 2026-09-28

适配 Claude Desktop **2.9939.2**。

### 覆盖情况

| 指标 | 数值 |
|---|---|
| react-intl 总词条 | 31,727 |
| 已覆盖 | 31,726 |
| **覆盖率** | **100.0%** |
| 占位符/ICU 结构校验 | 0 不一致 |

### 变更

- **新增 1,803 条翻译**，覆盖 2.9939.2 引入的新功能文案
- **清理 612 条旧词条**：官方重构了 message id，这些 key 在当前版本已不存在
- 新增覆盖的功能模块包括：
  - Routine（例行任务）相关界面
  - Claude in Chrome 浏览器控制（点击、滚动、输入等交互授权文案）
  - Partner / Enterprise 渠道与账单
  - MCP 服务器目录审核流程补充
  - 各类新的权限请求与设备验证提示
- 全部译文通过占位符与 ICU 结构校验，不存在会引发 react-intl 运行时错误的条目

[本次发布的完整说明](https://github.com/zz327455573/claude-desktop-zh-cn/releases/tag/v2.9939.2)

---

## [v2.7032.0] - 2026-09-23

适配 Claude Desktop **2.7032.0**。**里程碑版本** —— 从 83% 补到 100%。

### 覆盖情况

| 指标 | 数值 |
|---|---|
| react-intl 总词条 | 30,859 |
| 已覆盖 | 30,850 |
| **覆盖率** | **100.0%** |

### 变更

- **新增 12,115 条翻译**（该版本相对 1.52386.6 的新增词条 + 上游遗留占位）
- **清除 8,686 条 `待翻译:` 占位**：上游把未译词条直接写成 `待翻译:<原文>`，
  界面会显示成 “待翻译：xxx”。已按英文原文全部重译
- **修复 10 条 runtime bug**：上游把占位符变量名也译成了中文
  （如 `{role}` → `{角色}`、`{model}` → `{模型}`），
  react-intl 运行时找不到变量会导致界面异常。这是此前“汉化不完整”的隐藏原因之一
- **修复 3 条 ICU 结构问题**：复数块被整体删除、占位符多插/漏插
- 新增覆盖的功能模块：Remote Control、Effort（推理强度）、fast mode、
  Cowork、worktree、Claude in Chrome、插件目录、MCP 服务器注册、Hook 配置等
- 建立增量翻译工作流（`tools/sync.py` → 翻译 → `tools/apply.py` →
  `tools/validate.py` 校验），后续版本更新只需翻译新增部分

[本次发布的完整说明](https://github.com/zz327455573/claude-desktop-zh-cn/releases/tag/v2.7032.0)

---

## [v1.52386.6] - 2026-09-15

初始版本。在上游 `Jyy1529/claude-desktop_win-zh_cn` 12,700 条基础上
新增 1,339 条，覆盖该版本 1.52386.6 的新增功能（Aibo 助手、插件目录、
MCP 注册、Hook 配置等）。

---

[未发布]: https://github.com/zz327455573/claude-desktop-zh-cn/compare/v2.9939.2...HEAD
[v2.9939.2]: https://github.com/zz327455573/claude-desktop-zh-cn/compare/v2.7032.0...v2.9939.2
[v2.7032.0]: https://github.com/zz327455573/claude-desktop-zh-cn/compare/v1.52386.6...v2.7032.0
[v1.52386.6]: https://github.com/zz327455573/claude-desktop-zh-cn/releases/tag/v1.52386.6
