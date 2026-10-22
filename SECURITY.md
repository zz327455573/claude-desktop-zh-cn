# 安全政策

## 这个项目会动你的电脑吗

会，但范围严格限定，且全部可逆。**这是本项目唯一的"副作用"，请务必读一遍。**

`一键汉化.bat` / `tools/install.py` 只做四件事：

| # | 动作 | 位置 |
|---|---|---|
| 1 | 备份原版文件 | 仓库目录下 `out/original-backup/<版本>/` |
| 2 | 写入 4 个 JSON 语言包 | `%LOCALAPPDATA%\AnthropicClaude\app-<版本>\resources\ion-dist\i18n\`（含 `dynamic\` 子目录） |
| 3 | 给 1 个 JS 文件的语言白名单加一个条目 | 同版本 `resources\ion-dist\assets\v1\shared-*.js` |
| 4 | 改 2 个配置文件的 `locale` 字段 | `%APPDATA%\Claude-3p\config.json` 与 `%LOCALAPPDATA%\Claude-3p\config.json` |

### 明确不做的事

- **不请求管理员权限**，不弹 UAC。只读写当前用户自己的 AppData，不需要提权
- **不联网**。脚本没有任何网络请求，运行时不下载任何东西
- **不读取、不上传你的任何数据**。不碰对话记录、不碰账号凭据、不碰剪贴板
- **不加入开机启动**，不写注册表，不装服务，不改系统设置
- **不改 Claude 程序本体**（`claude.exe`、`app.asar` 均不碰），只改资源文件

### 怎么自己核实

这个项目全部代码开源，运行前你可以自己看：

```bash
:: 一键汉化.bat 只有 80 行，可以先读完再双击
notepad 一键汉化.bat

:: 真正干活的是这两个 Python 文件
notepad tools\install.py
notepad tools\restore.py
```

也可以用 `--dry-run` 预览它将改动什么而不实际写入：

```bash
python tools/install.py --dry-run
```

### 怎么撤销

双击 **`还原.bat`** 即可恢复官方原版，界面回到英文。
即使没有备份（比如你只下载了 ZIP、没在本机跑过安装），还原脚本也能通过删除注入文件 +
反向修改白名单来恢复原状。

## 报告安全问题

如果你发现本项目代码存在安全问题（比如意外读取了不该读的文件、有意外的网络行为），
请**不要**直接提公开 issue，而是通过 GitHub 的
[私密漏洞报告](https://github.com/zz327455573/claude-desktop-zh-cn/security/advisories/new)
提交。我们会在 7 天内响应。

## 关于语言包文件的完整性

每次发布会在 `SHA256SUMS.txt` 提供语言包的 SHA256 校验和，发布页面也会附上。
下载后可以自己核对，确认文件没被篡改：

```bash
sha256sum -c SHA256SUMS.txt
```
