"""フォントを iPhone / iPad 用の構成プロファイル（.mobileconfig）に包む
使い方: python3 make_mobileconfig.py フォント.ttf "表示名" 出力.mobileconfig
"""
import plistlib, sys, uuid, os

ttf, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
ident = 'io.github.yukanosimi-tech.' + os.path.splitext(os.path.basename(ttf))[0].lower()
pl = {
    'PayloadContent': [{
        'PayloadType': 'com.apple.font', 'PayloadVersion': 1,
        'PayloadIdentifier': ident + '.font', 'PayloadUUID': str(uuid.uuid5(uuid.NAMESPACE_URL, ident + '.font')).upper(),
        'PayloadDisplayName': name, 'Name': os.path.basename(ttf), 'Font': open(ttf, 'rb').read()}],
    'PayloadType': 'Configuration', 'PayloadVersion': 1,
    'PayloadIdentifier': ident, 'PayloadUUID': str(uuid.uuid5(uuid.NAMESPACE_URL, ident)).upper(),
    'PayloadDisplayName': name,
    'PayloadDescription': name + ' をインストールします。',
}
with open(out, 'wb') as f:
    plistlib.dump(pl, f)
