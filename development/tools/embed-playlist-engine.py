"""Embed the exact tested engine and its MIT license in the injected binary."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
license_text=(root/'third_party/TwitchAdBlockHQ-LICENSE.txt').read_text()
source='/*\n'+license_text+'\n*/\n'+(root/'src/PlaylistEngine.js').read_text()
data=source.encode('utf-8')+b'\0'
output=root/'build/PlaylistEngine.inc'
output.parent.mkdir(exist_ok=True)
output.write_text('static const unsigned char TPPlaylistEngineScript[] = {\n'+
    '\n'.join(','.join(str(b) for b in data[i:i+120])+',' for i in range(0,len(data),120))+'\n};\n')
print('Embedded playlist engine and license:',len(data),'bytes')
