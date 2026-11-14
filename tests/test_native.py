import ctypes as C,unittest,json,urllib.parse
from pathlib import Path
P=C.c_void_p;Z=C.c_size_t;D=C.c_double
F1=C.CFUNCTYPE(P,P);F2=C.CFUNCTYPE(P,P,P);F5=C.CFUNCTYPE(P,P,P,P,P,P);FS=C.CFUNCTYPE(None,P,P,P,Z);FD=C.CFUNCTYPE(None,P,P,P);FG=C.CFUNCTYPE(D,P,P);FM=C.CFUNCTYPE(P,P,P,D)
dll=C.CDLL(str(Path(__file__).with_name('NativeRewind-test.dll').resolve()))
dll.test_hook.argtypes=[Z,P]
for n in ['test_state','test_row']:getattr(dll,n).argtypes=[P,P]
for n in ['test_live','test_rewind','test_forward','test_apply','test_login','test_getstate']:getattr(dll,n).argtypes=[P]
for n in ['test_login','test_getstate']:getattr(dll,n).restype=P
dll.test_load.argtypes=[P,P,P]
dll.test_update.argtypes=[P]
dll.test_auto.restype=C.c_bool
dll.test_save_auto.argtypes=[C.c_bool]
dll.test_settings_load.argtypes=[P]
dll.test_configure_tabs.argtypes=[P]
dll.test_find.argtypes=[P];dll.test_find.restype=P
for n in ['test_scrub','test_prefetch','test_attach']:getattr(dll,n).argtypes=[P]
dll.test_bar.argtypes=[P,P,P,P]
dll.test_badge.argtypes=[P,P]
dll.test_preview.argtypes=[P]
dll.test_clock.argtypes=[D];dll.test_clock.restype=P
dll.test_spec.argtypes=[Z,D,D];dll.test_spec.restype=D
dll.test_now.argtypes=[D];dll.test_ready.argtypes=[P,D];dll.test_ready.restype=P
for n in ['test_fit_view','test_video_fit','test_normalize','test_relay','test_update_ad','test_apply_ad','test_fetch_ad']:getattr(dll,n).argtypes=[P]
dll.test_fit_pins.argtypes=[P];dll.test_fit_pins.restype=P
dll.test_fit.argtypes=[Z,D,D,D,D];dll.test_fit.restype=D
for n in ['test_playlist_ads','test_playlist_valid','test_hls_url']:getattr(dll,n).argtypes=[P];getattr(dll,n).restype=C.c_bool
dll.test_variant.argtypes=[P,P];dll.test_variant.restype=P
dll.test_save_ad.argtypes=[C.c_bool];dll.test_ad_enabled.restype=C.c_bool
class Runtime:
 def __init__(self):
  self.methods={};self.encodings=[];self.items={};self.assoc={};self.classes={};self.sels={};self.callbacks=[];self.errors=[];self.loads=[];self.seeks=[];self.pending=[];self.plays=[];self.now=1000.0;dll.test_now(self.now)
  def cb(t,f):
   def safe(*a):
    try:return f(*a)
    except Exception as e:self.errors.append(str(e));return 0
   c=t(safe);self.callbacks.append(c);return c
  functions=[(F1,lambda p:self.intern(self.classes,'class',C.string_at(p).decode())),(F1,lambda p:self.intern(self.sels,'selector',C.string_at(p).decode())),(F5,self.message),(F2,lambda o,k:self.assoc.get((o,k),0)),(FS,lambda o,k,v,p:self.assoc.__setitem__((o,k),v or 0)),(FD,lambda q,c,f:self.pending.append((c,f))),(FG,self.number),(FM,self.decimal),(FM,lambda o,s,t:self.seeks.append(t) or 0)]
  for i,(t,f) in enumerate(functions):dll.test_hook(i,cb(t,f))
 def new(self,kind,value):
  h=10000+len(self.items);self.items[h]=(kind,value);return h
 def intern(self,d,k,s):
  if s not in d:d[s]=self.new(k,s)
  return d[s]
 def obj(self,v):
  if v is None:return 0
  if isinstance(v,dict):return self.new('NSDictionary',{k:self.obj(x) for k,x in v.items()})
  if isinstance(v,list):return self.new('NSArray',[self.obj(x) for x in v])
  return self.new('NSString' if isinstance(v,str) else 'NSNumber',v)
 def val(self,h):return self.items.get(h,(None,None))[1]
 def raw(self,h):
  k,v=self.items.get(h,(None,None))
  if k=='NSDictionary':return {n:self.raw(x) for n,x in v.items()}
  return v
 def number(self,o,s):
  v=self.val(o);name=self.val(s)
  if isinstance(v,dict):
   if name=='testWidth':return float(v.get('width',375))
   if name=='testHeight':return float(v.get('height',220))
   if name=='testX':return float(v.get('x',0))
   if name=='testY':return float(v.get('y',0))
   if name=='alpha':return float(v.get('alpha',1))
   if name=='constant':return float(v.get('setConstant:',0))
   return float(v.get(name,v.get('setValue:',0)))
  return float(v or 0)
 def decimal(self,o,s,v):
  if self.val(s)=='numberWithDouble:':return self.obj(v)
  if self.val(s)=='constraintEqualToConstant:':return self.new('constraint',{'constant':v,'setConstant:':v,'firstItem':self.val(o).get('owner',0)})
  if isinstance(self.val(o),dict):self.val(o)[self.val(s)]=v
  return 0
 def message(self,o,s,a,b,c):
  name=self.val(s);kind,v=self.items.get(o,(None,None))
  if not o:return 0
  if name=='requestWithURL:':return self.new('NSMutableURLRequest',{'url':a,'headers':{}})
  if name in ['setHTTPMethod:','setHTTPBody:']:v[name]=a;return 0
  if name in ['setHTTPShouldHandleCookies:','setCachePolicy:']:v[name]=a;return 0
  if name=='setValue:forHTTPHeaderField:':v['headers'][self.val(b)]=self.val(a);return 0
  if name=='dataWithJSONObject:options:error:':return self.new('NSData',json.dumps(self.raw(a)).encode())
  if name=='JSONObjectWithData:options:error:':return self.obj(json.loads(self.val(a)))
  if name=='initWithData:encoding:':return self.obj(self.val(a).decode('utf-8'))
  if name in ['setScheme:','setHost:','setPath:','setQueryItems:']:v[name]=a;return 0
  if name=='queryItemWithName:value:':return self.new('NSURLQueryItem',{'name':self.val(a),'value':self.val(b)})
  if name=='URL':
   query=urllib.parse.urlencode([(self.val(x)['name'],self.val(x)['value']) for x in self.val(v['setQueryItems:'])]);return self.new('NSURL',urllib.parse.urlunsplit((self.val(v['setScheme:']),self.val(v['setHost:']),self.val(v['setPath:']),query,'')))
  if name=='statusCode':return v.get('statusCode',0)
  if name=='sendSynchronousRequest:returningResponse:error:':
   request=self.val(a);u=self.val(request['url']);self.http_requests=getattr(self,'http_requests',[])+[u]
   if urllib.parse.urlparse(u).hostname=='gql.twitch.tv':
    payload=json.loads(self.val(request['setHTTPBody:']));self.last_gql=payload;body=json.dumps({'data':{'streamPlaybackAccessToken':{'signature':'new-signature','value':'{"anonymous":true}'}}})
   elif u.endswith('/dirty.m3u8'):body='#EXTM3U\n#EXT-X-DATERANGE:CLASS="twitch-stitched-ad"\n#EXTINF:2,\nhttps://video.ttvnw.net/ad.ts'
   elif u.endswith('/clean.m3u8'):body=('#EXTM3U\n#EXT-X-DATERANGE:CLASS="twitch-stitched-ad"\n' if getattr(self,'all_sources_ads',False) else '#EXTM3U\n')+'#EXTINF:2,\nhttps://video.ttvnw.net/content.ts'
   else:body='#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080\nhttps://video.ttvnw.net/'+('dirty' if 'sig=original' in u else 'clean')+'.m3u8\n'
   response=self.new('NSHTTPURLResponse',{'statusCode':200});C.cast(b,C.POINTER(P))[0]=response;C.cast(c,C.POINTER(P))[0]=None;return self.new('NSData',body.encode())
  if name=='hostField':return v.get(self.val(a),0)
  if name=='hostFlag':v[self.val(a)]=bool(b);return 0
  if name=='objectForKey:' and kind=='defaults':
   value=getattr(self,'defaults',{}).get(self.val(a));return self.obj(value) if value is not None else 0
  if name in ['firstItem','secondItem','owningView','rightBarButtonItems','customView','currentTitle','accessibilityLabel','image','parentViewController','navigationItem','constraints']:return v.get(name,0)
  if name=='setCustomView:':v['customView']=a;return 0
  if name=='setHidesSharedBackground:':v['hidesBackground']=bool(a);return 0
  if name=='setContentMode:':v['contentMode']=a;return 0
  if name=='sendActionsForControlEvents:':v.setdefault('events',[]).append(a);return 0
  if name=='containsObject:':return int(a in v)
  if name=='deactivateConstraints:':
   for item in self.val(a):self.val(item)['active']=False
   return 0
  if name=='setActive:':v['active']=bool(a);return 0
  if name=='URLWithString:relativeToURL:':return self.new('NSURL',urllib.parse.urljoin(self.val(b),self.val(a)))
  if name=='absoluteURL':return o
  if name=='scheme':return self.obj(urllib.parse.urlparse(v).scheme)
  if name=='whitespaceAndNewlineCharacterSet':return self.obj(' \t\r\n')
  if name=='componentsSeparatedByString:':return self.new('NSArray',[self.obj(line) for line in v.split(self.val(a))])
  if name=='containsString:':return int(self.val(a) in v)
  if name=='hasSuffix:':return int(v.endswith(self.val(a)))
  if name=='standardUserDefaults':
   if not hasattr(self,'defaults'):self.defaults={}
   return self.intern(self.classes,'defaults','preferences')
  if name=='boolForKey:':return int(getattr(self,'defaults',{}).get(self.val(a),False))
  if name=='setBool:forKey:':self.defaults[self.val(b)]=bool(a);return 0
  if name=='setMode:':v['mode']=a;v['modeChanges']=v.get('modeChanges',0)+1;return 0
  if name=='mode':return v.get('mode',0)
  if name=='setView:':v['view']=a;return 0
  if name=='contentLayoutGuide':return o
  if name in ['labelColor','systemBackgroundColor']:return self.obj(name)
  if name in ['setNumberOfLines:','setOn:']:v[name]=a;return 0
  if name=='hostGetMethod':return self.methods.get((o,self.val(a)),0)
  if name=='hostTypeEncoding':return v['encoding']
  if name=='hostAddMethod':
   key=(o,self.val(a))
   if key in self.methods:return 0
   self.methods[key]=self.new('method',{'encoding':c,'imp':b});return 1
  if name=='respondsToSelector:':return int(isinstance(v,dict) and self.val(a) in v)
  if name=='effectiveUserInterfaceLayoutDirection':return int(v.get(name,0))
  if name=='isActive':return int(v.get('active',False))
  if name=='setUserInteractionEnabled:':v['interactive']=bool(a);return 0
  if name=='gestureRecognizers':return v.get(name,0)
  if name=='alloc':return self.new(v,{'children':[],'parent':0})
  if name=='initWithImage:':v['image']=a;return o
  if name=='isEnabled':return int(v.get('enabled',True))
  if name=='isHidden':return int(v.get('setHidden:',v.get('hidden',False)))
  if name in ['allButtons','bottomRightStackView','topLeftStackView','topRightStackView']:return v.get(name,0)
  if name in ['retain','autorelease']:return o
  if name in ['release','drain']:return 0
  if name=='isKindOfClass:':return int(kind==self.val(a) or (self.val(a)=='UIView' and (kind.endswith('View') or kind in ['UIButton','UIScrollView','UIControl'])) or (self.val(a)=='UIControl' and kind in ['UIButton','UISwitch']))
  if name=='objectForKey:':return v.get(self.val(a),0)
  if name=='setObject:forKey:':v[self.val(b)]=a;return 0
  if name=='removeObjectForKey:':v.pop(self.val(a),None);return 0
  if name=='stringWithUTF8String:':return self.obj(C.string_at(a).decode())
  if name=='numberWithUnsignedInteger:':return self.obj(a or 0)
  if name in ['unsignedIntegerValue','length','count']:
   if name=='unsignedIntegerValue':return int(v or 0)
   return len(v or '')
  if name in ['dictionary','array','weakObjectsHashTable']:
   return self.obj({}) if name=='dictionary' else self.new('NSArray' if name=='array' else 'weak',[])
  if name=='addObject:':
   if isinstance(v,list):v.append(a)
   else:v.setdefault('weak',[]).append(a)
   return 0
  if name=='anyObject':return v[0] if v else 0
  if name=='objectAtIndex:':return v[a or 0]
  if name=='isEqualToString:':return int(v==self.val(a))
  if name=='hasPrefix:':return int(v.startswith(self.val(a)))
  if name=='characterSetWithCharactersInString:':return self.obj(self.val(a))
  if name=='stringByTrimmingCharactersInSet:':return self.obj(v.strip(self.val(a)))
  if name=='URLWithString:':return self.new('NSURL',self.val(a))
  if name=='host':return self.obj(urllib.parse.urlparse(v).hostname)
  if name=='path':return self.obj(urllib.parse.urlparse(v).path)
  if name=='pathExtension':return self.obj(v.rsplit('.',1)[-1])
  if name=='lastPathComponent':return self.obj(v.rsplit('/',1)[-1])
  if name=='stringByDeletingPathExtension':return self.obj(v.rsplit('.',1)[0])
  if name in ['load:configuration:','loadSource:configuration:']:self.loads.append((o,name,a,b));return 0
  if name=='play':self.plays.append(o);return 0
  if name=='pause':return 0
  if name=='imageWithTintColor:':return self.new('UIImage',{'tint':self.val(a)})
  if name in ['colorWithRed:green:blue:alpha:','systemImageNamed:','imageWithConfiguration:','monospacedDigitSystemFontOfSize:weight:']:return self.obj('image color or font')
  if name=='layer':return self.new('layer',{})
  if name in ['setTextAlignment:','setClipsToBounds:','setBackgroundColor:']:v[name]=a;return 0
  if name=='titleLabel':return self.new('UILabel',{})
  if name=='setThumbImage:forState:':v.setdefault('thumbs',{})[b or 0]=a;return 0
  if name=='setImage:forState:':v['image']=a;return 0
  if name=='setAccessibilityValue:':v['accessibilityValue']=self.val(a);return 0
  if name=='setContinuous:':v['continuous']=bool(a);return 0
  if name=='addTarget:action:forControlEvents:':v.setdefault('actions',[]).append((self.val(b),c));return 0
  if name in ['setMinimumTrackTintColor:','setMaximumTrackTintColor:','setThumbTintColor:','setThumbImage:forState:','setTintColor:']:v[name]=a;return 0
  if name=='error':return v.get('error',0)
  if name=='source':return v.get('source',0)
  if name=='window':return 0
  if name=='stringValue':return self.obj(str(v))
  if name=='stringByAppendingString:':return self.obj(v+self.val(a))
  if name=='buttonWithType:':return self.new('UIButton',{'children':[],'parent':0})
  if name=='new':
   if v=='IVSPlayer':return 0
   return self.new(v,{'children':[],'parent':0,'arranged':[]})
  if name in ['whiteColor','systemRedColor','clearColor']:return self.obj(name)
  if name=='isTracking':return int(v.get('tracking',False))
  if name=='setText:':v['text']=a;return 0
  if name=='text':return v.get('text',0)
  if name in ['addSubview:','addArrangedSubview:']:
   v['children'].append(a);self.val(a)['parent']=o
   if name=='addArrangedSubview:':v['arranged'].append(a)
   return 0
  if name=='addObject:' and isinstance(v,dict):return 0
  if name in ['setAxis:','setAlignment:','setTranslatesAutoresizingMaskIntoConstraints:','setActive:','setContinuous:','setAccessibilityLabel:','setTitleColor:forState:','setTextColor:','setFont:','bringSubviewToFront:','addTarget:action:forControlEvents:']:return 0
  if name=='safeAreaLayoutGuide':return o
  if name in ['heightAnchor','widthAnchor','leadingAnchor','trailingAnchor','bottomAnchor','topAnchor','centerYAnchor','centerXAnchor','safeAreaLayoutGuide']:return self.new('anchor',{'owner':o,'attribute':name})
  if name=='constraintEqualToAnchor:constant:':return self.new('constraint',{'firstItem':v.get('owner',0),'secondItem':self.val(a).get('owner',0)})
  if name=='subviews':return self.new('NSArray',v.get('children',[]))
  if name=='player':return v['player']
  if name in ['setHidden:','setEnabled:','setTitle:forState:']:
   v[name]=self.val(a) if name=='setTitle:forState:' else bool(a)
   return 0
  if name=='superview':return v.get('parent',0)
  if name=='allObjects':return self.new('NSArray',v if kind=='weak' else [o])
  if name=='arrangedSubviews':return self.new('NSArray',v.get('arranged',[]))
  if name=='state':return v.get('state',2)
  raise AssertionError((kind,name))
 def setup(self,mode=0,source=False):
  self.player=self.new('player',{'position':100.0,'duration':500.0,'state':2});self.liveurl=self.new('NSURL','https://usher.ttvnw.net/api/channel/hls/example.m3u8?sig=original');self.row=self.new('row',{});self.sender=self.new('button',{'parent':self.row});dll.test_row(self.row,self.player)
  self.state=self.obj({'generation':3,'login':'example','mode':mode,'configuration':'config'});self.val(self.state)['liveURL']=self.liveurl
  if source:self.val(self.state)['liveSource']=self.obj('original source')
  dll.test_state(self.player,self.state)
 def advance(self,seconds):
  self.now+=seconds;dll.test_now(self.now)
 def assert_clean(self):assert not self.errors,self.errors
class Tests(unittest.TestCase):
 def setUp(self):self.r=Runtime()
 def tearDown(self):self.r.assert_clean()
 def test_auto_rewind_once_without_controls(self):
  r=self.r;r.setup();dll.test_save_auto(True);r.val(r.state).update(autoRewind=r.obj(1),cachedURL=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8'),cachedDuration=r.obj(500))
  dll.test_update(r.player);self.assertEqual(r.seeks,[499]);self.assertEqual(len(r.loads),1);dll.test_update(r.player);self.assertEqual(r.seeks,[499]);self.assertEqual(len(r.loads),1)
 def test_live_cancels_waiting_auto_rewind(self):
  r=self.r;r.setup();dll.test_save_auto(True);r.val(r.state)['autoRewind']=r.obj(1);dll.test_live(r.player)
  r.val(r.state).update(cachedURL=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8'),cachedDuration=r.obj(500));dll.test_update(r.player);self.assertEqual(r.seeks,[]);self.assertEqual(len(r.loads),1)
 def test_auto_rewind_waits_for_recording(self):
  r=self.r;r.setup();dll.test_save_auto(True);r.val(r.state)['autoRewind']=r.obj(1);dll.test_update(r.player);self.assertEqual(r.loads,[]);self.assertEqual(r.seeks,[])
 def test_exact_live_url_scope(self):
  for url,yes in [('https://usher.ttvnw.net/api/channel/hls/example.m3u8',True),('https://evil.example/api/channel/hls/example.m3u8',False),('https://usher.ttvnw.net/vod/123.m3u8',False),('https://usher.ttvnw.net/api/channel/hls/bad-name.m3u8',False)]:self.assertEqual(bool(dll.test_login(self.r.new('NSURL',url))),yes)
 def test_live_restores_original_url_and_invalidates_pending_fetch(self):
  r=self.r;r.setup(1);dll.test_live(r.player);self.assertEqual(r.loads[-1][2],r.liveurl);self.assertEqual(r.raw(r.state)['mode'],0);self.assertEqual(r.raw(r.state)['generation'],4);self.assertEqual(r.plays,[r.player])
 def test_live_restores_preloaded_source_when_present(self):
  r=self.r;r.setup(2,True);dll.test_live(r.player);self.assertEqual(r.loads[-1][1],'loadSource:configuration:');self.assertEqual(r.loads[-1][2],r.val(r.state)['liveSource'])
 def test_rewind_seeks_back_without_network_while_replaying(self):
  r=self.r;r.setup(2);dll.test_rewind(r.sender);r.advance(0.13);dll.test_tick();self.assertEqual(r.seeks,[90.0]);self.assertEqual(r.pending,[])
 def test_rewind_clamps_at_start(self):
  r=self.r;r.setup(2);r.val(r.player)['position']=8;dll.test_rewind(r.sender);r.advance(0.13);dll.test_tick();self.assertEqual(r.seeks,[0.0])
 def test_forward_seeks_and_returns_live_at_edge(self):
  r=self.r;r.setup(2);dll.test_forward(r.sender);r.advance(0.13);dll.test_tick();self.assertEqual(r.seeks,[110.0]);r.val(r.player)['position']=495;dll.test_forward(r.sender);self.assertEqual(r.loads[-1][2],r.liveurl)
 def test_loading_deduplicates_requests(self):
  r=self.r;r.setup();dll.test_rewind(r.sender);dll.test_rewind(r.sender);self.assertEqual(len(r.pending),1);self.assertEqual(r.raw(r.state)['mode'],0)
 def test_stale_recording_does_not_replace_changed_channel(self):
  r=self.r;r.setup();job=r.obj({'generation':2,'login':'example','duration':500});r.val(job)['player']=r.new('weak',[r.player]);r.val(job)['resultURL']=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8');dll.test_apply(job);self.assertEqual(r.loads,[])
 def test_current_recording_loads_and_queues_initial_seek(self):
  r=self.r;r.setup();job=r.obj({'generation':3,'login':'example','duration':500});r.val(job)['player']=r.new('weak',[r.player]);r.val(job)['resultURL']=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8');dll.test_apply(job);self.assertEqual(r.loads,[]);self.assertEqual(r.raw(r.state)['cachedDuration'],500);dll.test_rewind(r.sender);self.assertEqual(len(r.loads),1);self.assertEqual(r.raw(r.state)['pending'],490);self.assertEqual(r.plays,[]);dll.test_tick();self.assertEqual(r.seeks,[490.0]);self.assertNotIn('pending',r.raw(r.state));self.assertEqual(r.plays,[r.player])
 def test_unavailable_recording_leaves_live_playback_untouched(self):
  r=self.r;r.setup(0);job=r.obj({'generation':3,'login':'example'});r.val(job)['player']=r.new('weak',[r.player]);dll.test_apply(job);self.assertEqual(r.loads,[]);self.assertEqual(r.raw(r.state)['mode'],0)
 def test_failed_recording_load_restores_live(self):
  r=self.r;r.setup(2);r.val(r.state)['pending']=r.obj(470);r.val(r.state)['attempts']=r.obj(100);r.val(r.player)['duration']=0;dll.test_tick();self.assertEqual(r.loads[-1][2],r.liveurl);self.assertEqual(r.raw(r.state)['mode'],0)
 def test_slider_seeks_selected_position(self):
  r=self.r;r.setup(2);r.val(r.sender)['value']=0.5;dll.test_scrub(r.sender);dll.test_tick();self.assertEqual(r.seeks,[250.0])
 def test_slider_at_live_edge_restores_live(self):
  r=self.r;r.setup(2);r.val(r.sender)['value']=1.0;dll.test_scrub(r.sender);self.assertEqual(r.loads[-1][2],r.liveurl)
 def test_slider_ignores_invalid_value(self):
  r=self.r;r.setup(2);r.val(r.sender)['value']=float('nan');dll.test_scrub(r.sender);self.assertEqual(r.seeks,[]);self.assertEqual(r.loads,[])
 def test_dragging_bar_is_not_overwritten_by_timer(self):
  r=self.r;r.setup(2);slider=r.new('UISlider',{'tracking':True,'value':0.8});label=r.new('UILabel',{});live=r.new('UIButton',{});dll.test_bar(r.row,slider,label,live);dll.test_tick();self.assertNotIn('setValue:',r.val(slider))
 def test_repeated_scrub_while_loading_retargets_without_reloading(self):
  r=self.r;r.setup(2);r.val(r.state)['pending']=r.obj(450);r.val(r.sender)['value']=0.25;dll.test_scrub(r.sender);self.assertEqual(r.raw(r.state)['pending'],125);self.assertEqual(r.loads,[])
 def test_cached_seek_does_not_wait_for_network(self):
  r=self.r;r.setup();r.val(r.state)['cachedURL']=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8');r.val(r.state)['cachedDuration']=r.obj(500);r.val(r.sender)['value']=0.25;dll.test_scrub(r.sender);self.assertEqual(r.pending,[]);self.assertEqual(r.raw(r.state)['pending'],125);self.assertEqual(len(r.loads),1)
 def test_ready_state_seeks_before_starting_playback(self):
  r=self.r;r.setup(2);r.val(r.state)['pending']=r.obj(250);r.val(r.player)['state']=1;dll.test_tick();self.assertEqual(r.seeks,[250]);self.assertEqual(r.plays,[r.player])
 def test_mounts_full_width_slider_and_right_aligned_badge(self):
  r=self.r;r.setup();root=r.new('UIView',{'children':[],'parent':0});controls=r.new('UIView',{'children':[],'parent':root});video=r.new('IVSPlayerView',{'children':[],'parent':root,'player':r.player});r.val(root)['children']=[video,controls];dll.test_attach(controls);children=r.val(controls)['children'];self.assertEqual(len(children),5);row=next(x for x in children if r.items[x][0]=='UIStackView');self.assertEqual([r.items[x][0] for x in r.val(row)['arranged']],['UIButton','UISlider']);slider=r.val(row)['arranged'][1];self.assertTrue(r.val(slider)['continuous']);self.assertIn(('preview:',4096),r.val(slider)['actions']);self.assertIn(('scrub:',192),r.val(slider)['actions']);thumbs=r.val(slider)['thumbs'];self.assertEqual(r.val(thumbs[0])['tint'],'clearColor');self.assertEqual(r.val(thumbs[1])['tint'],'whiteColor');badge=r.val(children[-1])['children'][0];self.assertEqual(r.val(r.val(badge)['text']),'LIVE');dll.test_attach(controls);self.assertEqual(len(r.val(controls)['children']),5)
 def test_ten_second_clicks_retarget_pending_seek(self):
  r=self.r;r.setup(2);r.val(r.state)['pending']=r.obj(250);dll.test_rewind(r.sender);self.assertEqual(r.raw(r.state)['pending'],240);dll.test_forward(r.sender);self.assertEqual(r.raw(r.state)['pending'],250);self.assertEqual(r.loads,[])
 def test_uses_prepared_source_without_resolving_master_again(self):
  r=self.r;r.setup();r.val(r.state)['cachedURL']=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8');r.val(r.state)['cachedDuration']=r.obj(500);source=r.obj('prepared recording');r.val(r.state)['preparedPlayer']=r.new('player',{'source':source});r.val(r.state)['preparedAt']=r.obj(1000);r.val(r.state)['preparedDuration']=r.obj(500);r.val(r.sender)['value']=0.5;dll.test_scrub(r.sender);self.assertEqual(r.loads[-1][1],'loadSource:configuration:');self.assertEqual(r.loads[-1][2],source);self.assertEqual(r.pending,[])
 def test_elapsed_clock_hours_minutes_seconds_and_boundaries(self):
  for value,text in [(0,'00:00:00'),(59.9,'00:00:59'),(60,'00:01:00'),(3599,'00:59:59'),(3600,'01:00:00'),(5025,'01:23:45'),(45296,'12:34:56'),(-1,'00:00:00')]:self.assertEqual(self.r.val(dll.test_clock(value)),text)
 def test_drag_preview_updates_elapsed_timestamp_without_seeking(self):
  r=self.r;r.setup(2);r.val(r.player)['duration']=10050;slider=r.new('UISlider',{'parent':r.row,'tracking':True,'value':0.5});label=r.new('UILabel',{});live=r.new('UIButton',{});dll.test_bar(r.row,slider,label,live);dll.test_preview(slider);self.assertEqual(r.val(r.val(label)['text']),'01:23:45');self.assertEqual(r.seeks,[]);self.assertEqual(r.loads,[]);dll.test_tick();self.assertEqual(r.val(r.val(label)['text']),'01:23:45');dll.test_scrub(slider);dll.test_tick();self.assertEqual(r.seeks,[5025])
 def test_passive_timestamp_is_elapsed_position(self):
  r=self.r;r.setup(2);r.val(r.player)['position']=3661;r.val(r.player)['duration']=7200;slider=r.new('UISlider',{'parent':r.row,'tracking':False});label=r.new('UILabel',{});live=r.new('UIButton',{});dll.test_bar(r.row,slider,label,live);dll.test_tick();self.assertEqual(r.val(r.val(label)['text']),'01:01:01')
 def test_timestamp_hidden_at_live_and_shown_during_drag(self):
  r=self.r;r.setup(0);r.val(r.state)['cachedDuration']=r.obj(7200);slider=r.new('UISlider',{'parent':r.row,'tracking':False,'value':1.0});label=r.new('UILabel',{});live=r.new('UIButton',{});dll.test_bar(r.row,slider,label,live);dll.test_tick();self.assertTrue(r.val(label)['setHidden:']);r.val(slider)['tracking']=True;r.val(slider)['value']=0.5;dll.test_preview(slider);self.assertFalse(r.val(label)['setHidden:']);self.assertEqual(r.val(r.val(label)['text']),'01:00:00');r.val(slider)['tracking']=False;dll.test_tick();self.assertTrue(r.val(label)['setHidden:'])
 def test_rewind_timestamp_remains_visible(self):
  r=self.r;r.setup(2);slider=r.new('UISlider',{'parent':r.row,'tracking':False});label=r.new('UILabel',{});live=r.new('UIButton',{});dll.test_bar(r.row,slider,label,live);dll.test_tick();self.assertFalse(r.val(label)['setHidden:'])
 def test_live_badge_changes_label_when_rewound(self):
  r=self.r;r.setup(0);slider=r.new('UISlider',{'tracking':False});label=r.new('UILabel',{});live=r.new('UIButton',{});badge=r.new('UILabel',{});dll.test_bar(r.row,slider,label,live);dll.test_badge(r.row,badge);dll.test_tick();self.assertEqual(r.val(r.val(badge)['text']),'LIVE');r.val(r.state)['mode']=r.obj(2);dll.test_tick();self.assertEqual(r.val(r.val(badge)['text']),'LIVE \u25b6')
 def test_rapid_skips_issue_one_final_seek(self):
  r=self.r;r.setup(2);dll.test_rewind(r.sender);r.advance(0.04);dll.test_rewind(r.sender);r.advance(0.04);dll.test_rewind(r.sender);r.advance(0.11);dll.test_tick();self.assertEqual(r.seeks,[]);r.advance(0.02);dll.test_tick();self.assertEqual(r.seeks,[70]);dll.test_tick();self.assertEqual(r.seeks,[70])
 def test_live_cancels_queued_skip(self):
  r=self.r;r.setup(2);dll.test_rewind(r.sender);dll.test_live(r.player);r.advance(0.2);dll.test_tick();self.assertEqual(r.seeks,[])
 def test_ready_source_survives_unready_refresh(self):
  r=self.r;r.setup();old=r.obj('old ready source');r.val(r.state).update(preparedPlayer=r.new('player',{'source':old,'state':1}),preparedAt=r.obj(1000),preparedDuration=r.obj(500),warmingPlayer=r.new('player',{'source':0,'state':0}),warmingAt=r.obj(1000),warmingDuration=r.obj(550));self.assertEqual(dll.test_ready(r.state,250),old)
 def test_new_source_promoted_only_once_ready(self):
  r=self.r;r.setup();new=r.obj('new ready source');r.val(r.state).update(warmingPlayer=r.new('player',{'source':new,'state':1}),warmingAt=r.obj(1000),warmingDuration=r.obj(600));self.assertEqual(dll.test_ready(r.state,250),new);self.assertNotIn('warmingPlayer',r.raw(r.state))
 def test_stale_or_too_short_source_is_not_used(self):
  r=self.r;r.setup();old=r.obj('ready source');r.val(r.state).update(preparedPlayer=r.new('player',{'source':old,'state':1}),preparedAt=r.obj(1000),preparedDuration=r.obj(500));self.assertFalse(dll.test_ready(r.state,510));r.advance(91);self.assertFalse(dll.test_ready(r.state,250))
 def test_initial_source_issues_no_early_duplicate_seek(self):
  r=self.r;r.setup();r.val(r.state).update(cachedURL=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8'),cachedDuration=r.obj(500));r.val(r.sender)['value']=0.5;dll.test_scrub(r.sender);self.assertEqual(r.seeks,[]);dll.test_tick();self.assertEqual(r.seeks,[250]);dll.test_tick();self.assertEqual(r.seeks,[250])
 def test_failed_preparation_retries_after_five_seconds_not_thirty(self):
  r=self.r;r.setup();r.val(r.state).update(prepareFailed=r.obj(1),cacheRequestAt=r.obj(1000));dll.test_prefetch(r.player);self.assertEqual(r.pending,[]);r.advance(5.1);dll.test_prefetch(r.player);self.assertEqual(len(r.pending),1)
 def test_recording_unavailable_still_uses_normal_refresh_interval(self):
  r=self.r;r.setup();r.val(r.state)['cacheRequestAt']=r.obj(1000);r.advance(6);dll.test_prefetch(r.player);self.assertEqual(r.pending,[])
 def test_responsive_spacing_stays_compact_on_wide_player(self):
  for width in [320,375,430,600,768,1024,1366]:
   gap=dll.test_spec(2,width,300);self.assertGreaterEqual(gap,64);self.assertLessEqual(gap,88);self.assertLess(gap+22,width/2)
 def test_small_panes_keep_timeline_but_hide_side_skips(self):
  self.assertEqual(dll.test_spec(3,260,160),1);self.assertEqual(dll.test_spec(4,260,160),0);self.assertEqual(dll.test_spec(1,260,160),24)
 def test_mini_player_and_invalid_geometry_hide_custom_controls(self):
  for w,h in [(180,200),(375,90),(0,0),(float('nan'),200),(float('inf'),200)]:self.assertEqual(dll.test_spec(3,w,h),0)
 def test_resizing_does_not_duplicate_controls_or_seek(self):
  r=self.r;r.setup(2);root=r.new('UIView',{'children':[],'parent':0});controls=r.new('UIView',{'children':[],'parent':root,'width':375,'height':220});video=r.new('IVSPlayerView',{'children':[],'parent':root,'player':r.player});r.val(root)['children']=[video,controls]
  for w,h in [(375,220),(768,500),(260,160),(1024,450),(375,220)]:
   r.val(controls).update(width=w,height=h);dll.test_attach(controls);children=r.val(controls)['children'];self.assertEqual(len(children),5);row=next(x for x in children if r.items[x][0]=='UIStackView');side=children[2];self.assertEqual(r.val(side)['setHidden:'],not bool(dll.test_spec(4,w,h)))
  self.assertEqual(r.seeks,[]);self.assertEqual(r.loads,[])
 def test_responsive_policy_is_deterministic_across_fold_unfold_cycles(self):
  for _ in range(20):
   self.assertEqual(dll.test_spec(4,375,220),0);self.assertEqual(dll.test_spec(4,260,160),0);self.assertEqual(dll.test_spec(4,900,600),1)
 def test_skip_buttons_clear_live_badge_for_all_visible_sizes(self):
  for w in range(240,1400,10):
   for h in range(128,700,10):
    if dll.test_spec(4,w,h):
     padding=dll.test_spec(0,w,h);bottom=dll.test_spec(1,w,h);skip=dll.test_spec(2,w,h)
     horizontal=w*0.5+skip+22+8<=w-padding-68
     vertical=h*0.5+22+8<=h-bottom-92
     self.assertTrue(horizontal or vertical,(w,h))
 def test_short_narrow_pane_hides_overlapping_skips(self):
  for w,h in [(280,180),(300,200),(320,220),(340,200)]:self.assertEqual(dll.test_spec(4,w,h),0)
 def test_narrow_tall_player_restores_skip_controls(self):
  self.assertEqual(dll.test_spec(4,280,360),1)
 def test_skips_clear_timeline_and_timestamp_during_resize(self):
  for w in range(240,1400,10):
   for h in range(128,700,10):
    if dll.test_spec(4,w,h):
     pad=dll.test_spec(0,w,h);bottom=dll.test_spec(1,w,h);skip=dll.test_spec(2,w,h)
     self.assertLessEqual(h/2+30,h-bottom-44,(w,h))
     self.assertTrue(w/2-skip-22>=pad+80 or h/2+30<=h-bottom-66,(w,h))
 def test_wide_short_windows_hide_skips(self):
  for w in [600,768,1024,1366]:
   for h in [180,190,210]:self.assertEqual(dll.test_spec(4,w,h),0)
 def test_detached_player_keeps_timestamp_hidden(self):
  r=self.r;r.setup(2);root=r.new('UIView',{'children':[],'parent':0});controls=r.new('UIView',{'children':[],'parent':root,'width':768,'height':500});video=r.new('IVSPlayerView',{'children':[],'parent':root,'player':r.player});r.val(root)['children']=[video,controls]
  dll.test_attach(controls);children=r.val(controls)['children'];row=next(x for x in children if r.items[x][0]=='UIStackView');label=next(x for x in children if r.items[x][0]=='UILabel');dll.test_row(row,r.player)
  r.val(root)['children']=[controls];dll.test_attach(controls);dll.test_tick();self.assertTrue(r.val(label)['setHidden:'])
 def layout_fixture(self,w=768,h=500,x=0,y=0):
  r=self.r;r.setup(2);root=r.new('UIView',{'children':[],'parent':0});controls=r.new('UIView',{'children':[],'parent':root,'width':w,'height':h,'x':x,'y':y});video=r.new('IVSPlayerView',{'children':[],'parent':root,'player':r.player});r.val(root)['children']=[video,controls]
  dll.test_attach(controls);children=r.val(controls)['children'];row=next(v for v in children if r.items[v][0]=='UIStackView');return controls,row,root
 def test_native_button_collision_hides_overlay_then_restores(self):
  r=self.r;controls,row,_=self.layout_fixture();native=r.new('UIButton',{'parent':controls,'x':650,'y':380,'width':80,'height':44});r.val(controls)['allButtons']=r.new('NSArray',[native]);dll.test_attach(controls);self.assertTrue(r.val(row)['setHidden:'])
  r.val(native)['hidden']=True;dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:'])
 def test_native_bottom_actions_move_timeline_up(self):
  r=self.r;controls,row,_=self.layout_fixture();stack=r.new('UIStackView',{'parent':controls,'x':600,'y':410,'width':140,'height':70});r.val(controls)['bottomRightStackView']=stack;dll.test_attach(controls)
  constants=[v.get('setConstant:') for k,v in r.items.values() if k=='constraint'];self.assertIn(-98.0,constants);self.assertFalse(r.val(row)['setHidden:'])
 def test_hidden_native_ancestor_does_not_block_custom_controls(self):
  r=self.r;controls,row,_=self.layout_fixture();parent=r.new('UIView',{'parent':controls,'hidden':True});button=r.new('UIButton',{'parent':parent,'x':650,'y':380,'width':80,'height':44});r.val(controls)['allButtons']=r.new('NSArray',[button]);dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:'])
 def test_asymmetric_safe_area_is_used_for_collision_positions(self):
  r=self.r;controls,row,_=self.layout_fixture(x=70,y=30);native=r.new('UIButton',{'parent':controls,'x':720,'y':410,'width':80,'height':44});r.val(controls)['allButtons']=r.new('NSArray',[native]);dll.test_attach(controls);self.assertTrue(r.val(row)['setHidden:'])
 def test_two_players_are_not_arbitrarily_selected(self):
  r=self.r;controls,row,root=self.layout_fixture();other=r.new('player',{'state':2});dll.test_state(other,r.obj({'login':'other'}));video=r.new('IVSPlayerView',{'children':[],'parent':root,'player':other});r.val(root)['children'].append(video)
  dll.test_attach(controls);self.assertTrue(r.val(row)['setHidden:']);self.assertEqual(r.loads,[]);self.assertEqual(r.seeks,[])
 def test_rtl_live_button_collision_uses_left_edge(self):
  r=self.r;controls,row,_=self.layout_fixture();r.val(controls)['effectiveUserInterfaceLayoutDirection']=1;native=r.new('UIButton',{'parent':controls,'x':16,'y':375,'width':68,'height':20});r.val(controls)['allButtons']=r.new('NSArray',[native]);dll.test_attach(controls);self.assertTrue(r.val(row)['setHidden:'])
 def test_transparent_native_buttons_do_not_hide_overlay(self):
  r=self.r;controls,row,_=self.layout_fixture();native=r.new('UIButton',{'parent':controls,'x':650,'y':380,'width':80,'height':44,'alpha':0.0});r.val(controls)['allButtons']=r.new('NSArray',[native]);dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:'])
 def test_native_center_button_collision_hides_only_skip_controls(self):
  r=self.r;controls,row,_=self.layout_fixture();native=r.new('UIButton',{'parent':controls,'x':430,'y':228,'width':80,'height':44});r.val(controls)['allButtons']=r.new('NSArray',[native]);dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:']);buttons=[v for v in r.val(controls)['children'] if r.items[v][0]=='UIButton'];self.assertTrue(r.val(buttons[0])['setHidden:']);self.assertTrue(r.val(buttons[1])['setHidden:'])
 def test_local_player_stays_bound_when_neighbor_stream_exists(self):
  r=self.r;controls,row,root=self.layout_fixture();parent=r.new('UIView',{'children':[root],'parent':0});r.val(root)['parent']=parent;other=r.new('player',{'state':2});dll.test_state(other,r.obj({'login':'other'}));video=r.new('IVSPlayerView',{'children':[],'parent':parent,'player':other});r.val(parent)['children'].append(video);dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:'])
 def test_native_header_labels_are_reserved_too(self):
  r=self.r;controls,row,_=self.layout_fixture(w=375,h=160);header=r.new('UIStackView',{'parent':controls,'x':240,'y':0,'width':120,'height':70});r.val(controls)['topRightStackView']=header;dll.test_attach(controls);self.assertTrue(r.val(row)['setHidden:'])
 def test_unknown_native_button_collection_fails_safely(self):
  r=self.r;controls,row,_=self.layout_fixture();r.val(controls)['allButtons']=r.obj({'unexpected':1});dll.test_attach(controls);self.assertFalse(r.val(row)['setHidden:'])
 def test_auto_rewind_defaults_off(self):
  self.assertFalse(dll.test_auto())
 def test_auto_setting_persists_and_updates_next_live_load(self):
  r=self.r;r.setup();dll.test_save_auto(True);self.assertTrue(dll.test_auto());dll.test_load(r.player,r.liveurl,r.obj('config'));state=dll.test_getstate(r.player);self.assertEqual(r.raw(state)['autoRewind'],1)
  dll.test_save_auto(False);self.assertFalse(dll.test_auto());self.assertEqual(r.raw(state)['autoRewind'],0)
  dll.test_load(r.player,r.liveurl,r.obj('config'));self.assertEqual(r.raw(dll.test_getstate(r.player))['autoRewind'],0)
 def test_disabled_preference_blocks_already_queued_auto_switch(self):
  r=self.r;r.setup();r.val(r.state).update(autoRewind=r.obj(1),cachedURL=r.new('NSURL','https://usher.ttvnw.net/vod/123.m3u8'),cachedDuration=r.obj(500));dll.test_update(r.player);self.assertEqual(r.loads,[]);self.assertEqual(r.seeks,[])
 def test_settings_panel_contains_switch_explanation_and_done(self):
  r=self.r;vc=r.new('UIViewController',{});dll.test_settings_load(vc);scroll=r.val(vc)['view'];stack=r.val(scroll)['children'][0];contents=r.val(stack)['arranged'];switchrow=r.val(contents[1])['arranged'];toggle=switchrow[1];self.assertEqual(r.items[toggle][0],'UISwitch');self.assertFalse(r.val(toggle)['setOn:']);self.assertIn(('toggleAuto:',4096),r.val(toggle)['actions']);self.assertIn('not guaranteed',r.val(r.val(contents[2])['text']));self.assertIn(('done:',64),r.val(contents[-1])['actions'])
 def test_tab_mode_switches_only_when_needed(self):
  r=self.r;tabs=r.new('UIViewController',{'mode':2,'setMode:':True});dll.test_configure_tabs(tabs);self.assertEqual(r.val(tabs)['mode'],1);dll.test_configure_tabs(tabs);self.assertEqual(r.val(tabs)['modeChanges'],1)
 def test_tab_mode_older_system_is_untouched(self):
  r=self.r;tabs=r.new('UIViewController',{});dll.test_configure_tabs(tabs);self.assertNotIn('modeChanges',r.val(tabs))
 def test_thumb_hidden_until_actual_drag_even_if_highlight_stale(self):
  r=self.r;controls,row,_=self.layout_fixture();dll.test_row(row,r.player);slider=r.val(row)['arranged'][1];dll.test_tick();self.assertEqual(r.val(r.val(slider)['thumbs'][1])['tint'],'clearColor')
  r.val(slider)['tracking']=True;dll.test_tick();self.assertEqual(r.val(r.val(slider)['thumbs'][1])['tint'],'whiteColor')
  r.val(slider)['tracking']=False;dll.test_tick();self.assertEqual(r.val(r.val(slider)['thumbs'][5])['tint'],'clearColor')
 def feed_fixture(self,w=1172,h=700,vw=1920,vh=1080):
  r=self.r;pane=r.new('UIView',{'width':w,'height':h,'parent':0});feed=r.new('_TtC6Twitch14FeedPlayerView',{'width':w,'height':h,'parent':pane,'videoWidth':vw,'videoHeight':vh});container=r.new('UIView',{'width':w,'height':h,'parent':feed});video=r.new('_TtC6Twitch15VideoPlayerView',{'width':w,'height':h,'parent':container,'videoFillsViewBounds':True});scroll=r.new('UIScrollView',{'width':w,'height':h,'parent':video});r.val(video)['scrollView']=scroll;r.val(feed).update(playerContainerView=container,playerView=video)
  native=r.new('constraint',{'firstItem':video,'secondItem':container,'active':True});internal=r.new('constraint',{'firstItem':scroll,'secondItem':video,'active':True});r.val(feed)['constraints']=r.new('NSArray',[native]);r.val(video)['constraints']=r.new('NSArray',[internal]);return pane,feed,container,video,scroll,native,internal
 def test_feed_fit_replaces_oversized_placement_but_keeps_internal_constraints(self):
  r=self.r;pane,feed,container,video,scroll,native,internal=self.feed_fixture();dll.test_fit_view(feed);pins=r.val(dll.test_fit_pins(video));self.assertEqual(len(pins),4);self.assertFalse(r.val(native)['active']);self.assertTrue(r.val(internal)['active']);self.assertFalse(r.val(video)['videoFillsViewBounds']);self.assertEqual(r.val(scroll)['setZoomScale:'],1)
  self.assertAlmostEqual(r.val(pins[2])['setConstant:'],1172);self.assertAlmostEqual(r.val(pins[3])['setConstant:'],659.25)
 def test_sidebar_resize_fits_whole_video_to_visible_pane_and_restores(self):
  r=self.r;pane,feed,container,video,scroll,native,internal=self.feed_fixture();dll.test_fit_view(feed);pins_id=dll.test_fit_pins(video);pins=r.val(pins_id)
  r.val(pane)['width']=760;dll.test_fit_view(feed);self.assertEqual(dll.test_fit_pins(video),pins_id);self.assertEqual(r.val(pins[2])['setConstant:'],760);self.assertEqual(r.val(pins[3])['setConstant:'],427.5);self.assertEqual(r.val(pins[0])['setConstant:'],-206)
  r.val(pane)['width']=1172;dll.test_fit_view(feed);self.assertEqual(r.val(pins[2])['setConstant:'],1172);self.assertEqual(r.val(pins[0])['setConstant:'],0)
 def test_portrait_feed_keeps_all_source_content(self):
  r=self.r;pane,feed,container,video,*_=self.feed_fixture(vw=1080,vh=1920);dll.test_fit_view(feed);pins=r.val(dll.test_fit_pins(video));self.assertEqual(r.val(pins[3])['setConstant:'],700);self.assertEqual(r.val(pins[2])['setConstant:'],393.75)
 def test_zero_media_size_leaves_native_layout_untouched(self):
  r=self.r;pane,feed,container,video,scroll,native,internal=self.feed_fixture(vw=0,vh=0);dll.test_fit_view(feed);self.assertFalse(dll.test_fit_pins(video));self.assertTrue(r.val(native)['active'])
 def test_video_fit_does_not_change_fullscreen_player(self):
  r=self.r;view=r.new('_TtC6Twitch15VideoPlayerView',{'parent':0,'videoFillsViewBounds':True});dll.test_video_fit(view);self.assertTrue(r.val(view)['videoFillsViewBounds'])
 def test_fit_geometry_never_crops_or_distorts_supported_aspect_ratios(self):
  for vw,vh in [(1920,1080),(1080,1920),(3840,1080),(1080,1080)]:
   for w,h in [(1280,900),(760,700),(320,240),(430,900),(1024,600)]:
    x,y,fw,fh=[dll.test_fit(i,vw,vh,w,h) for i in range(4)];self.assertGreaterEqual(x,0);self.assertGreaterEqual(y,0);self.assertLessEqual(x+fw,w+1e-6);self.assertLessEqual(y+fh,h+1e-6);self.assertAlmostEqual(fw/fh,vw/vh)
 def toolbar_fixture(self,images=0,text=None,enabled=True):
  r=self.r;original=r.new('UIButton',{'children':[],'parent':0,'enabled':enabled});children=r.val(original)['children']
  for _ in range(images):children.append(r.new('UIImageView',{'children':[],'parent':original,'image':r.obj('glyph')}))
  if text:children.append(r.new('UILabel',{'children':[],'parent':original,'text':r.obj(text)}))
  bar=r.new('UIBarButtonItem',{'customView':original,'setHidesSharedBackground:':True});item=r.new('UINavigationItem',{'rightBarButtonItems':r.new('NSArray',[bar])});return item,bar,original
 def test_empty_toolbar_glyph_replaced_once_and_tap_forwarded(self):
  r=self.r;item,bar,original=self.toolbar_fixture();dll.test_normalize(item);replacement=r.val(bar)['customView'];self.assertNotEqual(replacement,original);self.assertTrue(r.val(bar)['hidesBackground']);dll.test_relay(replacement);self.assertEqual(r.val(original)['events'],[64]);dll.test_normalize(item);self.assertEqual(r.val(bar)['customView'],replacement)
 def test_stacked_toolbar_images_normalized_with_original_disabled_state(self):
  r=self.r;item,bar,original=self.toolbar_fixture(images=3,enabled=False);dll.test_normalize(item);replacement=r.val(bar)['customView'];self.assertNotEqual(replacement,original);self.assertFalse(r.val(replacement)['setEnabled:'])
 def test_legitimate_toolbar_icon_and_text_controls_preserved(self):
  r=self.r
  for images,text in [(1,None),(0,'Create')]:
   item,bar,original=self.toolbar_fixture(images,text);dll.test_normalize(item);self.assertEqual(r.val(bar)['customView'],original)
 def test_ad_markers_detected_only_in_playlist_directives(self):
  r=self.r
  for marker in ['#EXT-X-CUE-OUT:30','#EXT-X-DATERANGE:ID="break",CLASS="twitch-stitched-ad"','#EXT-X-DATERANGE:CLASS="twitch-stitched-mid"','#EXT-X-DATERANGE:CLASS="twitch-maf-ad"']:
   self.assertTrue(dll.test_playlist_ads(r.obj('#EXTM3U\n'+marker+'\n#EXTINF:2,\nhttps://video.ttvnw.net/ad.ts')))
  self.assertFalse(dll.test_playlist_ads(r.obj('#EXTM3U\n#EXTINF:2,\nhttps://video.ttvnw.net/processing/stitched-ad-documentary.ts')))
 def test_invalid_hls_and_untrusted_urls_are_rejected(self):
  r=self.r
  for text in ['<html>error</html>','',None]:self.assertFalse(dll.test_playlist_valid(r.obj(text)))
  for u in ['http://video.ttvnw.net/x.m3u8','https://ttvnw.net.attacker.invalid/x','file:///tmp/x','https://ttvnw.net@attacker.invalid/x']:self.assertFalse(dll.test_hls_url(r.new('NSURL',u)))
 def test_variant_selection_skips_audio_only_and_resolves_relative_video(self):
  r=self.r;master=r.obj('#EXTM3U\r\n#EXT-X-STREAM-INF:BANDWIDTH=100000,VIDEO="audio_only"\r\naudio.m3u8\r\n#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080\r\nvideo/1080.m3u8?sig=public\r\n');base=r.new('NSURL','https://video.ttvnw.net/path/master.m3u8');chosen=dll.test_variant(master,base);self.assertEqual(r.val(chosen),'https://video.ttvnw.net/path/video/1080.m3u8?sig=public')
 def test_ad_recovery_preference_independent_of_rewind(self):
  self.assertTrue(dll.test_ad_enabled());self.assertFalse(dll.test_auto());dll.test_save_ad(False);self.assertFalse(dll.test_ad_enabled());dll.test_save_auto(True);self.assertFalse(dll.test_ad_enabled())
 def ad_job(self,clean=True,generation=3):
  r=self.r;job=r.obj({'generation':generation,'login':'example','adDetected':1});r.val(job)['player']=r.new('weak',[r.player]);r.val(job)['polledURL']=r.new('NSURL','https://video.ttvnw.net/current.m3u8')
  if clean:r.val(job)['cleanURL']=r.new('NSURL','https://video.ttvnw.net/clean.m3u8')
  return job
 def test_verified_clean_live_candidate_is_applied_with_cooldown(self):
  r=self.r;r.setup();job=self.ad_job();dll.test_apply_ad(job);self.assertEqual(len(r.loads),1);self.assertEqual(r.val(r.loads[0][2]),'https://video.ttvnw.net/clean.m3u8');self.assertEqual(r.raw(r.state)['adNextProbe'],1045)
 def test_stale_channel_candidate_cannot_switch_current_stream(self):
  r=self.r;r.setup();job=self.ad_job(generation=2);dll.test_apply_ad(job);self.assertEqual(r.loads,[])
 def test_recovery_does_not_resume_paused_video_or_interrupt_rewind(self):
  r=self.r;r.setup();r.val(r.player)['state']=1;dll.test_apply_ad(self.ad_job());self.assertEqual(r.loads,[]);self.assertEqual(r.plays,[])
  r.val(r.player)['state']=3;r.val(r.state)['mode']=r.obj(2);dll.test_apply_ad(self.ad_job());self.assertEqual(r.loads,[])
 def test_disabling_recovery_while_job_pending_prevents_switch(self):
  r=self.r;r.setup();job=self.ad_job();dll.test_save_ad(False);dll.test_apply_ad(job);self.assertEqual(r.loads,[])
 def test_no_clean_candidate_preserves_original_playback(self):
  r=self.r;r.setup();dll.test_apply_ad(self.ad_job(clean=False));self.assertEqual(r.loads,[]);self.assertEqual(r.raw(r.state)['mode'],0)
 def test_poll_jobs_deduplicated_and_failed_probe_backs_off(self):
  r=self.r;r.setup();r.val(r.state)['adRecovery']=r.obj(1);dll.test_update_ad(r.player);dll.test_update_ad(r.player);self.assertEqual(len(r.pending),1)
  job=self.ad_job(clean=False);r.val(job)['failed']=r.obj(1);dll.test_apply_ad(job);self.assertEqual(r.raw(r.state)['adNextProbe'],1015);dll.test_update_ad(r.player);self.assertEqual(len(r.pending),1)
 def test_failed_candidate_restores_original_and_invalidates_inflight_jobs(self):
  r=self.r;r.setup();r.val(r.state).update(adRecovery=r.obj(1),adActiveURL=r.new('NSURL','https://video.ttvnw.net/clean.m3u8'));job=self.ad_job();r.val(r.player)['error']=r.obj('decode error');dll.test_update_ad(r.player);self.assertEqual(r.loads[-1][2],r.liveurl);self.assertEqual(r.raw(r.state)['generation'],4);dll.test_apply_ad(job);self.assertEqual(len(r.loads),1)
 def test_feed_fit_constraints_reactivate_after_view_detachment(self):
  r=self.r;pane,feed,container,video,*_=self.feed_fixture();dll.test_fit_view(feed);pins=r.val(dll.test_fit_pins(video));r.val(feed)['constraints']=r.new('NSArray',pins)
  for pin in pins:r.val(pin)['active']=False
  dll.test_fit_view(feed);self.assertTrue(all(r.val(pin)['active'] for pin in pins));self.assertEqual(len(r.val(dll.test_fit_pins(video))),4)
 def test_gesture_based_toolbar_keeps_its_original_touch_target(self):
  r=self.r;custom=r.new('UIView',{'children':[],'parent':0,'gestureRecognizers':r.new('NSArray',[r.obj('tap')])});bar=r.new('UIBarButtonItem',{'customView':custom});item=r.new('UINavigationItem',{'rightBarButtonItems':r.new('NSArray',[bar])});dll.test_normalize(item);self.assertEqual(r.val(bar)['customView'],custom);cover=r.val(custom)['children'][-1];self.assertFalse(r.val(cover)['interactive']);dll.test_normalize(item);self.assertEqual(len(r.val(custom)['children']),1)
 def test_ended_stream_does_not_restart_from_a_recovery_candidate(self):
  r=self.r;r.setup();r.val(r.player)['state']=4;r.val(r.state)['adRecovery']=r.obj(1);dll.test_update_ad(r.player);self.assertEqual(r.pending,[]);dll.test_apply_ad(self.ad_job());self.assertEqual(r.loads,[]);self.assertEqual(r.plays,[])
 def run_recovery_worker(self,all_ads=False):
  r=self.r;r.setup();r.all_sources_ads=all_ads;job=r.obj({'generation':3,'login':'example'});r.val(job)['player']=r.new('weak',[r.player]);r.val(job)['probeURL']=r.liveurl;dll.test_fetch_ad(job);self.assertEqual(len(r.pending),1);context,callback=r.pending.pop();C.CFUNCTYPE(None,P)(callback)(context);return job
 def test_full_recovery_worker_probes_ad_token_and_clean_variant_before_switch(self):
  r=self.r;self.run_recovery_worker();self.assertEqual(len(r.loads),1);self.assertEqual(r.val(r.loads[0][2]),'https://video.ttvnw.net/clean.m3u8');self.assertEqual(r.last_gql['variables']['kind'],'site');self.assertNotIn('playerType',r.last_gql['variables']);self.assertEqual(len(r.http_requests),5)
 def test_full_recovery_worker_keeps_original_when_every_candidate_contains_ads(self):
  r=self.r;self.run_recovery_worker(True);self.assertEqual(r.loads,[]);self.assertEqual(r.plays,[]);self.assertEqual(r.last_gql['variables']['kind'],'mobile_web');self.assertEqual(len(r.http_requests),11);self.assertEqual(r.raw(r.state)['adNextProbe'],1045)
if __name__=='__main__':unittest.main(verbosity=2)
