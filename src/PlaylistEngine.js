// Derived from Twitch AdBlock HQ's createPlaylistLib, MIT licensed.
// Copyright (c) 2026 Nello. See third_party/TwitchAdBlockHQ-LICENSE.txt.
// Upstream: 9ab8e5c827c5ab5a09ee3d605989cc0b0787650b.
// Native adaptation preserves HLS KEY/MAP tags; host/browser integration omitted.
function createPlaylistLib() {
    function parseAttributes(text) {
        const attributes = {};
        const pattern = /([A-Z0-9-]+)=("[^"]*"|[^,]*)/g;
        let match;
        while ((match = pattern.exec(text)) !== null) {
            const value = match[2];
            attributes[match[1]] = value.startsWith('"') ? value.slice(1, -1) : value;
        }
        return attributes;
    }

    function codecFamily(codecs) {
        const value = String(codecs || '').toLowerCase();
        if (/(^|,)\s*(hev1|hvc1)/.test(value)) return 'hevc';
        if (/(^|,)\s*av01/.test(value)) return 'av1';
        if (/(^|,)\s*avc[13]/.test(value)) return 'avc';
        if (/mp4a/.test(value)) return 'audio';
        return value.split('.')[0] || 'unknown';
    }

    function nextUriIndex(lines, start) {
        for (let i = start; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            if (!line.startsWith('#')) return i;
            if (line.startsWith('#EXTINF') || line.startsWith('#EXT-X-STREAM-INF')) return -1;
        }
        return -1;
    }

    function describeVariant(attributes, url) {
        const size = String(attributes.RESOLUTION || '').split('x');
        const width = parseInt(size[0], 10) || 0;
        const height = parseInt(size[1], 10) || 0;
        const fps = attributes['FRAME-RATE'] ? Math.round(parseFloat(attributes['FRAME-RATE'])) : 0;
        const codec = codecFamily(attributes.CODECS);
        const group = attributes.VIDEO || '';
        return {
            url,
            width,
            height,
            fps,
            codec,
            codecs: attributes.CODECS || '',
            bandwidth: parseInt(attributes.BANDWIDTH, 10) || 0,
            group,
            key: height ? `${width}x${height}@${fps}/${codec}` : `audio/${group || codec}`,
            label: height ? `${height}p${fps >= 48 ? fps : ''}` : 'audio only',
        };
    }

    function parseMaster(text) {
        const lines = String(text).replace(/\r/g, '').split('\n');
        const variants = [];
        for (let i = 0; i < lines.length; i++) {
            if (!lines[i].startsWith('#EXT-X-STREAM-INF:')) continue;
            const uriIndex = nextUriIndex(lines, i + 1);
            if (uriIndex < 0) continue;
            variants.push(describeVariant(parseAttributes(lines[i].slice(18)), lines[uriIndex].trim()));
        }
        return variants;
    }

    function qualityScore(variant) {
        return variant.height * 1000 + variant.fps;
    }

    // Finds the variant of another session to use for `target`: the identical rendition if it exists, otherwise
    // the best rendition that doesn't exceed the target and uses the same codec (the player can't switch codecs).
    function matchVariant(variants, target) {
        const exact = variants.find((v) => v.key === target.key && (!target.bandwidth || v.bandwidth >= target.bandwidth * 0.9));
        if (exact) {
            return { variant: exact, exact: true };
        }
        let best = null;
        for (const variant of variants) {
            if (!variant.height || !target.height || variant.codec !== target.codec) continue;
            if (qualityScore(variant) > qualityScore(target)) continue;
            if (!best || qualityScore(variant) > qualityScore(best) || (qualityScore(variant) === qualityScore(best) && variant.bandwidth > best.bandwidth)) {
                best = variant;
            }
        }
        return best ? { variant: best, exact: false } : null;
    }

    // URL fragments of ad and placeholder segments, as observed in the field by TwitchAdSolutions.
    // Real segment URLs use a base64url token, so these slash-delimited fragments can't occur in them by chance.
    const AD_SEGMENT_URL_PATTERNS = ['/adsquared/', '/_404/', '/processing'];

    // twitch-stitched-ad, twitch-stitched-* variants, twitch-ad-quartile, twitch-maf-ad, ...
    function isAdDateRangeClass(className) {
        return /(^|-)ad(-|$)/.test(className) || className.includes('stitched');
    }

    function parseMedia(text, knownSequenceByUri) {
        const lines = String(text).replace(/\r/g, '').split('\n');
        const playlist = {
            mediaSequence: 0,
            liveSequence: null,
            targetDuration: 0,
            segments: [],
            prefetch: [],
            dateRanges: [],
            hasAdMarkers: false,
            endList: false,
        };
        let pdt = null;
        let mapLine = null, keyLine = null, byteRange = null, previousRangeURI = null, previousRangeEnd = 0;
        let discontinuity = false;
        let inCue = false; // Between SCTE-35 #EXT-X-CUE-OUT and #EXT-X-CUE-IN
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            if (line.startsWith('#EXTINF:')) {
                const uriIndex = nextUriIndex(lines, i + 1);
                if (uriIndex < 0) continue;
                const comma = line.indexOf(',');
                const durationText = comma < 0 ? line.slice(8) : line.slice(8, comma);
                const title = comma < 0 ? '' : line.slice(comma + 1);
                for (let tag = i + 1; tag < uriIndex; tag++) {
                    const value = lines[tag].trim();
                    if (value.startsWith('#EXT-X-BYTERANGE:')) byteRange = value.slice(17);
                    else if (value.startsWith('#EXT-X-KEY:')) keyLine = value;
                    else if (value.startsWith('#EXT-X-MAP:')) mapLine = value;
                }
                const uri = lines[uriIndex].trim();
                if (byteRange) {
                    const parts = byteRange.split('@');
                    const length = Number(parts[0]);
                    const offset = parts.length > 1 ? Number(parts[1]) : previousRangeURI === uri ? previousRangeEnd : NaN;
                    if (!Number.isFinite(offset) || !Number.isFinite(length) || length <= 0) playlist.unsupportedByteRange = true;
                    else { byteRange = length + '@' + offset; previousRangeURI = uri; previousRangeEnd = offset + length; }
                }
                const forcedAd = inCue || AD_SEGMENT_URL_PATTERNS.some((pattern) => uri.includes(pattern));
                const originalSequence = playlist.mediaSequence + playlist.segments.length;
                let segmentKey = keyLine;
                if (segmentKey) {
                    const keyAttributes = parseAttributes(segmentKey.slice(11));
                    if (keyAttributes.METHOD === 'AES-128' && !keyAttributes.IV)
                        segmentKey += ',IV=0x' + originalSequence.toString(16).padStart(32, '0');
                }
                playlist.segments.push({
                    seq: playlist.mediaSequence + playlist.segments.length,
                    duration: parseFloat(durationText) || 0,
                    durationText,
                    title,
                    live: title.startsWith('live') && !forcedAd,
                    forcedAd,
                    uri,
                    pdt, mapLine, keyLine: segmentKey, byteRange,
                    pdtMs: pdt ? Date.parse(pdt) : NaN,
                    discontinuity,
                    gseq: null,
                });
                pdt = null;
                byteRange = null;
                discontinuity = false;
                i = uriIndex;
            } else if (line.startsWith('#EXT-X-MAP:')) {
                mapLine = line;
            } else if (line.startsWith('#EXT-X-KEY:')) {
                keyLine = line;
            } else if (line.startsWith('#EXT-X-BYTERANGE:')) {
                byteRange = line.slice(17);
            } else if (line.startsWith('#EXT-X-CUE-OUT')) {
                inCue = true;
                playlist.hasAdMarkers = true;
            } else if (line.startsWith('#EXT-X-CUE-IN')) {
                inCue = false;
            } else if (line.startsWith('#EXT-X-PROGRAM-DATE-TIME:')) {
                pdt = line.slice(25);
            } else if (line === '#EXT-X-DISCONTINUITY') {
                discontinuity = true;
            } else if (line.startsWith('#EXT-X-MEDIA-SEQUENCE:')) {
                playlist.mediaSequence = parseInt(line.slice(22), 10) || 0;
            } else if (line.startsWith('#EXT-X-TWITCH-LIVE-SEQUENCE:')) {
                const value = parseInt(line.slice(28), 10);
                playlist.liveSequence = Number.isFinite(value) ? value : null;
            } else if (line.startsWith('#EXT-X-TARGETDURATION:')) {
                playlist.targetDuration = parseInt(line.slice(22), 10) || 0;
            } else if (line.startsWith('#EXT-X-DATERANGE:')) {
                const className = parseAttributes(line.slice(17)).CLASS || '';
                if (isAdDateRangeClass(className) || line.includes('X-TV-TWITCH-AD') || line.includes('SCTE35-OUT')) {
                    playlist.hasAdMarkers = true;
                }
                playlist.dateRanges.push({ line, className });
            } else if (line.startsWith('#EXT-X-TWITCH-PREFETCH:')) {
                playlist.prefetch.push(line.slice(23));
            } else if (line === '#EXT-X-ENDLIST') {
                playlist.endList = true;
            }
        }
        if (!playlist.hasAdMarkers && !playlist.segments.some((s) => s.title.startsWith('live'))) {
            // Unknown segment titles and no ad markers: don't mistake the stream for an ad.
            playlist.segments.forEach((s) => { s.live = !s.forcedAd; });
        }
        assignGlobalSequence(playlist, knownSequenceByUri);
        return playlist;
    }

    // Numbers live segments with the channel-wide sequence. Sessions that showed an ad restart MEDIA-SEQUENCE at 0,
    // but #EXT-X-TWITCH-LIVE-SEQUENCE always holds the channel-wide number of the first live segment.
    function assignGlobalSequence(playlist, knownSequenceByUri) {
        let previous = null;
        let gap = false;
        for (const segment of playlist.segments) {
            if (!segment.live) {
                gap = true;
                continue;
            }
            const memoKey = segment.uri + (segment.byteRange ? '#range=' + segment.byteRange : '');
            const known = knownSequenceByUri ? knownSequenceByUri.get(memoKey) : undefined;
            if (known !== undefined) {
                segment.gseq = known;
            } else if (!previous) {
                segment.gseq = playlist.liveSequence !== null ? playlist.liveSequence : segment.seq;
            } else if (!gap && !segment.discontinuity) {
                segment.gseq = previous.gseq + 1;
            } else {
                // Live segments on both sides of an ad: the ad occupies real time, so count the skipped segments.
                const stepMs = (previous.duration || playlist.targetDuration || 2) * 1000;
                const elapsedMs = segment.pdtMs - previous.pdtMs;
                segment.gseq = previous.gseq + (Number.isFinite(elapsedMs) ? Math.max(1, Math.round(elapsedMs / stepMs)) : 1);
            }
            if (previous && segment.gseq <= previous.gseq) {
                segment.gseq = previous.gseq + 1;
            }
            previous = segment;
            gap = false;
        }
    }

    function rememberSequence(knownSequenceByUri, playlist) {
        const current = new Set();
        for (const segment of playlist.segments) {
            if (segment.live && segment.gseq !== null) {
                const memoKey = segment.uri + (segment.byteRange ? '#range=' + segment.byteRange : '');
                knownSequenceByUri.set(memoKey, segment.gseq);
                current.add(memoKey);
            }
        }
        for (const uri of knownSequenceByUri.keys()) {
            if (knownSequenceByUri.size <= 64) break;
            if (!current.has(uri)) knownSequenceByUri.delete(uri);
        }
    }

    function hasAdSegments(playlist) {
        return playlist.segments.some((s) => !s.live);
    }

    function isShowingAd(playlist) {
        const last = playlist.segments[playlist.segments.length - 1];
        return last ? !last.live : playlist.hasAdMarkers;
    }

    function newestLiveSegment(playlist) {
        for (let i = playlist.segments.length - 1; i >= 0; i--) {
            if (playlist.segments[i].live) return playlist.segments[i];
        }
        return null;
    }

    // One timeline per variant playlist the player requests. `virtual` becomes true once the playlist is rewritten.
    function createTimeline() {
        return { segments: [], lastGseq: -1, pdtOffsets: {}, virtual: false, skipToLive: false, heldRefreshes: 0 };
    }

    // Sequence numbers shown to the player, shared by every variant of a stream so quality switches stay aligned.
    // They equal the channel-wide sequence until content is skipped (e.g. while holding during an ad); the gap is
    // then closed so the player sees contiguous numbers.
    function createSequenceState() {
        return { offset: 0, offsetSince: -1, lastGseq: -1, lastVseq: -1 };
    }

    // Adds live segments newer than the timeline's newest segment. Returns what changed.
    // After a gap only the newest `maxAfterGap` segments are added, so playback resumes close to live.
    function appendToTimeline(timeline, segments, variantKey, sourceId, sequence, maxAfterGap) {
        const result = { appended: 0, resumedAfterGap: false, switchedSource: false, changedRendition: false };
        let fresh = segments.filter((s) => s.live && s.gseq !== null && s.gseq > timeline.lastGseq
            && !(timeline.virtual && s.gseq < sequence.offsetSince)); // Older ones would reuse numbers from before a gap
        const newest = timeline.segments[timeline.segments.length - 1];
        if (maxAfterGap && newest && fresh.length > maxAfterGap && (fresh[0].gseq !== newest.gseq + 1 || timeline.skipToLive)) {
            fresh = fresh.slice(-maxAfterGap);
        }
        if (fresh.length) {
            timeline.skipToLive = false;
        }
        for (const segment of fresh) {
            if (timeline.virtual && sequence.lastGseq >= 0 && segment.gseq > sequence.lastGseq + 1) {
                sequence.offset = sequence.lastVseq + 1 - segment.gseq;
                sequence.offsetSince = segment.gseq;
            }
            const vseq = segment.gseq + sequence.offset;
            if (segment.gseq > sequence.lastGseq) {
                sequence.lastGseq = segment.gseq;
                sequence.lastVseq = vseq;
            }
            const previous = timeline.segments[timeline.segments.length - 1];
            const contiguous = !!previous && segment.gseq === previous.gseq + 1;
            const sameSource = !!previous && previous.sourceId === sourceId;
            const discontinuity = !!previous && (!contiguous || previous.variantKey !== variantKey || (sameSource && segment.discontinuity));
            if (previous && !contiguous) {
                result.resumedAfterGap = true;
            }
            if (previous && !sameSource) {
                result.switchedSource = true;
            }
            if (previous && previous.variantKey !== variantKey) {
                result.changedRendition = true;
            }
            // Sessions label the same segment with slightly different times; keep the timeline's clock continuous.
            let pdtMs = segment.pdtMs;
            if (Number.isFinite(pdtMs)) {
                if (previous && contiguous && !sameSource && Number.isFinite(previous.pdtMs)) {
                    timeline.pdtOffsets[sourceId] = previous.pdtMs + previous.duration * 1000 - segment.pdtMs;
                } else if (!contiguous) {
                    timeline.pdtOffsets[sourceId] = 0;
                }
                pdtMs += timeline.pdtOffsets[sourceId] || 0;
            }
            if (previous && vseq !== previous.vseq + 1) {
                // The player got the missing numbers from another variant. A playlist can't have holes, so start over.
                timeline.segments.length = 0;
            }
            timeline.segments.push({
                gseq: segment.gseq,
                vseq,
                duration: segment.duration,
                durationText: segment.durationText,
                uri: segment.uri,
                mapLine: segment.mapLine, keyLine: segment.keyLine, byteRange: segment.byteRange,
                pdtMs,
                discontinuity,
                discontinuityNumber: previous ? previous.discontinuityNumber + (discontinuity ? 1 : 0) : 0,
                variantKey,
                sourceId,
            });
            timeline.lastGseq = segment.gseq;
            result.appended++;
        }
        return result;
    }

    function trimTimeline(timeline, maxSegments) {
        if (timeline.segments.length > maxSegments) {
            timeline.segments.splice(0, timeline.segments.length - maxSegments);
        }
    }

    function renderTimeline(timeline, options) {
        const opts = options || {};
        const segments = timeline.segments;
        const first = segments[0];
        let targetDuration = opts.targetDuration || 0;
        for (const segment of segments) {
            targetDuration = Math.max(targetDuration, Math.ceil(segment.duration));
        }
        const version = segments.some(s => s.mapLine) ? 7 : segments.some(s => s.byteRange) ? 4 : 3;
        const lines = ['#EXTM3U', '#EXT-X-VERSION:' + version, `#EXT-X-TARGETDURATION:${targetDuration || 6}`];
        lines.push(`#EXT-X-MEDIA-SEQUENCE:${first ? first.vseq : Math.max(0, opts.nextSequence || 0)}`);
        if (first) {
            lines.push(`#EXT-X-TWITCH-LIVE-SEQUENCE:${first.vseq}`);
            const discontinuitySequence = first.discontinuityNumber - (first.discontinuity ? 1 : 0);
            lines.push(`#EXT-X-DISCONTINUITY-SEQUENCE:${Math.max(0, discontinuitySequence)}`);
        }
        for (const line of opts.headerLines || []) {
            lines.push(line);
        }
        let lastMap = null, lastKey = null;
        for (const segment of segments) {
            if (segment.discontinuity) lines.push('#EXT-X-DISCONTINUITY');
            if (segment.keyLine !== lastKey) {
                lines.push(segment.keyLine || '#EXT-X-KEY:METHOD=NONE'); lastKey = segment.keyLine;
            }
            if (segment.mapLine && segment.mapLine !== lastMap) { lines.push(segment.mapLine); lastMap = segment.mapLine; }
            if (Number.isFinite(segment.pdtMs)) lines.push(`#EXT-X-PROGRAM-DATE-TIME:${new Date(segment.pdtMs).toISOString()}`);
            lines.push(`#EXTINF:${segment.durationText},live`);
            if (segment.byteRange) lines.push('#EXT-X-BYTERANGE:' + segment.byteRange);
            lines.push(segment.uri);
        }
        for (const uri of opts.prefetch || []) {
            lines.push(`#EXT-X-TWITCH-PREFETCH:${uri}`);
        }
        if (opts.endList) lines.push('#EXT-X-ENDLIST');
        return lines.join('\n') + '\n';
    }

    return {
        parseAttributes,
        codecFamily,
        parseMaster,
        parseMedia,
        matchVariant,
        qualityScore,
        rememberSequence,
        hasAdSegments,
        isShowingAd,
        newestLiveSegment,
        createTimeline,
        createSequenceState,
        appendToTimeline,
        trimTimeline,
        renderTimeline,
    };
}

// Native bridge, authored for TwitchPlus. This module performs no I/O and has no
// browser or account access. The same code runs in JavaScriptCore and Node tests.
(function (root) {
    'use strict';
    const Lib = createPlaylistLib();
    const channels = new Map();
    function state(channel, key, attributes) {
        if (!channels.has(channel)) {
            if (channels.size >= 24) channels.clear();
            channels.set(channel, { sequence: Lib.createSequenceState(), entries: new Map() });
        }
        const channelState = channels.get(channel);
        if (!channelState.entries.has(key)) {
            if (channelState.entries.size >= 64) channelState.entries.clear();
            const target = Lib.parseMaster('#EXTM3U\n' + attributes + '\ntarget.m3u8\n')[0];
            if (!target) throw new Error('Missing video rendition');
            channelState.entries.set(key, { memo: new Map(), timeline: Lib.createTimeline(), target });
        }
        return { channelState, entry: channelState.entries.get(key) };
    }
    function inspect(channel, key, attributes, text) {
        const { entry } = state(channel, key, attributes);
        const playlist = Lib.parseMedia(text, entry.memo);
        return { needsBackup: Lib.isShowingAd(playlist),
            unsupported: !!playlist.unsupportedByteRange,
            hasLive: !!Lib.newestLiveSegment(playlist), markers: playlist.hasAdMarkers,
            hasAdSegments: Lib.hasAdSegments(playlist), virtual: entry.timeline.virtual };
    }
    function eligible(text) {
        const playlist = Lib.parseMedia(text);
        return !playlist.unsupportedByteRange && !!Lib.newestLiveSegment(playlist) && !Lib.isShowingAd(playlist);
    }
    function variant(master, attributes) {
        const target = Lib.parseMaster('#EXTM3U\n' + attributes + '\ntarget.m3u8\n')[0];
        const match = target && Lib.matchVariant(Lib.parseMaster(master), target);
        if (!match) return null;
        const v = match.variant;
        const attributesLine = '#EXT-X-STREAM-INF:BANDWIDTH=' + v.bandwidth + ',RESOLUTION=' + v.width + 'x' + v.height +
            ',CODECS="' + v.codecs + '",FRAME-RATE=' + v.fps;
        return { url: v.url, key: v.key, exact: match.exact, attributes: attributesLine };
    }
    function process(channel, key, attributes, text, raw, backupText, backupAttributes, sourceID) {
        const { channelState, entry } = state(channel, key, attributes);
        const { timeline, memo, target } = entry;
        const main = Lib.parseMedia(text, memo);
        Lib.rememberSequence(memo, main);
        const showingAd = Lib.isShowingAd(main);
        const clean = !main.hasAdMarkers && !Lib.hasAdSegments(main);
        const globallyNumbered = main.segments.length && main.segments[0].seq === main.segments[0].gseq;
        if (!timeline.virtual && clean && globallyNumbered && channelState.sequence.offset === 0) {
            Lib.appendToTimeline(timeline, main.segments, target.key, 'main', channelState.sequence);
            Lib.trimTimeline(timeline, 16);
            return { body: raw, rewritten: false, backup: false, ad: false };
        }
        let source = null;
        if (showingAd && backupText) {
            const backup = Lib.parseMedia(backupText);
            const backupTarget = Lib.parseMaster('#EXTM3U\n' + backupAttributes + '\nbackup.m3u8\n')[0];
            if (backupTarget && backupTarget.codec === target.codec && !Lib.isShowingAd(backup) && Lib.newestLiveSegment(backup)) {
                source = { playlist: backup, key: backupTarget.key, id: sourceID || 'backup' };
            }
        }
        if (!showingAd) source = { playlist: main, key: target.key, id: 'main' };
        if (!source && !timeline.segments.length) {
            // No fabricated media / zero-segment playlist: preserve the original
            // response if startup has no usable backup and no live history.
            return { body: raw, rewritten: false, backup: false, ad: showingAd, noSource: true };
        }
        timeline.virtual = true;
        if (source) Lib.appendToTimeline(timeline, source.playlist.segments, source.key, source.id, channelState.sequence, 3);
        Lib.trimTimeline(timeline, 16);
        const selected = source ? source.playlist : main;
        const body = Lib.renderTimeline(timeline, {
            targetDuration: main.targetDuration,
            nextSequence: channelState.sequence.lastVseq + 1,
            headerLines: selected.dateRanges.filter(d => d.className === 'timestamp' || d.className === 'twitch-session').map(d => d.line),
            // Omit low-latency prefetch/parts after a rewrite: only fully parsed
            // live segments may enter the player, including the very first poll.
            prefetch: [], endList: main.endList,
        });
        return { body, rewritten: true, backup: !!source && source.id !== 'main', ad: showingAd,
            held: !source, noSource: !source, segments: timeline.segments.length };
    }
    root.TPPlaylistEngine = { inspect, eligible, variant, process };
    if (typeof module !== 'undefined' && module.exports) module.exports = { createPlaylistLib, engine: root.TPPlaylistEngine };
})(typeof globalThis !== 'undefined' ? globalThis : this);
