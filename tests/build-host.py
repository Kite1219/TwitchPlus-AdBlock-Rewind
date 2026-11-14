from pathlib import Path
import re
r=Path(__file__).resolve().parent;s=(r.parent/'src/NativeRewind.rs').read_text();s=re.sub(r'#\[used\]#\[unsafe\(link_section="__DATA,__mod_init_func"\)\]\s*static INITIALIZE:[^;]+;','',s)
s=re.sub(r'#\[link_name="objc_msgSend"\]fn (\w+)',lambda m:'#[link_name="host_'+m[1]+'"]fn '+m[1],s)
s+='\n'
for i in range(9):s+=f'static mut H{i}:Id=0 as Id;\n'
s+='''type F1=unsafe extern "C" fn(Id)->Id;type F2=unsafe extern "C" fn(Id,Id)->Id;type F5=unsafe extern "C" fn(Id,Id,Id,Id,Id)->Id;type FSet=unsafe extern "C" fn(Id,Id,Id,usize);type FDispatch=unsafe extern "C" fn(Id,Id,Id);type FDouble=unsafe extern "C" fn(Id,Id)->f64;type FMD=unsafe extern "C" fn(Id,Id,f64)->Id;
unsafe fn msg(o:Id,s:Id,a:Id,b:Id,c:Id)->Id{unsafe{transmute::<Id,F5>(H2)(o,s,a,b,c)}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_hook(i:usize,p:Id){unsafe{
'''
for i in range(9):s+=f'if i=={i}'+'{'+f'H{i}=p;'+'}\n'
s+='''OLD_LOAD=host_load as Id;OLD_SOURCE=host_load as Id;}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_state(p:Id,state:Id){unsafe{put(p,&raw const STATE_KEY,state);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_getstate(p:Id)->Id{unsafe{assoc(p,&raw const STATE_KEY)}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_row(row:Id,player:Id){unsafe{put(row,&raw const PLAYER_KEY,weak(player));ROWS=row;PLAYERS=weak(player);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_live(p:Id){unsafe{go_live(p);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_rewind(sender:Id){unsafe{rewind(0 as Id,0 as Id,sender);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_forward(sender:Id){unsafe{forward(0 as Id,0 as Id,sender);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_apply(job:Id){unsafe{apply_recording(job);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_load(p:Id,u:Id,c:Id){unsafe{load(p,s(b"load:configuration:\\0" as *const u8),u,c);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_login(u:Id)->Id{unsafe{login_from_url(u)}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_tick(){unsafe{tick(0 as Id,0 as Id,0 as Id);}}
unsafe extern "C" fn host_load(p:Id,s:Id,u:Id,c:Id){unsafe{msg(p,s,u,c,0 as Id);}}
'''
def export(name,args,ret,body):
 global s
 s+=f'#[unsafe(export_name="{name}")]pub unsafe extern "C" fn stub_{name}({args})->{ret}'+'{unsafe{'+body+'}}\n'
export('objc_getClass','p:Id','Id','transmute::<Id,F1>(H0)(p)')
export('sel_registerName','p:Id','Id','transmute::<Id,F1>(H1)(p)')
export('objc_getAssociatedObject','o:Id,k:Id','Id','transmute::<Id,F2>(H3)(o,k)')
export('objc_setAssociatedObject','o:Id,k:Id,v:Id,p:usize','()','transmute::<Id,FSet>(H4)(o,k,v,p);')
export('dispatch_async_f','q:Id,c:Id,f:Id','()','transmute::<Id,FDispatch>(H5)(q,c,f);')
for n in ['m0','m1','m2','m3','mu','count','b1','mb','title','action','md','double','time','seek','timer']:
 signatures={'m0':('o:Id,s:Id','Id','msg(o,s,0 as Id,0 as Id,0 as Id)'), 'm1':('o:Id,s:Id,a:Id','Id','msg(o,s,a,0 as Id,0 as Id)'), 'm2':('o:Id,s:Id,a:Id,b:Id','Id','msg(o,s,a,b,0 as Id)'), 'm3':('o:Id,s:Id,a:Id,b:Id,c:Id','Id','msg(o,s,a,b,c)'), 'mu':('o:Id,s:Id,a:usize','Id','msg(o,s,a as Id,0 as Id,0 as Id)'), 'count':('o:Id,s:Id','usize','msg(o,s,0 as Id,0 as Id,0 as Id) as usize'), 'b1':('o:Id,s:Id,a:Id','bool','msg(o,s,a,0 as Id,0 as Id)!=0 as Id'), 'mb':('o:Id,s:Id,a:bool','Id','msg(o,s,a as usize as Id,0 as Id,0 as Id)'), 'title':('o:Id,s:Id,a:Id,b:usize','Id','msg(o,s,a,b as Id,0 as Id)'), 'action':('o:Id,s:Id,a:Id,b:Id,c:usize','Id','msg(o,s,a,b,c as Id)'), 'md':('o:Id,s:Id,a:f64','Id','transmute::<Id,FMD>(H7)(o,s,a)'), 'double':('o:Id,s:Id','f64','transmute::<Id,FDouble>(H6)(o,s)'), 'time':('o:Id,s:Id','CMTime','stub_CMTimeMakeWithSeconds(transmute::<Id,FDouble>(H6)(o,s),600)'), 'seek':('o:Id,s:Id,t:CMTime','()','transmute::<Id,FMD>(H8)(o,s,stub_CMTimeGetSeconds(t));'), 'timer':('o:Id,s:Id,t:f64,a:Id,b:Id,c:Id,d:bool','Id','0 as Id')}
 export('host_'+n,*signatures[n])
export('CMTimeMakeWithSeconds','v:f64,_:i32','CMTime','CMTime{value:(v*600.0) as i64,scale:600,flags:1,epoch:0}')
export('CMTimeGetSeconds','t:CMTime','f64','t.value as f64/600.0')
for n,args,ret,result in [('objc_allocateClassPair','_:Id,_:Id,_:usize','Id','0 as Id'),('objc_registerClassPair','_:Id','()',''),('object_getClass','_:Id','Id','0 as Id'),('method_getImplementation','_:Id','Id','0 as Id'),('method_setImplementation','_:Id,_:Id','Id','0 as Id'),('class_getInstanceVariable','_:Id,_:Id','Id','0 as Id'),('ivar_getOffset','_:Id','usize','0'),('dlsym','_:Id,_:Id','Id','0 as Id'),('dispatch_get_global_queue','_:usize,_:usize','Id','0 as Id')]:export(n,args,ret,result)
export('host_rect','o:Id,_:Id','Rect','Rect{origin:Point{x:transmute::<Id,FDouble>(H6)(o,s(b"testX\\0" as *const u8)),y:transmute::<Id,FDouble>(H6)(o,s(b"testY\\0" as *const u8))},size:Size{width:transmute::<Id,FDouble>(H6)(o,s(b"testWidth\\0" as *const u8)),height:transmute::<Id,FDouble>(H6)(o,s(b"testHeight\\0" as *const u8))}}')
export('host_font2','o:Id,s:Id,size:f64,weight:f64','Id','msg(o,s,0 as Id,0 as Id,0 as Id)')
export('host_rgba','o:Id,s:Id,r:f64,g:f64,b:f64,a:f64','Id','msg(o,s,0 as Id,0 as Id,0 as Id)')
export('host_mf','o:Id,s:Id,a:f32','Id','transmute::<Id,FMD>(H7)(o,s,a as f64)')
export('host_float','o:Id,s:Id','f32','transmute::<Id,FDouble>(H6)(o,s) as f32')
export('host_b0','o:Id,s:Id','bool','msg(o,s,0 as Id,0 as Id,0 as Id)!=0 as Id')
export('host_anchor','o:Id,s:Id,a:Id,c:f64','Id','msg(o,s,a,0 as Id,0 as Id)')
export('class_getInstanceMethod','c:Id,sel:Id','Id','msg(c,s(b"hostGetMethod\\0" as *const u8),sel,0 as Id,0 as Id)')
export('method_getTypeEncoding','m:Id','Id','msg(m,s(b"hostTypeEncoding\\0" as *const u8),0 as Id,0 as Id,0 as Id)')
export('class_addMethod','c:Id,sel:Id,imp:Id,enc:Id','bool','msg(c,s(b"hostAddMethod\\0" as *const u8),sel,imp,enc)!=0 as Id')
export('host_convert_rect','o:Id,_:Id,r:Rect,to:Id','Rect','Rect{origin:Point{x:transmute::<Id,FDouble>(H6)(o,s(b"testX\\0" as *const u8)),y:transmute::<Id,FDouble>(H6)(o,s(b"testY\\0" as *const u8))},size:r.size}')
export('host_set_bool','o:Id,sel:Id,v:bool,k:Id','()','msg(o,sel,v as usize as Id,k,0 as Id);')
export('host_present','o:Id,sel:Id,vc:Id,animated:bool,c:Id','()','msg(o,sel,vc,animated as usize as Id,c);')
export('host_dismiss','o:Id,sel:Id,animated:bool,c:Id','()','msg(o,sel,animated as usize as Id,c,0 as Id);')
s+='static mut HOST_NOW:f64=1000.0;\n'
export('CFAbsoluteTimeGetCurrent','','f64','HOST_NOW')
s+='''#[unsafe(no_mangle)]pub unsafe extern "C" fn test_scrub(sender:Id){unsafe{scrub(0 as Id,0 as Id,sender);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_prefetch(player:Id){unsafe{prefetch(player);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_attach(controls:Id){unsafe{attach(controls);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_bar(row:Id,slider:Id,label:Id,live:Id){unsafe{put(row,&raw const SLIDER_KEY,slider);put(row,&raw const LABEL_KEY,label);put(row,&raw const LIVE_KEY,live);}}
'''
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_preview(sender:Id){unsafe{preview(0 as Id,0 as Id,sender);}}\n#[unsafe(no_mangle)]pub unsafe extern "C" fn test_clock(t:f64)->Id{unsafe{clock(t)}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_badge(row:Id,badge:Id){unsafe{put(row,&raw const BADGE_KEY,badge);}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_now(t:f64){unsafe{HOST_NOW=t;}}\n#[unsafe(no_mangle)]pub unsafe extern "C" fn test_ready(state:Id,target:f64)->Id{unsafe{prepared_source(state,target)}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_spec(i:usize,w:f64,h:f64)->f64{let v=responsive(w,h);if i==0{return v.padding;}if i==1{return v.bottom;}if i==2{return v.skip;}if i==3{return if v.visible{1.0}else{0.0};}if v.sides{1.0}else{0.0}}\n' 
s+='\n#[unsafe(no_mangle)]pub static _fltused:i32=0;\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_update(p:Id){unsafe{update_playback(p);}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_install(c:Id){unsafe{install_horizontal_bars(c);}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_find(v:Id)->Id{unsafe{find_player(v,0)}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_auto()->bool{unsafe{auto_enabled()}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_save_auto(v:bool){unsafe{save_auto(v);}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_settings_load(v:Id){unsafe{settings_load(v,0 as Id);}}\n'
s+='#[unsafe(no_mangle)]pub unsafe extern "C" fn test_configure_tabs(v:Id){unsafe{configure_tabs(v);}}\n'
(r/'NativeRewind-host.rs').write_text(s)
