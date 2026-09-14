# Claude Desktop 中文语言包（社区维护版）

> 上游汉化项目 [Jyy1529/claude-desktop_win-zh_cn](https://github.com/Jyy1529/claude-desktop_win-zh_cn) 自 2026-07-25 起停滞，新版 Claude Desktop（app-1.52386.6）新增的大量功能未覆盖。
> 本仓库在上游 12700 条基础上，补齐了 1339 条新功能文案，使其对应当前版本的 react-intl 词条实现 **100% 覆盖**（重扫确认 0 缺失）。

## 这是什么

Claude Desktop（Claude Code 桌面版，安装于 `%LOCALAPPDATA%\AnthropicClaude\`）的中文语言包。
每次版本更新，Squirrel 会装一个全新的 `app-xxx` 目录，汉化会被清零，需要重打一遍。

本仓库提供：
- **`zh-CN.json`** —— 完整中文界面语言包，**36977 条**（上游 35638 + 本仓库新增 1339）
- **`菜单-zh-CN.json`** —— Electron 原生右键菜单翻译
- **`补丁-第一部分.json` / `补丁-第二部分.json`** —— 本次新增的 1339 条增量翻译
- **`合并补丁.py`** —— 把增量合并进完整语言包的脚本
- **`扫描缺失.py`** —— 扫描新版 JS 找出未翻译词条的工具（版本更新后用它定位新词）

## 新增覆盖了什么

这 1339 条主要覆盖 Claude Desktop 8-9 月新增的功能模块（上游 7 月版本里没有的）：

- **Aibo 个人助手** —— 日历管理、邮件、待办、页面、位置共享、语音消息、权限请求等完整界面
- **插件目录（Plugin Directory）** —— 提交、验证、扫描、审核、发布、下架、重新上架、安全检查全套流程文案
- **MCP 服务器注册** —— 未注册服务器、directory 链接、OAuth、租户 URL 等
- **Hook 配置** —— 各类 hook 事件（工具调用前后、会话开始、压缩前等）
- **权限/登录/验证请求** —— 重新连接、设备验证、浏览器访问批准
- **新模型与思考模式** —— 自适应思考、扩展思考、快速模式、Opus/Sonnet 说明
- **体验数据重置、用量上限、组织管理** 等

## 怎么用

> 前提：你已经在用上游的 `patch_windowsapps_json_only.py` 和 `patch_chunks_zh_cn.py` 打过汉化。本仓库只替换/补充其中的语言包。

### 打汉化（版本更新后）

```bash
cd /d/AI-Tools/claude-zh-patch/claude-desktop_win-zh_cn-master

# 1. 用本仓库的 zh-CN.json 替换上游那份
cp /d/AI-Tools/claude-desktop-zh-cn/zh-CN.json resources/frontend-zh-CN.json
cp /d/AI-Tools/claude-desktop-zh-cn/菜单-zh-CN.json resources/desktop-zh-CN.json

# 2. 跑上游补丁脚本（把 <新版本> 换成实际目录名）
python patch_windowsapps_json_only.py --app-dir "C:\Users\Admin\AppData\Local\AnthropicClaude\app-<新版本>"
python patch_chunks_zh_cn.py --app-dir "C:\Users\Admin\AppData\Local\AnthropicClaude\app-<新版本>"

# 3. 跑误伤修复（必跑，带语法门禁）
python "C:\Users\Admin\AppData\Local\AnthropicClaude\汉化说明\fix-zh-patch-damage.py"
```

### 改 locale

打开 `C:\Users\Admin\AppData\Local\Claude-3p\config.json`，确认：
```json
"locale": "zh-CN"
```
> 注意：应用读的是 Local 这份。更新可能把它重置回 en-US，必须检查。
> Claude Desktop 必须完全退出（托盘右键退出）再改，否则退出时会用内存里的旧值回写覆盖。

### 重启

完全退出 Claude Desktop（托盘右键退出，不是最小化）再打开。

## 版本更新后自己补词

新版本装上后，词条会对不上。用本仓库的扫描工具定位新词：

```bash
python 扫描缺失.py
# 输出 missing_keys.json，列出所有新版 JS 里有、语言包里没有的 id
```

然后人工翻译，用 `合并补丁.py` 合并进 `zh-CN.json`。这就是本仓库 1339 条的来源。

## 为什么不覆盖全部英文

Claude Desktop 的界面文字分两类：

1. **走 react-intl 的文案**（有 `id` + `defaultMessage`）—— **本仓库已 100% 覆盖**（重扫 0 缺失）
2. **硬编码在组件里的英文字符串**（如 `<button>Cancel</button>`）—— 这类不在语言包里，需要改 JS

第 2 类有约 7 万处，其中很多是代码逻辑值（图标名 `Copy`、AST 节点 `ADBE Vector Group`、枚举值 `Assignment` 等），盲替换会复现"复制按钮消失"那类事故。所以上游只挑高频词替换（`patch_chunks_zh_cn.py` 那几百处），不做全覆盖。这是有意的权衡，不是遗漏。

## 致谢与版权

- 基础汉化（12700 条 + 补丁工具）来自 [Jyy1529/claude-desktop_win-zh_cn](https://github.com/Jyy1529/claude-desktop_win-zh_cn)，MIT 许可
- 本仓库在它基础上新增的 1339 条翻译为社区补充，同样以 MIT 许可发布
- Claude Desktop 本体版权归 Anthropic 所有，本仓库不包含任何官方代码，仅提供语言包和工具

## 上游 PR

本仓库的 1339 条增量已可向上游提交 PR。如果你 fork 上游想合并，直接用 `补丁-第一部分.json` + `补丁-第二部分.json` 合并进上游的 `frontend-zh-CN.json` 即可。
