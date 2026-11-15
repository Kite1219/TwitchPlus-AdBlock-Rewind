'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {engine,createPlaylistLib}=require('../src/PlaylistEngine.js');
const Lib=createPlaylistLib();
const full='#EXT-X-STREAM-INF:BANDWIDTH=6000000,RESOLUTION=1920x1080,CODECS="avc1.64002A,mp4a.40.2",FRAME-RATE=60';
const low='#EXT-X-STREAM-INF:BANDWIDTH=600000,RESOLUTION=640x360,CODECS="avc1.4D401E,mp4a.40.2",FRAME-RATE=30';
function live(first,count=4,extra='') {
    let text=`#EXTM3U\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:${first}\n#EXT-X-TWITCH-LIVE-SEQUENCE:${first}\n${extra}`;
    for(let i=0;i<count;i++) text+=`#EXTINF:2.000,live\nhttps://video.ttvnw.net/live-${first+i}.ts\n`;
    return text;
}
const ads='#EXTM3U\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:0\n#EXT-X-DATERANGE:ID="pod",CLASS="twitch-stitched-ad",DURATION=30\n#EXTINF:2.000,Amazon|123\nhttps://video.ttvnw.net/adsquared/ad.ts\n';
function process(channel,main,backup='',backupAttrs=full,source='backup') {
    return engine.process(channel,'main-url',full,main,main,backup,backupAttrs,source);
}

test('clean response passes through byte-for-byte while timeline is tracked',()=>{
    const input=live(100);const result=process('clean',input);
    assert.equal(result.body,input);assert.equal(result.rewritten,false);
});
test('a fresh preroll can use real live backup segments without forwarding ad media',()=>{
    assert.equal(engine.inspect('preroll','main-url',full,ads).needsBackup,true);
    const result=process('preroll',ads,live(200));
    assert.equal(result.backup,true);assert.ok(!result.body.includes('adsquared'));
    assert.ok(!result.body.includes('Amazon|'));assert.ok(result.body.includes('live-203.ts'));
});
test('announced ads whose actual segments stay live do not require a backup',()=>{
    const input=live(300,4,'#EXT-X-DATERANGE:ID="notice",CLASS="twitch-stitched-ad"\n');
    const inspection=engine.inspect('announced','main-url',full,input);
    assert.equal(inspection.needsBackup,false);
    const result=process('announced',input);
    assert.equal(result.backup,false);assert.ok(!result.body.includes('twitch-stitched'));
    assert.ok(result.body.includes('live-303.ts'));
});
test('ad switch and return keep contiguous numbers across session-relative numbering',()=>{
    process('sequence',live(100));
    const switched=process('sequence',ads,live(104));
    const sequence=Lib.parseMedia(switched.body).segments.map(s=>s.seq);
    assert.deepEqual(sequence,[100,101,102,103,104,105,106,107]);
    const after=live(108).replace('#EXT-X-MEDIA-SEQUENCE:108','#EXT-X-MEDIA-SEQUENCE:14');
    const returned=process('sequence',after);
    assert.equal(returned.backup,false);
    const all=Lib.parseMedia(returned.body).segments.map(s=>s.seq);
    assert.deepEqual(all,[100,101,102,103,104,105,106,107,108,109,110,111]);
    assert.ok(!returned.body.includes('#EXT-X-MEDIA-SEQUENCE:14\n'));
});
test('360p fallback signals rendition discontinuity and returns to full quality',()=>{
    process('lowres',live(400));
    const fallback=process('lowres',ads,live(404),low);
    assert.ok(fallback.body.includes('#EXT-X-DISCONTINUITY\n'));
    const restored=process('lowres',live(408));
    assert.equal(restored.backup,false);assert.ok(restored.body.includes('live-411.ts'));
});
test('a wrong-codec backup cannot be mixed into the decoder timeline',()=>{
    process('codec',live(500));
    const wrong=full.replace('avc1.64002A','hvc1.1.6.L150');
    const result=process('codec',ads,live(504),wrong);
    assert.equal(result.held,true);assert.ok(!result.body.includes('live-504.ts'));
    assert.ok(!result.body.includes('adsquared'));
});
test('failure with live history holds real frames and can recover later',()=>{
    process('hold',live(600));
    const held=process('hold',ads);
    assert.equal(held.held,true);assert.ok(held.body.includes('live-603.ts'));
    assert.ok(!held.body.includes('adsquared'));
    const recovered=process('hold',ads,live(620));
    assert.equal(recovered.backup,true);assert.ok(recovered.body.includes('live-623.ts'));
    const seq=Lib.parseMedia(recovered.body).segments.map(s=>s.seq);
    assert.ok(seq.every((n,i)=>i===0 || n===seq[i-1]+1));
});
test('failure at startup does not fabricate media or return an empty live playlist',()=>{
    const result=process('no-source',ads);
    assert.equal(result.noSource,true);assert.equal(result.body,ads);
});
test('rewritten responses drop prefetch hints that could carry ad media',()=>{
    const result=process('prefetch',ads,live(700)+'#EXT-X-TWITCH-PREFETCH:https://video.ttvnw.net/adsquared/next.ts\n');
    assert.ok(!result.body.includes('PREFETCH'));assert.ok(!result.body.includes('adsquared'));
});
test('stale ad tags do not disqualify a live backup',()=>{
    assert.equal(engine.eligible(live(800,4,'#EXT-X-DATERANGE:ID="old",CLASS="twitch-stitched-ad"\n')),true);
    assert.equal(engine.eligible(ads),false);
});
test('master matching preserves codec and chooses the closest lower rendition',()=>{
    const master='#EXTM3U\n'+low+'\nhttps://video.ttvnw.net/360.m3u8\n';
    const chosen=engine.variant(master,full);
    assert.equal(chosen.key,'640x360@30/avc');assert.equal(chosen.exact,false);
    assert.equal(engine.variant(master,full.replace('avc1.64002A','hvc1.1.6.L150')),null);
});
test('fMP4 map and encryption key survive filtering and source changes',()=>{
    const first=live(900,4,'#EXT-X-MAP:URI="https://video.ttvnw.net/init-a.mp4"\n#EXT-X-KEY:METHOD=AES-128,URI="https://video.ttvnw.net/key-a"\n');
    process('maps',first);
    const backup=live(904,4,'#EXT-X-MAP:URI="https://video.ttvnw.net/init-b.mp4"\n#EXT-X-KEY:METHOD=AES-128,URI="https://video.ttvnw.net/key-b"\n');
    const result=process('maps',ads,backup);
    assert.ok(result.body.includes('#EXT-X-VERSION:7'));
    assert.ok(result.body.includes('init-a.mp4'));assert.ok(result.body.includes('init-b.mp4'));
    assert.ok(result.body.includes('key-a'));assert.ok(result.body.includes('key-b'));
});
test('separate playback sessions never reuse another session virtual sequence',()=>{
    process('session-a',live(1000));process('session-a',ads,live(1004));
    const fresh=process('session-b',live(10));
    assert.equal(fresh.body,live(10));assert.ok(!fresh.body.includes('live-1000'));
});
test('byte ranges are made explicit and retained when rebuilding a live playlist',()=>{
    const body='#EXTM3U\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:1200\n#EXT-X-TWITCH-LIVE-SEQUENCE:1200\n'+
        '#EXT-X-DATERANGE:ID="old",CLASS="twitch-stitched-ad"\n'+
        '#EXTINF:2,live\n#EXT-X-BYTERANGE:1000@0\nhttps://video.ttvnw.net/media.mp4\n'+
        '#EXTINF:2,live\n#EXT-X-BYTERANGE:1000\nhttps://video.ttvnw.net/media.mp4\n';
    const result=process('ranges',body);
    assert.ok(result.body.includes('#EXT-X-BYTERANGE:1000@0'));
    assert.ok(result.body.includes('#EXT-X-BYTERANGE:1000@1000'));
    assert.ok(result.body.includes('#EXT-X-VERSION:4'));
});
test('an undefined initial byte range is bypassed instead of inventing an offset',()=>{
    const body=live(1300).replace('#EXTINF:2.000,live','#EXTINF:2.000,live\n#EXT-X-BYTERANGE:1000');
    assert.equal(engine.inspect('bad-range','main-url',full,body).unsupported,true);
    assert.equal(engine.eligible(body),false);
});
