"""日本人韓国語聞き分けられない問題フォント：日本の看板風 ＋ 日本人が聞き分けにくい字母を字ごとにランダムで入れ替え"""
import random
import make_font as mf

INI_G = ['ㄱㅋㄲ', 'ㄷㅌㄸ', 'ㅂㅍㅃ', 'ㅈㅊㅉ', 'ㅅㅆ']
VOW_G = ['ㅗㅓ', 'ㅛㅕ', 'ㅜㅡ', 'ㅔㅐ', 'ㅖㅒ', 'ㅞㅙㅚ']
FIN_G = [['ㄴ', 'ㅇ'], ['ㄱ', 'ㅋ', 'ㄲ'], ['ㄷ', 'ㅌ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅎ']]

def pick(j, groups, rng):
    for g in groups:
        if j in g:
            return rng.choice(list(g))
    return j

_orig = mf.syllable

def syllable(ini, vow, fin):
    li, vi, ti = mf.INITIALS.index(ini), mf.VOWELS.index(vow), mf.FINALS.index(fin)
    rng = random.Random(0xAC00 + (li * 21 + vi) * 28 + ti)
    ini = pick(ini, INI_G, rng)
    vow = pick(vow, VOW_G, rng)
    if fin:
        fin = pick(fin, FIN_G, rng)
    return _orig(ini, vow, fin)

mf.syllable = syllable

if __name__ == '__main__':
    import sys
    # 使い方: python3 make_mimi.py 出力.ttf [英語名] [日本語名]
    mf.build(sys.argv[1] if len(sys.argv) > 1 else 'NihonjinKankokugoKikiwakerarenaiMondaiFont.ttf',
             family=sys.argv[2] if len(sys.argv) > 2 else "Nihonjin Kankokugo Kikiwakerarenai Mondai Font",
             ja_family=sys.argv[3] if len(sys.argv) > 3 else "日本人韓国語聞き分けられない問題フォント")
