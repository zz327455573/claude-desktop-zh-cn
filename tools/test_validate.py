#!/usr/bin/env python3
"""validate.py 的回归测试。

校验器是翻译质量的唯一自动防线（它会拒绝写入占位符不一致的译文），
所以它自己必须被测试覆盖。改动 validate.py 后务必跑这个。

    python tools/test_validate.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import signature  # noqa: E402

# (说明, 英文, 中文, 是否应该被判为不一致)
CASES = [
    # --- 必须抓到的真 bug ---
    ("变量名被误译", "My role is {role}.", "我的角色是 {角色}。", True),
    ("占位符漏译", "Only {gb} GB free.", "仅剩 GB。", True),
    ("占位符多插", "Added {n}.", "添加了 {n} 个共 {m}。", True),
    ("plural 删掉一个分支", "{c, plural, one {# file} other {# files}}",
     "{c, plural, one {# 个文件}}", True),
    ("select 删掉一个分支", "{p, select, a {Alpha} other {Beta}}",
     "{p, select, a {甲}}", True),
    ("行内标签名被译", "<link>Learn more</link>", "<链接>了解更多</链接>", True),
    ("number 格式修饰符丢失", "{n, number} / {limit, number}",
     "{n} / {limit}", True),

    # --- 不能误报的正常译法 ---
    ("plural 中文无单复数同译", "{n, plural, one {# minute} other {# minutes}}",
     "{n, plural, one {# 分钟} other {# 分钟}}", False),
    ("select 分支译成中文", "{p, select, daily {Daily} other {Monthly}}",
     "{p, select, daily {每日} other {每月}}", False),
    ("嵌套 plural 内嵌 select", "{c, plural, one {{s, select, a {A} other {B}}} other {# 项}}",
     "{c, plural, one {{s, select, a {甲} other {乙}}} other {# 项}}", False),
    ("含 # 计数的分支", "{c, plural, one {# commit} other {# commits}}",
     "{c, plural, one {# 个提交} other {# 个提交}}", False),
    ("空分支保留", "{c, plural, =0 {} one {# item} other {# items}}",
     "{c, plural, =0 {} one {# 项} other {# 项}}", False),
]


def main() -> int:
    failed = 0
    for desc, en, zh, should_fail in CASES:
        bad = signature(en) != signature(zh)
        if bad != should_fail:
            failed += 1
            kind = "漏检（真 bug 没抓到）" if should_fail else "误报（正常译法被拒）"
            print(f"FAIL  {desc}: {kind}")
            print(f"        en: {en}")
            print(f"        zh: {zh}")
        else:
            print(f"ok    {desc}")

    print(f"\n{len(CASES) - failed}/{len(CASES)} 通过")
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
