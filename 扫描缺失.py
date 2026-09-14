import json, re, os, glob, sys

v1_dir = r"C:/Users/Admin/AppData/Local/AnthropicClaude/app-1.52386.6/resources/ion-dist/assets/v1"
zh_path = r"C:/Users/Admin/AppData/Local/AnthropicClaude/app-1.52386.6/resources/ion-dist/i18n/zh-CN.json"

# bytes 读取，避免 minified JS 里偶发的编码问题；提取后再 decode
pat_dm_id = re.compile(rb'defaultMessage:"((?:[^"\\]|\\.)*)"\s*,\s*id:"([^"]*)"')
pat_id_dm = re.compile(rb'id:"([^"]*)"\s*,\s*defaultMessage:"((?:[^"\\]|\\.)*)"')

pairs = {}
total_calls = 0
files = sorted(glob.glob(os.path.join(v1_dir, "*.js")))
for fp in files:
    with open(fp, "rb") as f:
        data = f.read()
    for m in pat_dm_id.finditer(data):
        dm = m.group(1).decode("utf-8", "replace")
        mid = m.group(2).decode("utf-8", "replace")
        pairs.setdefault(mid, set()).add(dm)
        total_calls += 1
    for m in pat_id_dm.finditer(data):
        mid = m.group(1).decode("utf-8", "replace")
        dm = m.group(2).decode("utf-8", "replace")
        pairs.setdefault(mid, set()).add(dm)
        total_calls += 1

def unescape(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s

zh = json.load(open(zh_path, encoding="utf-8"))

missing = {}
ambiguous = {}
for mid, dms in pairs.items():
    if mid not in zh:
        if len(dms) > 1:
            ambiguous[mid] = sorted(dms)
        else:
            missing[mid] = list(dms)[0]

print("JS 文件数:", len(files))
print("formatMessage 调用总数:", total_calls)
print("JS 中不同 id 数:", len(pairs))
print("zh-CN.json 现有条数:", len(zh))
print("缺失 id 数(未翻译):", len(missing))
print("  其中多个 defaultMessage 的 id:", len(ambiguous))
print("  纯缺失(单一 defaultMessage):", len(missing) - 0)

# 统计 defaultMessage 长度分布，看翻译量
lens = [len(unescape(v)) for v in missing.values()]
if lens:
    lens.sort()
    print("缺失条目英文长度: 最短%d / 中位%d / p90=%d / 最长%d" % (
        lens[0], lens[len(lens)//2], lens[int(len(lens)*0.9)], lens[-1]))
    total_chars = sum(lens)
    print("缺失英文总字符数:", total_chars)

print("\n=== 缺失样本(前 30) ===")
items = list(missing.items())
for i, (k, v) in enumerate(items[:30]):
    print(repr(k), "=>", repr(unescape(v)))

# 保存完整缺失列表到文件，供下一步翻译用
out = r"C:/Users/Admin/汉化/missing_keys.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump({k: unescape(v) for k, v in missing.items()}, f, ensure_ascii=False, indent=1)
print("\n完整缺失列表已存:", out)
