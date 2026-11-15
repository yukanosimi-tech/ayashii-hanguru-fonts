#!/bin/sh
# フォントを全部作り直す。必要なもの: Python 3 と fontTools（pip install fonttools）
set -e
cd "$(dirname "$0")"
OUT=../fonts
IOS=../ios
mkdir -p "$OUT" "$IOS"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

K_EN="Nihonjin Kankokugo Kikiwakerarenai Mondai Font"
K_JA="日本人韓国語聞き分けられない問題フォント"

# 1. 日本の怪しい韓国語フォント
python3 make_font.py "$OUT/NihonNoAyashiiKankokugoFont.ttf"

# おまけ: なんで連音化するんやねんホンマ韓国語は難しいフォント（字母の入れ替え ＋ 連音化）
R_EN="Nande Renonka Surunyanen Honma Kankokugo Wa Muzukashii Font"
R_JA="なんで連音化するんやねんホンマ韓国語は難しいフォント"
python3 make_mimi.py "$TMP/base.ttf" "$R_EN" "$R_JA"
python3 add_liaison.py "$TMP/base.ttf" "$OUT/NandeRenonkaSurunyanenHonmaKankokugoWaMuzukashiiFont.ttf"

# 2. 日本人韓国語聞き分けられない問題フォント（字母の入れ替えだけ）
python3 make_mimi.py "$OUT/NihonjinKankokugoKikiwakerarenaiMondaiFont.ttf" "$K_EN" "$K_JA"

# iPhone / iPad 用
for f in NihonNoAyashiiKankokugoFont:"日本の怪しい韓国語フォント" \
         NandeRenonkaSurunyanenHonmaKankokugoWaMuzukashiiFont:"$R_JA" \
         NihonjinKankokugoKikiwakerarenaiMondaiFont:"$K_JA"; do
  file=${f%%:*}; name=${f#*:}
  python3 make_mobileconfig.py "$OUT/$file.ttf" "$name" "$IOS/$file.mobileconfig"
done
echo done
