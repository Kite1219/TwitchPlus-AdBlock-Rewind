#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/embed-playlist-engine.py
app="$PWD/build/LayoutFixture.app"
mkdir -p "$app"
python3 - "$app" <<'PY'
import pathlib,plistlib,sys
p=pathlib.Path(sys.argv[1])/'Info.plist'
p.write_bytes(plistlib.dumps({'CFBundleIdentifier':'com.twitchplus.layoutfixture',
 'CFBundleName':'LayoutFixture','CFBundleExecutable':'LayoutFixture','CFBundlePackageType':'APPL',
 'CFBundleVersion':'1','CFBundleShortVersionString':'1.0','MinimumOSVersion':'16.4',
 'LSRequiresIPhoneOS':True,'UIDeviceFamily':[1],'UILaunchScreen':{}}))
PY
xcrun --sdk iphonesimulator clang -target "$(uname -m)-apple-ios16.4-simulator" \
  -isysroot "$(xcrun --sdk iphonesimulator --show-sdk-path)" \
  -DTP_USE_APPLE_SDK -fobjc-arc -fblocks -Os -Wall -Wextra \
  -Wno-unused-function -Wno-unguarded-availability-new -Wno-deprecated-declarations \
  -framework Foundation -framework UIKit -framework JavaScriptCore \
  tests/LayoutFixture.m src/TwitchPlusCore.c -o "$app/LayoutFixture"
codesign --force --sign - "$app"
python3 - "$app" <<'PY'
import json,pathlib,subprocess,sys
def run(*args,**kw): return subprocess.run(args,check=True,text=True,**kw)
def output(*args): return subprocess.check_output(args,text=True)
devices=json.loads(output('xcrun','simctl','list','devices','available','--json'))['devices']
choices=[d for runtime,ds in sorted(devices.items(),reverse=True) if '.iOS-' in runtime
         for d in ds if d.get('isAvailable') and d['name'].startswith('iPhone')]
if not choices: raise SystemExit('No available iPhone simulator runtime')
device=next((d for d in choices if d['state']=='Booted'),choices[0])
udid=device['udid']
if device['state']!='Booted': run('xcrun','simctl','boot',udid)
run('xcrun','simctl','bootstatus',udid,'-b',timeout=240)
run('xcrun','simctl','install',udid,sys.argv[1],timeout=120)
launch=subprocess.run(['xcrun','simctl','launch','--console','--terminate-running-process',udid,
                      'com.twitchplus.layoutfixture'],text=True,timeout=120)
container=output('xcrun','simctl','get_app_container',udid,'com.twitchplus.layoutfixture','data').strip()
report=json.loads((pathlib.Path(container)/'Documents/layout-fixture.json').read_text())
report['simulator']=device['name']
pathlib.Path('build/layout-fixture.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not report.get('passed'): raise SystemExit('UIKit layout fixture failed')
PY
