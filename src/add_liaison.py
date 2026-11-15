"""フォントに「連音化を発音どおりに表示する」OpenType機能を追加する。
例: 한국어 → 한구거、음악이 → 으마기、있어요 → 이써요、좋아 → 조아、많이 → 마니
仕組み: [パッチム X の字][ㅇ で始まる字] の並びを見つけたら、
        前の字からパッチムを外し（または一部を残し）、後ろの字の ㅇ を X に置き換える。
        重なった連鎖（음악이 など）に対応するため、同じ処理を2回かける。
使い方: python3 add_liaison.py 入力.ttf 出力.ttf
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

INITIALS = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
FINALS = [''] + list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

# パッチム → (前の字に残すパッチム, 後ろの字の新しい初声)。None は「後ろは ㅇ のまま」
MOVE = {
    'ㄱ': ('', 'ㄱ'), 'ㄲ': ('', 'ㄲ'), 'ㄳ': ('ㄱ', 'ㅆ'), 'ㄴ': ('', 'ㄴ'), 'ㄵ': ('ㄴ', 'ㅈ'),
    'ㄶ': ('', 'ㄴ'), 'ㄷ': ('', 'ㄷ'), 'ㄹ': ('', 'ㄹ'), 'ㄺ': ('ㄹ', 'ㄱ'), 'ㄻ': ('ㄹ', 'ㅁ'),
    'ㄼ': ('ㄹ', 'ㅂ'), 'ㄽ': ('ㄹ', 'ㅆ'), 'ㄾ': ('ㄹ', 'ㅌ'), 'ㄿ': ('ㄹ', 'ㅍ'), 'ㅀ': ('', 'ㄹ'),
    'ㅁ': ('', 'ㅁ'), 'ㅂ': ('', 'ㅂ'), 'ㅄ': ('ㅂ', 'ㅆ'), 'ㅅ': ('', 'ㅅ'), 'ㅆ': ('', 'ㅆ'),
    'ㅈ': ('', 'ㅈ'), 'ㅊ': ('', 'ㅊ'), 'ㅋ': ('', 'ㅋ'), 'ㅌ': ('', 'ㅌ'), 'ㅍ': ('', 'ㅍ'),
    'ㅎ': ('', None),   # 좋아 → 조아（ㅎ は消えるだけ）
}

def name(l, v, t): return f"uni{0xAC00 + (l * 21 + v) * 28 + t:04X}"


def build_fea():
    fea = []
    ieung = INITIALS.index('ㅇ')
    ieung_glyphs = [name(ieung, v, t) for v in range(21) for t in range(28)]
    fea.append(f"@IEUNG = [{' '.join(ieung_glyphs)}];")
    rules = []
    for fin, (keep, new_ini) in MOVE.items():
        ti = FINALS.index(fin)
        kt = FINALS.index(keep)
        src = [name(l, v, ti) for l in range(19) for v in range(21)]
        dst = [name(l, v, kt) for l in range(19) for v in range(21)]
        key = f"F{ti}"
        fea.append(f"@{key} = [{' '.join(src)}];")
        fea.append(f"lookup DROP_{key} {{ sub @{key} by [{' '.join(dst)}]; }} DROP_{key};")
        if new_ini is not None:
            ni = INITIALS.index(new_ini)
            to = [name(ni, v, t) for v in range(21) for t in range(28)]
            fea.append(f"lookup INI_{key} {{ sub @IEUNG by [{' '.join(to)}]; }} INI_{key};")
            rules.append(f"    sub @{key}' lookup DROP_{key} @IEUNG' lookup INI_{key};")
        else:
            rules.append(f"    sub @{key}' lookup DROP_{key} @IEUNG;")
    body = "\n".join(rules)
    fea.append(f"lookup LIAISON1 {{\n{body}\n}} LIAISON1;")
    fea.append(f"lookup LIAISON2 {{\n{body}\n}} LIAISON2;")
    for feat in ('ccmp', 'calt'):
        fea.append(f"feature {feat} {{\n  script hang; language dflt;\n  lookup LIAISON1;\n  lookup LIAISON2;\n"
                   f"  script DFLT; language dflt;\n  lookup LIAISON1;\n  lookup LIAISON2;\n}} {feat};")
    return "languagesystem DFLT dflt;\nlanguagesystem hang dflt;\n" + "\n".join(fea)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    f = TTFont(src)
    addOpenTypeFeaturesFromString(f, build_fea())
    f.save(dst)
    print('ok')
