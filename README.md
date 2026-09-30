<div align="center">

# Claude Desktop 简体中文语言包

**Claude Desktop (Windows) 的完整简体中文本地化**

[![菜单覆盖](https://img.shields.io/badge/菜单-100%25-brightgreen)](https://github.com/zz327455573/claude-desktop-zh-cn)
[![界面覆盖](https://img.shields.io/badge/界面-99%25-green)](https://github.com/zz327455573/claude-desktop-zh-cn)
[![词条](https://img.shields.io/badge/词条-32500%2B-blue)](https://github.com/zz327455573/claude-desktop-zh-cn)
[![适配版本](https://img.shields.io/badge/适配-2.9939.4-green)](https://github.com/zz327455573/claude-desktop-zh-cn)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

官方从未发布简体中文语言包。上游社区项目
[Jyy1529/claude-desktop_win-zh_cn](https://github.com/Jyy1529/claude-desktop_win-zh_cn)
自 2026-07 停更，只覆盖约 1.3 万词条，且存在大量 `待翻译:` 占位。

**本项目是目前仍在维护的中文本地化来源**：

| 包 | 覆盖率 |
|---|---|
| `menu-zh-CN.json`（右键菜单、托盘菜单） | **100%** |
| `zh-CN.json`（前端界面） | **99%** |

界面剩余未覆盖的 key 中约 266 个**不含自然语言**——是占位符模板
（`{count} × {name}`）、产品名、示例值、单位与数字，显示的是变量值而非英文句子。
判断方法是对比官方日文本地化：官方同样保留英文的即为不该译。

[使用说明](#-使用说明) · [更新记录](CHANGELOG.md) · [参与翻译](CONTRIBUTING.md) · [问题反馈](.github/ISSUE_TEMPLATE/translation-issue.md)

</div>

---

## 这是什么

Claude Desktop（含 Claude Code 桌面版）的界面文案全部走 react-intl，
简体中文不在官方支持的语言列表里。本项目提供三份语言包文件，
放进对应目录即可让界面变成中文。

## 使用说明

### 方式一：直接下载（推荐）

从 [Releases](https://github.com/zz327455573/claude-desktop-zh-cn/releases/latest)
下载对应版本的语言包，覆盖到以下位置（`<版本号>` 见
`%LOCALAPPDATA%\AnthropicClaude\packages\RELEASES` 里最新的那行）：

| 下载的文件 | 覆盖到 |
|---|---|
| `zh-CN.json` | `%LOCALAPPDATA%\AnthropicClaude\app-<版本号>\resources\ion-dist\i18n\zh-CN.json` |
| `menu-zh-CN.json` | `%LOCALAPPDATA%\AnthropicClaude\app-<版本号>\resources\zh-CN.json` |
| `statsig-zh-CN.json` | `...\resources\ion-dist\i18n\statsig\zh-CN.json` |

然后把 `%LOCALAPPDATA%\Claude-3p\config.json` 的 `locale` 改成 `zh-CN`：

```json
{ "locale": "zh-CN" }
```

> ⚠️ **要改 `Local` 下的这份，不是 `Roaming` 的** —— 应用实际读 Local 这份。
> 改完**完全退出** Claude Desktop（托盘右键 → 退出，不是最小化）再打开。

### 方式二：脚本一键应用

```bash
git clone https://github.com/zz327455573/claude-desktop-zh-cn.git
cd claude-desktop-zh-cn
python tools/install.py
```

`install.py` 会自动识别当前运行的版本，完成全部四步：备份原版语言包 →
写入三份语言包 → 给 JS 补语言白名单 → 设好 locale。
加 `--dry-run` 可预览将改动的内容而不写入。

### 常见问题

<details>
<summary><b>为什么版本更新后界面又变回英文？</b></summary>

Claude Desktop 用 Squirrel 自动更新，每次更新都安装一个全新的
<code>app-x.x.x.x</code> 目录（干净官方文件），汉化不跟着迁移，
需要重新覆盖一次。
</details>

<details>
<summary><b>覆盖了语言包，设置里仍不显示简体中文？</b></summary>

JS 里还有一份语言白名单，需要把 <code>zh-CN</code> 加进去。
<code>tools/apply.py</code> 会处理；手动覆盖的话，在
<code>resources/ion-dist/assets/</code> 的 <code>shared-*.js</code> 里搜索
<code>"en-US"</code> 附近的语言数组，把 <code>"zh-CN"</code> 补进去。
</details>

<details>
<summary><b>个别地方还是英文 / 显示 “待翻译”？</b></summary>

官方会把新功能的文案 id 重新 hash，旧 key 失效、新 key 没译文。
带上界面截图和具体文案去提 issue，会补进下一个版本。
</details>

<details>
<summary><b>改完语言包闪退/白屏</b></summary>

语言包 JSON 损坏会导致解析失败。先验证再重启：

```bash
python -c "import json;json.load(open('zh-CN.json',encoding='utf-8'))"
```
</details>

## 覆盖范围说明

官方界面文字分两类：

1. **走 react-intl 的文案**（有 `id` + `defaultMessage`）—— **本项目 100% 覆盖**
2. **硬编码在组件里的英文**（如 `<button>Cancel</button>`）—— 不在语言包里，需改 JS

第 2 类约有数万处，其中很多是代码逻辑值（图标名 `Copy`、AST 节点名、
枚举值等），盲目替换会引发运行事故。汉化工具只挑高频 UI 词替换那几百处，
不做全覆盖——这是有意的权衡，不是遗漏。

## 目录结构

```
claude-desktop-zh-cn/
├── zh-CN.json              主语言包（前端界面，react-intl 格式，约 3.2 万条）
├── menu-zh-CN.json           Electron 原生右键菜单
├── statsig-zh-CN.json      Statsig 实验平台
├── docs/
│   └── terminology.json    术语表（翻译必读，保证全文一致）
├── tools/
│   ├── install.py          一键应用（语言包 + 白名单 + locale + 备份）
│   ├── sync.py             对比当前版本英文源，导出待译增量
│   ├── apply.py            合并增量翻译并校验
│   ├── validate.py         占位符/ICU 结构一致性校验
│   ├── scan-missing.py     扫描当前版本的未翻译词条
│   └── merge-patches.py    合并增量补丁文件
├── .github/
│   └── ISSUE_TEMPLATE/     问题反馈模板
├── CHANGELOG.md            更新记录
└── CONTRIBUTING.md         参与翻译指南
```

## 参与翻译

官方版本更新会带来新的未翻译词条。本项目维护一套增量工作流，
每轮只需翻译新增部分，不必重译整包。详见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## 术语约定

`docs/terminology.json` 是必须遵守的术语表，选自高频 UI 概念，
保证同一英文词在全站译法一致（Artifact → 制品、Session → 会话、
Connector → 连接器、Effort → 推理强度等）。

## 致谢

初始翻译基础来自 [Jyy1529/claude-desktop_win-zh_cn](https://github.com/Jyy1529/claude-desktop_win-zh_cn)（已停更）。
本项目接管维护，并修复了若干会影响运行的翻译缺陷：
变量名被误译成中文（`{role}` → `{角色}`，会让 react-intl 运行时找不到变量）、
ICU 复数块被整体删除（导致参数缺失）等。

## License

[MIT](LICENSE)。Claude Desktop 本体版权归 Anthropic 所有，
本仓库不包含任何官方代码，仅提供语言包和工具。
