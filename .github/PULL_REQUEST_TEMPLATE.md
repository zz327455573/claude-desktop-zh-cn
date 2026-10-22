---
name: Pull Request
about: 贡献译文、修复脚本或改进文档
title: "<类型>: <简述>"
labels: ""
assignees: ""
---

## 这个 PR 做什么

<!-- 一句话说明 -->



## 类型

- [ ] 补充/修正译文
- [ ] 适配新版本 Claude Desktop
- [ ] 修复脚本 bug
- [ ] 改进文档
- [ ] 其他

## 改动清单

<!-- 改了哪些文件，为什么 -->



## 自检

- [ ] `python -m pytest tools/test_install.py -v` 全部通过
- [ ] 如果改了 `zh-CN.json`：确认没有引入占位符/ICU 结构不一致
      （CI 会查，但请先自己跑一遍，见 CONTRIBUTING.md）
- [ ] 如果改了 `install.py`：`python tools/install.py --dry-run` 正常
- [ ] 如果新增/改了 `.bat`：确认是 CRLF 换行
- [ ] 如果改了语言包内容：更新了 `I18N-COVERAGE-REPORT.md` 的对应数字

## 关联 issue

<!-- 例如：Closes #12 -->
