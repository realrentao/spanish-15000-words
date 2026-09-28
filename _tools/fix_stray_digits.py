import json, re, asyncio, edge_tts, os, glob

# 各文件需修复的 ES 子串（用于定位），以及中文前缀规则
# 规则：去掉 ES 尾随 " NNN"，中文按 年/月份 自动补前缀
def fix_file(fn):
    raw = open(fn, encoding='utf-8').read()
    pre = 'window.BOOK_DATA=window.BOOK_DATA||{};'
    assert raw.startswith(pre), 'PREFIX MISSING in '+fn
    k = raw.index('=', raw.index('window.BOOK_DATA[')) + 1
    i = raw.index('{', k)
    obj = json.loads(raw[i:].rstrip().rstrip(';'))
    fixed = []
    for sec in obj['secs']:
        for kind in ('w', 's', 'e'):
            for row in sec.get(kind, []):
                if not isinstance(row, list) or len(row) < 2:
                    continue
                es = row[0]
                m = re.search(r' (\d+)\s*$', es)
                if not m:
                    continue
                num = m.group(1)
                new_es = es[:m.start()].rstrip()
                zh = row[1] if len(row) > 1 else ''
                if zh.startswith('年'):
                    new_zh = num + '年' + zh[1:]
                elif zh.startswith('月份'):
                    new_zh = num + '月份' + zh[2:]
                else:
                    new_zh = num + zh
                row[0] = new_es
                if len(row) > 1:
                    row[1] = new_zh
                fixed.append((sec['name'], kind, es, new_es, zh, new_zh, row[3], row[4]))
    if fixed:
        open(fn, 'w', encoding='utf-8').write(pre + 'window.BOOK_DATA[' + fn.split('sec/')[1].split('.js')[0] + ']=' + json.dumps(obj, ensure_ascii=False) + ';')
    return fixed

jobs = []  # (es_text, zh_text, es_file, zh_file)
for fn in ['data/sec/4.js', 'data/sec/16.js', 'data/sec/36.js']:
    fixed = fix_file(fn)
    for f in fixed:
        print('FILE', fn, '|', f[0], '|', f[1])
        print('  ES:', repr(f[2]), '->', repr(f[3]))
        print('  ZH:', repr(f[4]), '->', repr(f[5]))
        print('  audio:', f[6], f[7])
        jobs.append((f[3], f[5], 'audio/' + f[6], 'audio/' + f[7]))

async def gen(text, voice, out):
    await edge_tts.Communicate(text, voice).save(out)
    print('OK audio', out, os.path.getsize(out), 'bytes')

async def main():
    for es, zh, ef, zf in jobs:
        await gen(es, 'es-ES-ElviraNeural', ef)
        await gen(zh, 'zh-CN-XiaoxiaoNeural', zf)

asyncio.run(main())
print('ALL DONE, jobs:', len(jobs))
