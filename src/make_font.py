"""わざと「日本の看板っぽい」ハングルフォントを組み合わせ方式で生成する試作スクリプト。
ルール:
  - 字母ごとにパーツは1種類だけ。置き場所の枠に合わせて引き伸ばすだけ
  - 字はマスの7割程度、等幅、字間広め
  - 各パーツは枠の中央に単純配置（重心調整なし）
  - 線は均一太さ・端は四角（日本のゴシック風）、ㅅ は「人」型、ㅇ は正円
"""
import math
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM = 1000
VERSION = "0.1"
COPYRIGHT = "Copyright 2026 yukanosimi-tech"
ADV = 1000
STROKE = 56                       # 線の太さ（均一）
BOX = (150, -70, 850, 630)       # 字を置く範囲（マスの7割）
GAP = 0.06                        # パーツ枠の内側余白（割合）

# ---------- 字母の形（単位正方形 0..1、y は上向き） ----------
# 'L': 折れ線, 'C': 正円 (cx, cy, r)
def L(*pts): return ('L', pts)
def C(cx, cy, r): return ('C', (cx, cy, r))

CONS = {
    'ㄱ': [L((0, 1), (1, 1), (1, 0))],
    'ㄴ': [L((0, 1), (0, 0), (1, 0))],
    'ㄷ': [L((1, 1), (0, 1), (0, 0), (1, 0))],
    'ㄹ': [L((0, 1), (1, 1), (1, .5), (0, .5), (0, 0), (1, 0))],
    'ㅁ': [L((0, 1), (1, 1), (1, 0), (0, 0), (0, 1))],
    'ㅂ': [L((0, 1), (0, 0), (1, 0), (1, 1)), L((0, .5), (1, .5))],
    'ㅅ': [L((.5, 1), (0, 0)), L((.42, .62), (1, 0))],            # 「人」っぽく
    'ㅇ': [C(.5, .5, .5)],
    'ㅈ': [L((0, 1), (1, 1)), L((.5, 1), (0, 0)), L((.42, .55), (1, 0))],
    'ㅊ': [L((.5, 1), (.5, .86)), L((0, .8), (1, .8)), L((.5, .8), (0, 0)), L((.42, .42), (1, 0))],
    'ㅋ': [L((0, 1), (1, 1), (1, 0)), L((0, .5), (1, .5))],
    'ㅌ': [L((1, 1), (0, 1), (0, 0), (1, 0)), L((0, .5), (1, .5))],
    'ㅍ': [L((0, 1), (1, 1)), L((0, 0), (1, 0)), L((.3, 1), (.3, 0)), L((.7, 1), (.7, 0))],
    'ㅎ': [L((.5, 1), (.5, .86)), L((.05, .74), (.95, .74)), C(.5, .3, .3)],
}
DOUBLE = {'ㄲ': 'ㄱㄱ', 'ㄸ': 'ㄷㄷ', 'ㅃ': 'ㅂㅂ', 'ㅆ': 'ㅅㅅ', 'ㅉ': 'ㅈㅈ',
          'ㄳ': 'ㄱㅅ', 'ㄵ': 'ㄴㅈ', 'ㄶ': 'ㄴㅎ', 'ㄺ': 'ㄹㄱ', 'ㄻ': 'ㄹㅁ',
          'ㄼ': 'ㄹㅂ', 'ㄽ': 'ㄹㅅ', 'ㄾ': 'ㄹㅌ', 'ㄿ': 'ㄹㅍ', 'ㅀ': 'ㄹㅎ', 'ㅄ': 'ㅂㅅ'}

def vbar(x): return L((x, 1), (x, 0))
VOW_V = {   # 縦長の母音（子音の右に置く）
    'ㅣ': [vbar(.5)],
    'ㅏ': [vbar(.35), L((.35, .5), (.8, .5))],
    'ㅑ': [vbar(.35), L((.35, .63), (.8, .63)), L((.35, .37), (.8, .37))],
    'ㅓ': [vbar(.65), L((.2, .5), (.65, .5))],
    'ㅕ': [vbar(.65), L((.2, .63), (.65, .63)), L((.2, .37), (.65, .37))],
    'ㅐ': [vbar(.3), vbar(.85), L((.3, .5), (.85, .5))],
    'ㅒ': [vbar(.3), vbar(.85), L((.3, .63), (.85, .63)), L((.3, .37), (.85, .37))],
    'ㅔ': [vbar(.5), vbar(.9), L((.05, .5), (.5, .5))],
    'ㅖ': [vbar(.5), vbar(.9), L((.05, .63), (.5, .63)), L((.05, .37), (.5, .37))],
}
VOW_H = {   # 横長の母音（子音の下に置く）
    'ㅡ': [L((0, .5), (1, .5))],
    'ㅗ': [L((0, .3), (1, .3)), L((.5, .3), (.5, .8))],
    'ㅛ': [L((0, .3), (1, .3)), L((.33, .3), (.33, .8)), L((.67, .3), (.67, .8))],
    'ㅜ': [L((0, .7), (1, .7)), L((.5, .7), (.5, .2))],
    'ㅠ': [L((0, .7), (1, .7)), L((.33, .7), (.33, .2)), L((.67, .7), (.67, .2))],
}
VOW_MIX = {'ㅘ': 'ㅗㅏ', 'ㅙ': 'ㅗㅐ', 'ㅚ': 'ㅗㅣ', 'ㅝ': 'ㅜㅓ', 'ㅞ': 'ㅜㅔ', 'ㅟ': 'ㅜㅣ', 'ㅢ': 'ㅡㅣ'}

INITIALS = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
VOWELS = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
FINALS = [''] + list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')


# ---------- 描画 ----------
class Glyph:
    def __init__(self):
        self.contours = []

    def poly(self, pts):
        # TrueType は時計回りが外側。符号付き面積で向きをそろえる
        a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                for i in range(len(pts)))
        if a > 0:
            pts = pts[::-1]
        self.contours.append(pts)

    def segment(self, p, q):
        (x1, y1), (x2, y2) = p, q
        d = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        h = STROKE / 2
        x1, y1, x2, y2 = x1 - ux * h, y1 - uy * h, x2 + ux * h, y2 + uy * h   # 四角い端
        nx, ny = -uy * h, ux * h
        self.poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)])

    def ring(self, cx, cy, r, n=64):
        ro, ri = r + STROKE / 2, max(r - STROKE / 2, 1)
        outer = [(cx + ro * math.cos(2 * math.pi * k / n), cy + ro * math.sin(2 * math.pi * k / n)) for k in range(n)]
        inner = [(cx + ri * math.cos(2 * math.pi * k / n), cy + ri * math.sin(2 * math.pi * k / n)) for k in range(n)]
        self.poly(outer)
        self.contours.append(inner[::-1] if _area(inner) < 0 else inner)   # 内側は逆向き

    def to_tt(self):
        pen = TTGlyphPen(None)
        for c in self.contours:
            pen.moveTo(_r(c[0]))
            for p in c[1:]:
                pen.lineTo(_r(p))
            pen.closePath()
        g = pen.glyph()
        if g.numberOfContours > 0:
            g.flags[0] |= 0x40          # OVERLAP_SIMPLE（重なり輪郭をMacでもきれいに）
        return g


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))

def _r(p): return (round(p[0]), round(p[1]))


def draw_shape(g, strokes, box):
    """単位正方形の字母を枠 box=(x0,y0,x1,y1) に引き伸ばして描く（線の太さは均一のまま）"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    px, py = w * GAP + STROKE / 2, h * GAP + STROKE / 2
    x0, y0, w, h = x0 + px, y0 + py, max(w - 2 * px, 1), max(h - 2 * py, 1)
    tf = lambda p: (x0 + p[0] * w, y0 + p[1] * h)
    for kind, data in strokes:
        if kind == 'L':
            pts = [tf(p) for p in data]
            for a, b in zip(pts, pts[1:]):
                g.segment(a, b)
        else:
            cx, cy, r = data
            # 正円にこだわる：枠が縦長でも横長でも、短い辺に合わせた真ん丸
            rr = r * min(w, h)
            g.ring(*tf((cx, cy)), rr)


def draw_cons(g, c, box):
    if c in DOUBLE:   # 二重子音・二重パッチムは枠を左右に割って並べるだけ
        x0, y0, x1, y1 = box
        m = (x0 + x1) / 2
        draw_cons(g, DOUBLE[c][0], (x0, y0, m, y1))
        draw_cons(g, DOUBLE[c][1], (m, y0, x1, y1))
    else:
        draw_shape(g, CONS[c], box)


def sub(box, fx0, fy0, fx1, fy1):
    x0, y0, x1, y1 = box
    return (x0 + (x1 - x0) * fx0, y0 + (y1 - y0) * fy0, x0 + (x1 - x0) * fx1, y0 + (y1 - y0) * fy1)


def syllable(ini, vow, fin):
    g = Glyph()
    B = BOX
    if vow in VOW_V:
        if fin:
            draw_cons(g, ini, sub(B, 0, .42, .6, 1)); draw_shape(g, VOW_V[vow], sub(B, .6, .42, 1, 1))
            draw_cons(g, fin, sub(B, .1, 0, .9, .4))
        else:
            draw_cons(g, ini, sub(B, 0, .1, .6, .9)); draw_shape(g, VOW_V[vow], sub(B, .6, 0, 1, 1))
    elif vow in VOW_H:
        if fin:
            draw_cons(g, ini, sub(B, .15, .66, .85, 1)); draw_shape(g, VOW_H[vow], sub(B, 0, .36, 1, .66))
            draw_cons(g, fin, sub(B, .15, 0, .85, .36))
        else:
            draw_cons(g, ini, sub(B, .15, .45, .85, 1)); draw_shape(g, VOW_H[vow], sub(B, 0, 0, 1, .45))
    else:
        h, v = VOW_MIX[vow]
        if fin:
            draw_cons(g, ini, sub(B, .1, .66, .6, 1)); draw_shape(g, VOW_H[h], sub(B, 0, .4, .7, .66))
            draw_shape(g, VOW_V[v], sub(B, .7, .4, 1, 1)); draw_cons(g, fin, sub(B, .1, 0, .9, .36))
        else:
            draw_cons(g, ini, sub(B, .1, .45, .6, 1)); draw_shape(g, VOW_H[h], sub(B, 0, 0, .7, .45))
            draw_shape(g, VOW_V[v], sub(B, .7, 0, 1, 1))
    return g


def single_jamo(j):
    g = Glyph()
    box = sub(BOX, .15, .1, .85, .9)
    if j in VOW_V: draw_shape(g, VOW_V[j], sub(BOX, .3, 0, .7, 1))
    elif j in VOW_H: draw_shape(g, VOW_H[j], sub(BOX, 0, .2, 1, .8))
    elif j in VOW_MIX:
        h, v = VOW_MIX[j]
        draw_shape(g, VOW_H[h], sub(BOX, 0, .1, .65, .6)); draw_shape(g, VOW_V[v], sub(BOX, .65, 0, 1, 1))
    else: draw_cons(g, j, box)
    return g


def build(path, family="Nihon No Ayashii Kankokugo Font", ja_family="日本の怪しい韓国語フォント"):
    order, cmap, glyphs, metrics = ['.notdef', 'space'], {0x20: 'space', 0x3000: 'space'}, {}, {}
    glyphs['.notdef'] = Glyph().to_tt(); glyphs['space'] = Glyph().to_tt()
    metrics['.notdef'] = (ADV, 0); metrics['space'] = (ADV // 2, 0)
    cmap[0x3000] = 'space'

    def add(cp, g):
        name = f"uni{cp:04X}"
        tt = g.to_tt()
        order.append(name); cmap[cp] = name; glyphs[name] = tt
        lsb = getattr(tt, 'xMin', 0) if tt.numberOfContours else 0
        metrics[name] = (ADV, lsb)

    for li, ini in enumerate(INITIALS):
        for vi, vow in enumerate(VOWELS):
            for ti, fin in enumerate(FINALS):
                add(0xAC00 + (li * 21 + vi) * 28 + ti, syllable(ini, vow, fin))
    compat = 'ㄱㄲㄳㄴㄵㄶㄷㄸㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅃㅄㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ' + VOWELS
    for i, j in enumerate(compat):
        add(0x3131 + i, single_jamo(j))

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    for n in order:   # glyf 計算後の正しい lsb を入れる
        g = fb.font['glyf'][n]
        g.recalcBounds(fb.font['glyf'])
        metrics[n] = (metrics[n][0], getattr(g, 'xMin', 0) if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=880, descent=-200)
    fb.setupNameTable({"familyName": family, "styleName": "Regular",
                       "uniqueFontIdentifier": family + " Regular " + VERSION,
                       "fullName": family + " Regular", "psName": family.replace(' ', '') + "-Regular",
                       "version": "Version " + VERSION,
                       "copyright": COPYRIGHT,
                       "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
                       "licenseInfoURL": "https://openfontlicense.org"})
    if ja_family:   # 日本語環境ではフォント一覧に日本語名を出す
        nm = fb.font['name']
        nm.setName(ja_family, 1, 3, 1, 0x411)
        nm.setName(ja_family, 4, 3, 1, 0x411)
        nm.setName("Regular", 2, 3, 1, 0x411)
    fb.setupOS2(fsType=0, sTypoAscender=880, sTypoDescender=-200, sTypoLineGap=0,
                usWinAscent=920, usWinDescent=240, ulCodePageRange1=(1 << 19))
    fb.setupPost()
    fb.font['OS/2'].ulUnicodeRange1 = (1 << 28)   # Hangul Jamo
    fb.font['OS/2'].ulUnicodeRange2 = (1 << (56 - 32))  # Hangul Syllables
    fb.save(path)


if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else 'NihonNoAyashiiKankokugoFont.ttf')
    print('ok')
