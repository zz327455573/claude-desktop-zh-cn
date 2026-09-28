# 参与翻译指南

感谢你愿意参与 Claude Desktop 的中文本地化。本文说明如何在版本更新后
补全新增词条，以及必须遵守的翻译规范。

## 工作流总览

```
tools/sync.py          对比当前版本英文源，导出待译增量 out/todo.json
      ↓
   人工/AI 翻译        out/todo.json → out/translated.json
      ↓
tools/apply.py         合并进 zh-CN.json（自动校验，不一致拒绝写入）
      ↓
tools/validate.py      全量校验占位符与 ICU 结构
      ↓
   git commit & push
```

## 第一步：生成待译清单

```bash
cd claude-desktop-zh-cn
python tools/sync.py
```

会自动识别当前运行的 Claude Desktop 版本，输出：

```
该版本英文总词条: 31727
zh-CN 已覆盖:      29924  (94.3%)
待翻译(含占位符):  1803
旧词条(新版已删):   612
```

待译清单在 `out/todo.json`，格式为 `{key: 英文原文}`。

> `out/` 在 `.gitignore` 里，不会误提交。

## 第二步：翻译

把 `out/todo.json` 的 value 全部译成中文，保存为 `out/translated.json`
（`{key: 中文译文}`，key 一个都不能改）。

### 必须遵守的规范

1. **占位符原样保留，且出现次数必须与原文一致**

   ```json
   "FvUCks/zNL": "Only {availableGb, number} GB is free on the disk containing {worktreeDir}. A worktree needs at least {requiredGb, number} GB."
   ```

   译文中 `{availableGb, number}` `{requiredGb, number}` `{worktreeDir}`
   必须原样出现，次数一致。**多插或漏插都会导致界面错乱。**

2. **绝对不能翻译变量名**

   ```json
   "9qVxOC/tnJ": "My role is {role}."
   ```
   ✅ `我的角色是 {role}。`
   ❌ `我的角色是 {角色}。`  ← 这会让 react-intl 运行时找不到变量

   这是上游真实踩过的坑，`validate.py` 会抓出来。

3. **ICU 复数/选择格式：结构和分支数必须保留**

   ```json
   "{count, plural, one {# file didn’t upload.} other {# files didn’t upload.}} Try again."
   ```

   译成中文时**即使没有单复数差异，也必须保留每个分支并各给译文**：

   ```
   {count, plural, one {# 个文件上传失败。} other {# 个文件上传失败。}}请重试。
   ```

   ❌ 不能因为“中文一样”就把整个 plural 块删掉 —— 会导致参数缺失。

4. **行内标签只译标签内文字**

   ```
   <link>Learn more about usage limits</link>
   ```
   ✅ `<link>了解用量限制详情</link>`
   ❌ `<链接>了解用量限制详情</链接>`

5. **术语遵循 `docs/terminology.json`**

   术语表锁定的译法必须一致（Artifact → 制品、Session → 会话、
   Connector → 连接器、Effort → 推理强度等）。
   术语表没有的词，保持全站一致即可。

6. **标点规范**

   | 场景 | 规则 | 例 |
   |---|---|---|
   | 按钮、菜单项 | 不加句号 | `保存` `删除` `重新连接` |
   | 进行中/对话框动作 | 用 `…`（单个省略号字符） | `正在保存…` `选择环境…` |
   | 说明、提示文字 | 用 `。` | `设置已保存。` |
   | 疑问句 | 用 `？` | `确定要删除吗？` |

7. **用“你”不用“您”**

8. **专有名词保留英文**

   MCP、GitHub、GitLab、SSO、JWKS、Okta、WorkOS、Entra ID、macOS、
   Windows、WSL、SSH、Claude Code、Cowork、Anthropic、OAuth 等。
   URL、路径、示例值、JSON 字面量一律原样保留。

## 第三步：合并并校验

```bash
python tools/apply.py out/translated.json
python tools/validate.py out/en-cache.json zh-CN.json
```

`apply.py` 合并前会逐条校验占位符，**不一致的条目拒绝写入**并列出明细，
不会污染主包。修好 `translated.json` 后重跑即可。

`validate.py` 输出 `占位符/标签不一致: 0` 才算通过。

## 第四步：提交

```bash
git add zh-CN.json docs/
git commit -m “feat(zh-CN): 适配 Claude Desktop <版本号>，覆盖 XX%”
git push
```

## 提交信息规范

采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
feat(zh-CN): 适配 2.9939.2，补全 1803 条新增词条
fix(zh-CN): 修复 {role} 等变量名被误译导致界面异常
docs: 更新术语表
chore: 清理废弃词条
```

## 报告问题

发现某个界面位置显示英文、显示“待翻译”、或译文明显错了，
请按 [issue 模板](.github/ISSUE_TEMPLATE/translation-issue.md) 提交，
附上界面截图和具体文案。
