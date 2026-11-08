import argparse,copy,hashlib,struct,zipfile,plistlib
from pathlib import Path
LOAD_PATH=""
def sha(data):
    return hashlib.sha256(data).hexdigest()


def macho(data):
    if struct.unpack_from('<I', data)[0] != 0xfeedfacf:
        raise ValueError('Expected a thin little-endian 64-bit Mach-O')
    magic, cpu, subtype, filetype, ncmds, cmdsize, flags, reserved = struct.unpack_from('<8I', data)
    cursor = 32
    commands = []
    section_offsets = []
    for _ in range(ncmds):
        cmd, size = struct.unpack_from('<II', data, cursor)
        if size < 8 or cursor + size > 32 + cmdsize:
            raise ValueError('Invalid load command')
        entry = {'command': cmd, 'size': size, 'offset': cursor}
        if cmd in (0xc, 0x80000018, 0x8000001f, 0x80000023, 0xd):
            offset = struct.unpack_from('<I', data, cursor+8)[0]
            entry['path'] = data[cursor+offset:cursor+size].split(b'\0')[0].decode()
        if cmd == 0x19:
            count = struct.unpack_from('<I', data, cursor+64)[0]
            for i in range(count):
                pos = cursor+72+i*80
                offset = struct.unpack_from('<I', data, pos+48)[0]
                if offset:
                    section_offsets.append(offset)
        if cmd == 0x2c:
            entry['cryptid'] = struct.unpack_from('<I', data, cursor+16)[0]
        commands.append(entry)
        cursor += size
    if cursor != 32+cmdsize:
        raise ValueError('Load-command byte count mismatch')
    return {'cpu': cpu, 'filetype': filetype, 'ncmds': ncmds, 'sizeofcmds': cmdsize,
            'header_end': cursor, 'first_section': min(section_offsets), 'commands': commands}


def inject(data):
    metadata = macho(data)
    if metadata['cpu'] != 0x100000c:
        raise ValueError('Expected ARM64')
    if any(c.get('cryptid', 0) != 0 for c in metadata['commands']):
        raise ValueError('Encrypted executable cannot be patched')
    if any(c.get('path') == LOAD_PATH for c in metadata['commands']):
        raise ValueError('Library already injected')
    name = LOAD_PATH.encode() + b'\0'
    size = (24+len(name)+7) & ~7
    command = struct.pack('<6I', 0xc, size, 24, 0, 0x10000, 0x10000) + name
    command += bytes(size-len(command))
    start = metadata['header_end']
    if start+size > metadata['first_section'] or any(data[start:start+size]):
        raise ValueError('Insufficient zero-filled header padding; refusing to shift code')
    result = bytearray(data)
    struct.pack_into('<II', result, 16, metadata['ncmds']+1, metadata['sizeofcmds']+size)
    result[start:start+size] = command
    # The only changed bytes are the command counts and formerly unused padding.
    assert result[:16] == data[:16]
    assert result[24:start] == data[24:start]
    assert result[start+size:] == data[start+size:]
    patched = macho(result)
    assert sum(c.get('path') == LOAD_PATH for c in patched['commands']) == 1
    return bytes(result), metadata, patched



def main():
 global LOAD_PATH
 p=argparse.ArgumentParser();p.add_argument('--base',required=True,type=Path);p.add_argument('--libs',required=True,type=Path);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
 assert args.base.resolve()!=args.output.resolve(),'Input must not be overwritten'
 names=['NativeChat','ForcedFollow','NativeRewind']; additions={}
 for name in names:
  data=(args.libs/(name+'.dylib')).read_bytes();assert macho(data)['cpu']==0x100000c
  additions['Payload/Twitch.app/Frameworks/'+name+'.dylib']=data
 additions['Payload/Twitch.app/ForcedFollowLive.graphql']=(Path(__file__).resolve().parents[1]/'src/ForcedFollowLive.graphql').read_bytes()
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(args.base) as z:
  assert len(z.namelist())==len(set(z.namelist()))
  info=plistlib.loads(z.read('Payload/Twitch.app/Info.plist'));assert str(info.get('CFBundleShortVersionString','')).startswith('30.7')
  assert 'Payload/Twitch.app/Frameworks/TwitchAdBlock.dylib' in z.namelist()
  assert not set(additions).intersection(z.namelist()),'Use the original base, not an already patched app'
  binary=z.read('Payload/Twitch.app/Twitch')
  for name in names:
   LOAD_PATH='@executable_path/Frameworks/'+name+'.dylib';binary,_,_=inject(binary)
  old={}
  with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
   for entry in z.infolist():
    data=z.read(entry);old[entry.filename]=sha(data);out.writestr(copy.copy(entry),binary if entry.filename=='Payload/Twitch.app/Twitch' else data)
   for name,data in additions.items():
    entry=zipfile.ZipInfo(name);entry.create_system=3;entry.external_attr=(0o100755 if name.endswith('.dylib') else 0o100644)<<16;entry.compress_type=zipfile.ZIP_DEFLATED;out.writestr(entry,data)
 with zipfile.ZipFile(args.output) as z:
  assert z.testzip() is None
  for name,digest in old.items():
   if name!='Payload/Twitch.app/Twitch':assert sha(z.read(name))==digest,name
 print('Built unsigned IPA:',args.output)
if __name__=='__main__':main()
