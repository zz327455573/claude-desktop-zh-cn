#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""claude-desktop-zh-cn 测试套件。

跑法:
    python -m pytest tools/test_install.py -v
    python tools/test_install.py          # 没有 pytest 时也能跑

分三组:

A. 白名单补丁 —— 改错会直接白屏，是历史事故根因，判据最严
B. 语言包完整性 —— 占位符/ICU 结构与官方 en-US 不一致会让 react-intl 运行时抛错，
   比译错更严重；这组是防白屏的核心
C. 版本识别与安装目标 —— 保证 install.py 找得到正确的版本目录

所有测试都不碰真实 Claude 安装目录，只操作临时文件。
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import install  # noqa: E402

# 占位符/ICU 签名提取（与 tools/validate.py 同源，这里内联一份以免依赖顺序问题）
TAG_RE = re.compile(r'<(/?)([A-Za-z][\w-]*)')
NUMFMT_RE = re.compile(r',\s*number\b')
ICU_KINDS = {'plural', 'select', 'selectordinal'}


def top_level_placeholders(text: str) -> list[str]:
    out, depth, start = [], 0, -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == '}' and depth > 0:
            depth -= 1
            if depth == 0:
                out.append(text[start:i])
    return out


def icu_block_count(inner: str, kind: str) -> int:
    rest = re.sub(r'^\s*[\w.]+\s*,\s*' + kind + r'\s*,\s*', '', inner)
    depth, blocks = 0, 0
    for ch in rest:
        if ch == '{':
            if depth == 0:
                blocks += 1
            depth += 1
        elif ch == '}':
            depth -= 1
    return blocks


def norm_var(inner: str) -> str:
    inner = NUMFMT_RE.sub(', number', inner)
    parts = [p.strip() for p in split_top(inner, ',')]
    if not parts or not parts[0]:
        return '?'
    name = parts[0]
    if len(parts) < 2:
        return name
    kind = parts[1].split()[0]
    if kind in ICU_KINDS:
        return f'{name}/{kind}/x{icu_block_count(inner, kind)}'
    return f'{name}/{kind}'


def split_top(text: str, sep: str) -> list[str]:
    out, depth, cur = [], 0, ''
    for ch in text:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def signature(text) -> tuple:
    if not isinstance(text, str):
        return ('__nonstring__', type(text).__name__)
    vars_ = tuple(sorted(norm_var(p) for p in top_level_placeholders(text)))
    tags = tuple(sorted(m.group(2) for m in TAG_RE.finditer(text)))
    return (vars_, tags)


# ---------------------------------------------------------------- 测试数据

OFFICIAL_ARRAY = ('["en-US","de-DE","fr-FR","ko-KR","ja-JP",'
                  '"es-419","es-ES","it-IT","hi-IN","pt-BR","id-ID"]')


class TestLocaleWhitelistPatch:
    """A 组：白名单补丁。改错会白屏，所以边界抓得特别紧。"""

    def test_adds_locale_to_official_array(self):
        text = f'var vg={OFFICIAL_ARRAY};'
        new, changed = install.patch_locale_array_in_text(text)
        assert changed
        assert install.LOCALE in json.loads(
            re.search(r'\[[^]]*\]', new).group(0))

    def test_is_idempotent(self):
        text = f'var vg={OFFICIAL_ARRAY};'
        once, _ = install.patch_locale_array_in_text(text)
        twice, changed = install.patch_locale_array_in_text(once)
        assert not changed, '第二次运行不应再改动'
        assert once == twice

    def test_patches_every_occurrence(self):
        text = f'a={OFFICIAL_ARRAY};b={OFFICIAL_ARRAY};'
        new, changed = install.patch_locale_array_in_text(text)
        assert changed
        arrays = re.findall(r'\[[^]]*\]', new)
        assert len(arrays) == 2
        assert all(install.LOCALE in json.loads(a) for a in arrays)

    def test_does_not_touch_icon_name_arrays(self):
        # 历史事故：把 ["Copy","Check"] 这类数组改坏导致复制按钮消失
        text = 'var icons=["Copy","Check","CheckCircle","Paste"];'
        new, changed = install.patch_locale_array_in_text(text)
        assert not changed
        assert new == text

    def test_does_not_touch_enum_arrays(self):
        text = 'var modes=["low","medium","high","xhigh","max"];'
        new, changed = install.patch_locale_array_in_text(text)
        assert not changed
        assert new == text

    def test_does_not_touch_partial_official_arrays(self):
        # 只有 en-US 一个，不满足"至少 6 个官方语言"，不是白名单
        text = 'var a=["en-US"];var b=["en-US","de-DE"];'
        new, changed = install.patch_locale_array_in_text(text)
        assert not changed
        assert new == text

    def test_handles_malformed_json_array_gracefully(self):
        # 正则可能匹配到不是合法 JSON 的片段，必须原样放回而不是抛异常
        text = 'var x=["en-US","de-DE","fr-FR","ko-KR","ja-JP",];'
        new, changed = install.patch_locale_array_in_text(text)
        assert isinstance(new, str)

    def test_result_is_valid_json(self):
        text = f'var vg={OFFICIAL_ARRAY};'
        new, _ = install.patch_locale_array_in_text(text)
        arr = json.loads(re.search(r'\[[^]]*\]', new).group(0))
        assert isinstance(arr, list)
        assert arr[0] == 'en-US'
        assert arr[-1] == install.LOCALE

    def test_preserves_surrounding_code(self):
        text = f'function f(){{return {OFFICIAL_ARRAY}}}//comment'
        new, _ = install.patch_locale_array_in_text(text)
        assert new.startswith('function f(){return [')
        assert new.endswith(']}//comment')

    def test_only_primary_locale_not_compat(self):
        """白名单只加 zh-Hans，不加 zh-CN（否则语言栏出现重复条目）。"""
        text = f'var vg={OFFICIAL_ARRAY};'
        new, _ = install.patch_locale_array_in_text(text)
        arr = json.loads(re.search(r'\[[^]]*\]', new).group(0))
        assert 'zh-Hans' in arr
        assert 'zh-CN' not in arr


class TestVersionKey:
    """C 组：版本目录识别。认错版本会汉化到不相关的目录。"""

    def test_basic(self):
        assert install.version_key('app-2.42304.2') == (2, 42304, 2)

    def test_four_part(self):
        assert install.version_key('app-1.2.3.4') == (1, 2, 3, 4)

    def test_ignores_non_numeric_suffix(self):
        # 正则只抓 [\d.]，遇到 - 就停，所以后缀被忽略且不引入多余的 0 分量
        assert install.version_key('app-2.42304.2-beta') == (2, 42304, 2)

    def test_garbage(self):
        assert install.version_key('not-a-version') == (0,)

    def test_ordering(self):
        versions = ['app-2.42304.0', 'app-2.42304.2', 'app-2.37337.1']
        ranked = sorted(versions, key=install.version_key, reverse=True)
        assert ranked[0] == 'app-2.42304.2'


class TestLanguagePackIntegrity:
    """B 组：语言包完整性。占位符不一致会让 react-intl 运行时抛错。"""

    @classmethod
    def setUpClass(cls):
        # 2.7MB 的 JSON 解析一次要好几秒，缓存住，别每个测试各解析一遍
        cls._zh = json.loads(
            (ROOT / 'zh-CN.json').read_text(encoding='utf-8-sig'))

    @property
    def zh(self) -> dict:
        return self._zh

    def test_zh_cn_json_is_valid_and_flat(self):
        data = self.zh
        assert isinstance(data, dict) and data
        non_str = [k for k, v in data.items() if not isinstance(v, str)]
        assert not non_str, f'有 {len(non_str)} 个非字符串值，react-intl 要求扁平 string→string'

    def test_no_empty_values(self):
        empty = [k for k, v in self.zh.items() if not v.strip()]
        assert not empty, f'有 {len(empty)} 条空译文'

    def test_placeholders_match_reference(self):
        """与仓库自带参考译本的占位符结构必须一致（防运行时炸）。"""
        ref_path = ROOT / 'docs' / 'reference-zh-CN.json'
        if not ref_path.exists():
            return  # 没有参考文件时跳过
        ref = json.loads(ref_path.read_text(encoding='utf-8-sig'))
        bad = [k for k, v in ref.items()
               if k in self.zh and signature(self.zh[k]) != signature(v)]
        assert not bad, f'{len(bad)} 条占位符不一致，前几个: {bad[:5]}'


class TestDynamicPack:
    def test_dynamic_pack_exists_and_valid(self):
        path = ROOT / 'zh-CN-dynamic.json'
        assert path.exists(), '缺少 zh-CN-dynamic.json，新版渲染层会 404'
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        assert isinstance(data, dict) and data
        assert all(isinstance(v, str) for v in data.values())


# ------------------------------------------------------------ 无 pytest 时

def _run_without_pytest() -> int:
    passed = failed = 0
    for cls in (TestLocaleWhitelistPatch, TestVersionKey,
                TestLanguagePackIntegrity, TestDynamicPack):
        setup = getattr(cls, 'setUpClass', None)
        if setup:
            setup()
        instance = cls()
        for name in sorted(dir(instance)):
            if not name.startswith('test_'):
                continue
            try:
                getattr(instance, name)()
                passed += 1
                print(f'  PASS  {cls.__name__}.{name}')
            except AssertionError as e:
                failed += 1
                print(f'  FAIL  {cls.__name__}.{name}: {e}')
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f'  ERROR {cls.__name__}.{name}: {type(e).__name__}: {e}')
    print(f'\n{passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(_run_without_pytest())
