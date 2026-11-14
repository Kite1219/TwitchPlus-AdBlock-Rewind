#include "AppleRuntime.h"
#include "../build/PlaylistEngine.inc"

// Independent implementation. Pie was inspected as a protocol reference; no
// extension code, proxy credentials, or extension assets are bundled here.
static NSMutableDictionary *TPMappings,*TPChannels,*TPStats;
static NSURLSession *TPNetwork;
static NSObject *TPLock;
static JSContext *TPJS;
static char TPTaskKey;
static void (*TPOldData)(id,SEL,id,id,id);
static void (*TPOldComplete)(id,SEL,id,id,id);
static NSString *const TPEnabledKey=@"TwitchPlusNativeAdRecoveryEnabled";
static NSString *const TPCompactKey=@"TwitchPlusCompactWidePhone";

static void TPCount(NSString *key) {
    @synchronized(TPLock) { TPStats[key]=@([TPStats[key] unsignedIntegerValue]+1); }
}
static BOOL TPEnabled(void) {
    NSUserDefaults *d=[NSUserDefaults standardUserDefaults];
    return ![d objectForKey:TPEnabledKey] || [d boolForKey:TPEnabledKey];
}
static BOOL TPAllowed(NSURL *URL) {
    NSString *host=URL.host.lowercaseString;
    return [URL.scheme.lowercaseString isEqualToString:@"https"] &&
           ([host isEqualToString:@"ttvnw.net"] || [host hasSuffix:@".ttvnw.net"]);
}
static NSString *TPLogin(NSURL *URL) {
    if(!TPAllowed(URL) || ![URL.host.lowercaseString isEqualToString:@"usher.ttvnw.net"]) return nil;
    NSString *path=URL.path;
    if(!([path hasPrefix:@"/api/channel/hls/"] || [path hasPrefix:@"/api/v2/channel/hls/"]) ||
       ![URL.pathExtension isEqualToString:@"m3u8"]) return nil;
    NSString *name=[URL.lastPathComponent substringToIndex:URL.lastPathComponent.length-5];
    const char *p=name.UTF8String; NSUInteger n=name.length;
    if(!n || n>25) return nil;
    for(NSUInteger i=0;i<n;i++) if(!((p[i]>='a'&&p[i]<='z') || (p[i]>='A'&&p[i]<='Z') ||
                                    (p[i]>='0'&&p[i]<='9') || p[i]=='_')) return nil;
    return name.lowercaseString;
}
static NSString *TPText(NSData *data) {
    if(!tp_hls_valid(data.bytes,data.length)) return nil;
    return [[NSString alloc] initWithData:data encoding:4];
}
static id TPJSCall(NSString *method,NSArray *arguments) {
    @synchronized(TPLock) {
        if(!TPJS) return nil;
        TPJS.exception=nil;
        JSValue *function=[[TPJS objectForKeyedSubscript:@"TPPlaylistEngine"] objectForKeyedSubscript:method];
        id result=[[function callWithArguments:arguments] toObject];
        if(TPJS.exception) { TPCount(@"engineErrors"); TPJS.exception=nil; return nil; }
        return result;
    }
}
static NSString *TPAttribute(NSString *line,NSString *name) {
    NSRange key=[line rangeOfString:[name stringByAppendingString:@"="]];
    if(key.location==NSNotFound) return nil;
    NSString *tail=[line substringFromIndex:key.location+key.length];
    if([tail hasPrefix:@"\""]) {
        tail=[tail substringFromIndex:1]; NSRange end=[tail rangeOfString:@"\""];
        return end.location==NSNotFound?nil:[tail substringToIndex:end.location];
    }
    return [tail componentsSeparatedByString:@","][0];
}
static NSURL *TPAbsolute(NSString *line,NSURL *base) {
    NSURL *result=[NSURL URLWithString:line relativeToURL:base].absoluteURL;
    return TPAllowed(result)?result:nil;
}
static NSMutableDictionary *TPContext(NSString *login,NSURL *masterURL) {
    @synchronized(TPLock) {
        NSMutableDictionary *context=TPChannels[login];
        BOOL same=NO;
        @synchronized(context) { same=[context[@"masterURL"] isEqualToString:masterURL.absoluteString]; }
        if(!context || !same) {
            // Prevent unlimited growth when browsing many channels / qualities.
            if(TPChannels.count>=24 || TPMappings.count>=2048) {
                [TPChannels removeAllObjects]; [TPMappings removeAllObjects];
            }
            context=[NSMutableDictionary dictionary]; context[@"login"]=login;
            context[@"identity"]=[[NSUUID UUID] UUIDString];
            context[@"masterURL"]=masterURL.absoluteString; context[@"enabled"]=@(TPEnabled());
            context[@"device"]=[[[NSUUID UUID] UUIDString] stringByReplacingOccurrencesOfString:@"-" withString:@""].lowercaseString;
            TPChannels[login]=context;
        }
        return context;
    }
}
static NSDictionary *TPMapping(NSURL *URL) {
    @synchronized(TPLock) { return TPMappings[URL.absoluteString]; }
}
static void TPRecordMaster(NSString *text,NSURL *base,NSMutableDictionary *context) {
    NSString *attributes=nil;
    for(NSString *raw in [text componentsSeparatedByString:@"\n"]) {
        NSString *line=[raw stringByReplacingOccurrencesOfString:@"\r" withString:@""];
        if([line hasPrefix:@"#EXT-X-STREAM-INF:"]) { attributes=line; continue; }
        if(!attributes || !line.length || [line hasPrefix:@"#"]) continue;
        NSURL *URL=TPAbsolute(line,base);
        if(URL && TPAttribute(attributes,@"RESOLUTION")) {
            NSDictionary *mapping=@{@"context":context,@"attributes":attributes,@"key":URL.absoluteString};
            @synchronized(TPLock) { TPMappings[URL.absoluteString]=mapping; }
        }
        attributes=nil;
    }
}
static NSData *TPFetch(NSURL *URL,NSDictionary *payload,NSString *device) {
    BOOL gql=[URL.absoluteString isEqualToString:@"https://gql.twitch.tv/gql"];
    if(!gql && !TPAllowed(URL)) return nil;
    NSMutableURLRequest *request=[NSMutableURLRequest requestWithURL:URL];
    request.timeoutInterval=2.0; request.HTTPShouldHandleCookies=NO;
    [request setValue:@"Mozilla/5.0" forHTTPHeaderField:@"User-Agent"];
    if(gql) {
        request.HTTPMethod=@"POST";
        request.HTTPBody=[NSJSONSerialization dataWithJSONObject:payload options:0 error:0];
        [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
        [request setValue:@"kimne78kx3ncx6brgo4mv6wki5h1ko" forHTTPHeaderField:@"Client-ID"];
        [request setValue:device forHTTPHeaderField:@"X-Device-Id"];
        [request setValue:@"https://www.twitch.tv" forHTTPHeaderField:@"Origin"];
    }
    dispatch_semaphore_t done=dispatch_semaphore_create(0);
    TPDispatchRetain(done); // ARC captures ownership in the SDK build.
    __block NSData *body=nil;
    NSURLSessionTask *task=[TPNetwork dataTaskWithRequest:request completionHandler:^(NSData *data,NSURLResponse *response,NSError *error) {
        if(!error && [(NSHTTPURLResponse *)response statusCode]==200 && data.length<=1048576 &&
           (gql || TPAllowed(response.URL))) body=data;
        dispatch_semaphore_signal(done);
        TPDispatchRelease(done);
    }];
    [task resume];
    BOOL timeout=dispatch_semaphore_wait(done,dispatch_time(0,2400000000LL))!=0;
    if(timeout) [task cancel];
    TPDispatchRelease(done);
    if(timeout) { TPCount(@"networkTimeouts"); return nil; }
    return body;
}
static NSURL *TPMaster(NSMutableDictionary *context,NSString *kind) {
    NSDictionary *metadata=nil;
    @synchronized(context) { metadata=[context copy]; }
    NSString *platform=[kind isEqualToString:@"autoplay"]?@"android":@"web";
    NSDictionary *payload=@{
        @"operationName":@"TwitchPlusNativeToken",
        @"query":@"query TwitchPlusNativeToken($tp_login:String!,$tp_kind:String!,$tp_platform:String!){streamPlaybackAccessToken(channelName:$tp_login,params:{platform:$tp_platform,playerBackend:\"mediaplayer\",playerType:$tp_kind}){signature value}}",
        @"variables":@{@"tp_login":metadata[@"login"],@"tp_kind":kind,@"tp_platform":platform}};
    NSData *bytes=TPFetch([NSURL URLWithString:@"https://gql.twitch.tv/gql"],payload,metadata[@"device"]);
    if(!bytes) return nil;
    id result=[NSJSONSerialization JSONObjectWithData:bytes options:0 error:0];
    if(![result isKindOfClass:[NSDictionary class]]) return nil;
    id data=result[@"data"]; if(![data isKindOfClass:[NSDictionary class]]) return nil;
    id token=data[@"streamPlaybackAccessToken"]; if(![token isKindOfClass:[NSDictionary class]]) return nil;
    NSString *signature=token[@"signature"],*access=token[@"value"];
    if(![signature isKindOfClass:[NSString class]] || ![access isKindOfClass:[NSString class]]) return nil;
    NSURLComponents *parts=[NSURLComponents new]; parts.scheme=@"https"; parts.host=@"usher.ttvnw.net";
    parts.path=[NSString stringWithFormat:@"/api/channel/hls/%@.m3u8",metadata[@"login"]];
    parts.queryItems=@[[NSURLQueryItem queryItemWithName:@"sig" value:signature],
        [NSURLQueryItem queryItemWithName:@"token" value:access],
        [NSURLQueryItem queryItemWithName:@"allow_source" value:@"true"],
        [NSURLQueryItem queryItemWithName:@"allow_audio_only" value:@"false"],
        [NSURLQueryItem queryItemWithName:@"playlist_include_framerate" value:@"true"],
        [NSURLQueryItem queryItemWithName:@"player_type" value:kind]];
    return parts.URL;
}
static NSDictionary *TPVariant(NSString *master,NSURL *base,NSString *wanted) {
    id selected=TPJSCall(@"variant",@[master,wanted]);
    if(![selected isKindOfClass:[NSDictionary class]]) return nil;
    NSURL *URL=TPAbsolute(selected[@"url"],base);
    return URL?@{@"url":URL,@"attributes":selected[@"attributes"]}:nil;
}
static NSURL *TPResolved(NSString *line,NSURL *base,BOOL strict) {
    NSURL *URL=[NSURL URLWithString:line relativeToURL:base].absoluteURL;
    if(![URL.scheme.lowercaseString isEqualToString:@"https"]) return nil;
    return !strict || TPAllowed(URL)?URL:nil;
}
static NSString *TPRebase(NSString *text,NSURL *base,BOOL strict) {
    NSMutableArray *lines=[NSMutableArray array];
    for(NSString *raw in [text componentsSeparatedByString:@"\n"]) {
        NSString *line=[raw stringByReplacingOccurrencesOfString:@"\r" withString:@""];
        if(line.length && ![line hasPrefix:@"#"]) {
            NSURL *URL=TPResolved(line,base,strict); if(!URL) return nil;
            line=URL.absoluteString;
        } else {
            // Resolve KEY/MAP/PART/PRELOAD-HINT URI attributes against the backup,
            // not against the URL of the intercepted original response.
            NSMutableString *rebased=[NSMutableString string]; NSString *rest=line;
            while(YES) {
                NSRange marker=[rest rangeOfString:@"URI=\""];
                if(marker.location==NSNotFound) { [rebased appendString:rest]; break; }
                NSUInteger start=marker.location+marker.length;
                NSString *tail=[rest substringFromIndex:start]; NSRange end=[tail rangeOfString:@"\""];
                if(end.location==NSNotFound) return nil;
                NSURL *URL=TPResolved([tail substringToIndex:end.location],base,strict); if(!URL) return nil;
                [rebased appendString:[rest substringToIndex:start]]; [rebased appendString:URL.absoluteString];
                rest=[tail substringFromIndex:end.location];
            }
            line=rebased;
        }
        [lines addObject:line];
    }
    return [lines componentsJoinedByString:@"\n"];
}
static NSDictionary *TPCleanSource(NSMutableDictionary *context,NSString *attributes) {
    // Parallel attempts have an overall deadline. Only Twitch HTTPS endpoints are
    // contacted, using anonymous tokens and an isolated session without cookies.
    NSMutableDictionary *search=[NSMutableDictionary dictionary];
    dispatch_group_t group=dispatch_group_create();
    for(NSString *kind in @[@"popout",@"mobile_web",@"autoplay"]) {
        dispatch_group_async(group,dispatch_get_global_queue(0,0),^{ @autoreleasepool {
            NSURL *masterURL=TPMaster(context,kind);
            NSString *master=masterURL?TPText(TPFetch(masterURL,nil,nil)):nil;
            NSDictionary *choice=master?TPVariant(master,masterURL,attributes):nil;
            NSURL *variant=choice[@"url"];
            NSString *media=variant?TPText(TPFetch(variant,nil,nil)):nil;
            if(media && [TPJSCall(@"eligible",@[media]) boolValue]) {
                NSString *rebased=TPRebase(media,variant,YES);
                if(rebased) @synchronized(search) {
                    if(!search[@"closed"] && (!search[@"body"] || ![kind isEqualToString:@"autoplay"])) {
                        search[@"body"]=rebased; search[@"url"]=variant; search[@"type"]=kind;
                        search[@"attributes"]=choice[@"attributes"];
                    }
                }
            }
        }});
    }
    dispatch_group_wait(group,dispatch_time(0,5200000000LL));
    NSDictionary *result=nil;
    @synchronized(search) {
        search[@"closed"]=@YES;
        if(search[@"body"]) @synchronized(context) {
            context[@"backupURL"]=search[@"url"]; context[@"backupAttributes"]=attributes;
            context[@"backupType"]=search[@"type"];
            context[@"backupActualAttributes"]=search[@"attributes"];
            result=@{@"body":search[@"body"],@"attributes":search[@"attributes"],@"source":search[@"url"]};
        }
    }
    // libdispatch retains an in-flight group for its work items.
    TPDispatchRelease(group);
    return result;
}
static NSData *TPTransform(NSData *body,NSURL *URL,NSDictionary *mapping,NSString *login) {
    NSString *text=TPText(body); if(!text) return body;
    if(login && [text containsString:@"#EXT-X-STREAM-INF:"]) {
        TPRecordMaster(text,URL,TPContext(login,URL)); TPCount(@"masters"); return body;
    }
    if(!mapping || ![text containsString:@"#EXTINF:"]) return body;
    TPCount(@"mediaResponses");
    NSMutableDictionary *context=mapping[@"context"];
    NSDictionary *metadata=nil;
    @synchronized(context) { metadata=[context copy]; }
    if(![metadata[@"enabled"] boolValue]) return body;
    NSString *rebased=TPRebase(text,URL,NO);
    if(!rebased) { TPCount(@"rebaseBypass"); return body; }
    NSDictionary *inspection=TPJSCall(@"inspect",@[metadata[@"identity"],mapping[@"key"],mapping[@"attributes"],rebased]);
    if(![inspection isKindOfClass:[NSDictionary class]]) { TPCount(@"engineBypass"); return body; }
    if([inspection[@"unsupported"] boolValue]) { TPCount(@"unsupportedFormatBypass"); return body; }
    BOOL needsBackup=[inspection[@"needsBackup"] boolValue];
    if(needsBackup) TPCount(@"adResponses");
    // A response filter never calls play(), seeks, or reloads the player.
    // Paused streams stay paused, including requests already in flight.
    if(needsBackup && [NSThread isMainThread]) { TPCount(@"mainThreadBypass"); return body; }
    NSDictionary *replacement=nil; NSURL *cached=nil; NSString *cachedAttributes=nil;
    if(needsBackup) @synchronized(context) {
        if([context[@"backupAttributes"] isEqualToString:mapping[@"attributes"]]) cached=context[@"backupURL"];
        cachedAttributes=context[@"backupActualAttributes"];
    }
    if(cached) {
        NSString *media=TPText(TPFetch(cached,nil,nil));
        if(media && [TPJSCall(@"eligible",@[media]) boolValue]) {
            NSString *clean=TPRebase(media,cached,YES);
            if(clean) replacement=@{@"body":clean,@"attributes":cachedAttributes,@"source":cached};
        }
    }
    if(needsBackup && !replacement) {
        NSTimeInterval now=[NSDate timeIntervalSinceReferenceDate]; BOOL search=NO;
        @synchronized(context) {
            if(![context[@"busy"] boolValue] && now>=[context[@"retryAfter"] doubleValue]) {
                context[@"busy"]=@YES; search=YES;
            }
        }
        if(search) {
            replacement=TPCleanSource(context,mapping[@"attributes"]);
            @synchronized(context) {
                context[@"busy"]=@NO;
                context[@"retryAfter"]=@([NSDate timeIntervalSinceReferenceDate]+(replacement?0:15));
            }
        }
    }
    NSDictionary *rendered=TPJSCall(@"process",@[metadata[@"identity"],mapping[@"key"],mapping[@"attributes"],rebased,text,
        replacement[@"body"]?:@"",replacement[@"attributes"]?:@"",[replacement[@"source"] absoluteString]?:@""]);
    if(![rendered isKindOfClass:[NSDictionary class]] || ![rendered[@"body"] isKindOfClass:[NSString class]]) return body;
    if([rendered[@"noSource"] boolValue]) TPCount(@"noCleanSource");
    if([rendered[@"held"] boolValue]) TPCount(@"heldResponses");
    if([rendered[@"backup"] boolValue]) TPCount(@"substitutedResponses");
    return [rendered[@"body"] dataUsingEncoding:4];
}
static void TPData(id self,SEL selector,NSURLSession *session,NSURLSessionTask *task,NSData *data) {
    NSMutableDictionary *slot=objc_getAssociatedObject(task,&TPTaskKey);
    if(!slot) {
        NSURL *URL=task.currentRequest.URL?:task.originalRequest.URL;
        NSString *login=TPLogin(URL)?:TPLogin(task.originalRequest.URL);
        NSDictionary *mapping=TPMapping(URL)?:TPMapping(task.originalRequest.URL);
        if(!TPAllowed(URL) || (!login && !mapping) || [(NSHTTPURLResponse *)task.response statusCode]!=200) {
            TPOldData(self,selector,session,task,data); return;
        }
        slot=[NSMutableDictionary dictionary]; slot[@"body"]=[NSMutableData data]; slot[@"url"]=URL;
        if(login) slot[@"login"]=login; if(mapping) slot[@"mapping"]=mapping;
        objc_setAssociatedObject(task,&TPTaskKey,slot,1);
    }
    NSMutableData *buffer=slot[@"body"];
    if([slot[@"passthrough"] boolValue]) { TPOldData(self,selector,session,task,data); return; }
    if(!tp_buffer_fits(buffer.length,data.length,1048576)) {
        if(buffer.length) TPOldData(self,selector,session,task,buffer);
        slot[@"passthrough"]=@YES; [slot removeObjectForKey:@"body"];
        TPCount(@"oversizedBypass"); TPOldData(self,selector,session,task,data); return;
    }
    [buffer appendData:data];
}
static void TPComplete(id self,SEL selector,NSURLSession *session,NSURLSessionTask *task,NSError *error) {
    NSDictionary *slot=objc_getAssociatedObject(task,&TPTaskKey);
    objc_setAssociatedObject(task,&TPTaskKey,nil,1);
    if(slot && ![slot[@"passthrough"] boolValue] && !error) {
        // Keep slow backup requests off IVS's serial delegate queue. Other
        // segment/audio tasks can complete while this manifest is transformed.
        dispatch_async(dispatch_get_global_queue(0,0),^{ @autoreleasepool {
            NSData *result=TPTransform(slot[@"body"],slot[@"url"],slot[@"mapping"],slot[@"login"]);
            [session.delegateQueue addOperationWithBlock:^{
                if(result.length) TPOldData(self,@selector(URLSession:dataTask:didReceiveData:),session,task,result);
                TPOldComplete(self,selector,session,task,nil);
            }];
        }});
        return;
    }
    TPOldComplete(self,selector,session,task,error);
}

// Layout implementation follows below; all UIKit work runs on the main thread.
static NSHashTable *TPRoots;
static char TPPinsKey,TPPinParentKey,TPCompactAppliedKey,TPVideoSizeKey;
static void (*TPOldFeedLayout)(id,SEL),(*TPOldVideoLayout)(id,SEL),(*TPOldRootLayout)(id,SEL),(*TPOldTheaterLayout)(id,SEL);
static void (*TPOldDiscoveryLayout)(id,SEL);
static NSString *TPGeometry=@"No feed layout observed yet";
static NSString *TPTheaterGeometry=@"No theater layout observed yet";

static id TPField(id object,const char *name) {
    if(!object) return nil;
    Ivar ivar=class_getInstanceVariable(object_getClass(object),name);
    if(!ivar) return nil;
    return object_getIvar(object,ivar);
}
static CGSize TPVideoSize(id feed) {
    Ivar ivar=class_getInstanceVariable(object_getClass(feed),"videoSize");
    return ivar?*(CGSize *)((char *)(__bridge void *)feed+ivar_getOffset(ivar)):(CGSize){0,0};
}
static BOOL TPKind(id object,const char *name) { return object && [object isKindOfClass:objc_getClass(name)]; }
static BOOL TPWidePhone(UIWindow *window) {
    // Use the window's system trait, unaffected by a child controller override.
    // Fold/unfold and display scaling require no guessed screen dimensions.
    return [UIDevice currentDevice].userInterfaceIdiom==0 && window && window.traitCollection.horizontalSizeClass==2;
}
static BOOL TPCompactEnabled(void) {
    NSUserDefaults *defaults=[NSUserDefaults standardUserDefaults];
    return ![defaults objectForKey:TPCompactKey] || [defaults boolForKey:TPCompactKey];
}
static void TPApplyCompact(UIViewController *root) {
    if(![root respondsToSelector:@selector(traitOverrides)]) return;
    BOOL apply=TPWidePhone(root.view.window) && TPCompactEnabled();
    if(apply && !objc_getAssociatedObject(root,&TPCompactAppliedKey)) {
        objc_setAssociatedObject(root,&TPCompactAppliedKey,@YES,1);
        root.traitOverrides.horizontalSizeClass=1; TPCount(@"compactApplied");
    } else if(!apply && objc_getAssociatedObject(root,&TPCompactAppliedKey)) {
        Class trait=objc_getClass("UITraitHorizontalSizeClass");
        if(trait && [root.traitOverrides respondsToSelector:@selector(removeTrait:)]) {
            objc_setAssociatedObject(root,&TPCompactAppliedKey,nil,1); [root.traitOverrides removeTrait:trait];
        }
    }
}
static void TPRootLayout(UIViewController *self,SEL selector) {
    [TPRoots addObject:self]; TPApplyCompact(self); TPOldRootLayout(self,selector);
}
static BOOL TPDescendant(id item,UIView *view) {
    // Only external placement constraints are changed; internal rendering and
    // scroll-view constraints must stay owned by the application.
    if([item isKindOfClass:[UILayoutGuide class]]) item=[item owningView];
    if(![item isKindOfClass:[UIView class]]) return NO;
    UIView *child=item;
    for(NSUInteger depth=0;child && depth<32;depth++,child=child.superview) if(child==view) return YES;
    return NO;
}
static BOOL TPInternalLayoutItem(id item,UIView *view) {
    if([item isKindOfClass:[UILayoutGuide class]]) return TPDescendant(item,view);
    return item!=view && TPDescendant(item,view);
}
static void TPPlace(UIView *view,UIView *container,CGRect fitted,BOOL horizontalOnly) {
    if(!tp_rect_valid(fitted)) return;
    NSArray *pins=objc_getAssociatedObject(view,&TPPinsKey);
    NSHashTable *parents=objc_getAssociatedObject(view,&TPPinParentKey);
    NSArray *liveParents=parents.allObjects;
    UIView *previous=liveParents.count?liveParents[0]:nil;
    if(previous!=container && pins) { [NSLayoutConstraint deactivateConstraints:pins]; pins=nil; }
    for(UIView *owner=view;owner;owner=owner.superview) {
        // Snapshot because deactivation changes the owning view's collection.
        NSArray *constraints=[owner.constraints copy];
        for(NSLayoutConstraint *constraint in constraints) {
            if([pins containsObject:constraint]) continue;
            id first=constraint.firstItem,second=constraint.secondItem;
            if(first!=view && second!=view) continue;
            id other=first==view?second:first;
            NSInteger attribute=first==view?constraint.firstAttribute:constraint.secondAttribute;
            BOOL horizontal=(attribute==1 || attribute==2 || attribute==5 || attribute==6 || attribute==7 || attribute==9);
            if((!horizontalOnly || horizontal) && !TPInternalLayoutItem(other,view)) constraint.active=NO;
        }
        if(owner==container) break;
    }
    if(!pins) {
        view.translatesAutoresizingMaskIntoConstraints=NO;
        NSLayoutConstraint *left=[view.centerXAnchor constraintEqualToAnchor:container.centerXAnchor constant:0];
        NSLayoutConstraint *width=[view.widthAnchor constraintEqualToConstant:fitted.size.width];
        if(horizontalOnly) pins=@[left,width];
        else pins=@[left,width,[view.centerYAnchor constraintEqualToAnchor:container.centerYAnchor constant:0],
                    [view.heightAnchor constraintEqualToConstant:fitted.size.height]];
        objc_setAssociatedObject(view,&TPPinsKey,pins,1);
        // Parent already retains its child. Avoid a child->parent retention cycle.
        NSHashTable *weak=[NSHashTable weakObjectsHashTable]; [weak addObject:container];
        objc_setAssociatedObject(view,&TPPinParentKey,weak,1);
    }
    CGRect bounds=container.bounds;
    double values[4]={fitted.origin.x+fitted.size.width*.5-bounds.origin.x-bounds.size.width*.5,
        fitted.size.width,fitted.origin.y+fitted.size.height*.5-bounds.origin.y-bounds.size.height*.5,fitted.size.height};
    for(NSUInteger i=0;i<pins.count;i++) {
        NSLayoutConstraint *pin=pins[i]; if(pin.constant!=values[i]) pin.constant=values[i];
        if(!pin.active) pin.active=YES;
    }
}
static UIView *TPFeedAncestor(UIView *view) {
    for(NSUInteger depth=0;view && depth<24;depth++,view=view.superview)
        if(TPKind(view,"_TtC6Twitch14FeedPlayerView")) return view;
    return nil;
}
static void TPAspect(UIView *video) {
    Ivar flag=class_getInstanceVariable(object_getClass(video),"videoFillsViewBounds");
    if(flag) *(unsigned char *)((char *)(__bridge void *)video+ivar_getOffset(flag))=0;
    UIView *layerView=TPField(video,"playerLayerView"); id layer=layerView.layer;
    if([layer respondsToSelector:@selector(setVideoGravity:)]) {
        // NSObject dynamic dispatch through a declared selector, no guessed ivar
        // layout for IVSPlayerLayer or its internal rendering objects.
        void (*send)(id,SEL,id)=(void *)dlsym((void *)(intptr_t)-2,"objc_msgSend");
        id (*get)(id,SEL)=(void *)dlsym((void *)(intptr_t)-2,"objc_msgSend");
        if(send && get && ![get(layer,@selector(videoGravity)) isEqual:@"AVLayerVideoGravityResizeAspect"])
            send(layer,@selector(setVideoGravity:),@"AVLayerVideoGravityResizeAspect");
    }
    UIScrollView *scroll=TPField(video,"scrollView");
    NSString *size=[NSString stringWithFormat:@"%.2f:%.2f",video.bounds.size.width,video.bounds.size.height];
    if(![objc_getAssociatedObject(video,&TPVideoSizeKey) isEqual:size]) {
        if([scroll isKindOfClass:[UIScrollView class]]) scroll.zoomScale=1;
        objc_setAssociatedObject(video,&TPVideoSizeKey,size,1);
    }
}
static CGRect TPSidebarClip(UIView *root,UIView *container,CGRect area,NSUInteger depth,NSUInteger *budget) {
    if(!root || depth>18 || !*budget || root.hidden || root.alpha<.05) return area;
    (*budget)--;
    if(root!=container && !TPDescendant(container,root)) {
        NSString *name=[NSString stringWithUTF8String:class_getName(object_getClass(root))];
        if([name containsString:@"Sidebar"] || [name containsString:@"SideBar"]) {
            CGRect box=[root convertRect:root.bounds toView:container];
            if(tp_rect_valid(box) && box.size.width>=120 && box.size.width<=container.window.bounds.size.width*.48 &&
               box.size.height>=container.window.bounds.size.height*.5 && box.origin.x<=area.origin.x+2 &&
               box.origin.x+box.size.width>area.origin.x) {
                double edge=box.origin.x+box.size.width;
                area.size.width-=edge-area.origin.x; area.origin.x=edge;
            }
        }
    }
    for(UIView *child in root.subviews) area=TPSidebarClip(child,container,area,depth+1,budget);
    return area;
}
static void TPFeedLayout(UIView *self,SEL selector) {
    TPOldFeedLayout(self,selector); TPCount(@"feedLayouts");
    UIView *container=TPField(self,"playerContainerView"),*video=TPField(self,"playerView");
    if(![container isKindOfClass:[UIView class]] || !TPKind(video,"_TtC6Twitch15VideoPlayerView") ||
       video.superview!=container || !container.window) { TPCount(@"feedHierarchyBypass"); return; }
    CGRect area=container.bounds;
    // The immediate card parent can retain the old width. Walk every clipping
    // ancestor, including the actual window, using converted coordinates.
    NSUInteger ancestors=0;
    for(UIView *parent=container.superview;parent && ancestors<40;parent=parent.superview,ancestors++) {
        if(parent.clipsToBounds || parent==container.window) {
            CGRect clip=[parent convertRect:parent.bounds toView:container];
            if(tp_rect_valid(clip)) area=tp_intersect_horizontal(area,clip);
        }
    }
    NSUInteger budget=1000;
    area=TPSidebarClip(container.window,container,area,0,&budget);
    CGSize size=TPVideoSize(self);
    // IVS reports the real source dimensions even before FeedPlayerView caches it.
    if(!(size.width>0 && size.height>0)) {
        id player=TPField(self,"player");
        if([player respondsToSelector:@selector(videoSize)]) {
            CGSize (*send)(id,SEL)=(void *)dlsym((void *)(intptr_t)-2,"objc_msgSend");
            if(send) size=send(player,@selector(videoSize));
        }
    }
    CGRect fitted=tp_aspect_fit(size,area);
    TPGeometry=[NSString stringWithFormat:@"Feed container %.0fx%.0f; visible x=%.0f width=%.0f; source %.0fx%.0f; fitted %.0fx%.0f; ancestors %lu",
        container.bounds.size.width,container.bounds.size.height,area.origin.x,area.size.width,
        size.width,size.height,fitted.size.width,fitted.size.height,(unsigned long)ancestors];
    if(!tp_rect_valid(fitted)) { TPCount(@"feedSizeBypass"); return; }
    TPPlace(video,container,fitted,NO); TPAspect(video); TPCount(@"feedFits");
    UIView *thumbnail=TPField(self,"thumbnailView");
    if([thumbnail isKindOfClass:[UIView class]]) thumbnail.contentMode=1;
}
static void TPVideoLayout(UIView *self,SEL selector) {
    if(TPFeedAncestor(self)) TPAspect(self);
    TPOldVideoLayout(self,selector);
    if(TPFeedAncestor(self)) TPAspect(self);
}
static void TPTheaterLayout(UIView *self,SEL selector) {
    TPOldTheaterLayout(self,selector);
    if(!TPWidePhone(self.window) || self.bounds.size.width<self.window.bounds.size.width*.85 ||
       self.bounds.size.height<self.window.bounds.size.height*.3) return;
    UIView *stack=TPField(self,"videoPlayerStackView"),*video=TPField(self,"videoPlayerView");
    if(![stack isKindOfClass:[UIView class]] || !TPDescendant(stack,self)) return;
    // Extend the video background across the reserved strip. Player controls keep
    // their original safe-area constraints; this changes horizontal placement only.
    CGRect full=[self.window convertRect:self.window.bounds toView:self];
    full.origin.y=self.bounds.origin.y; full.size.height=self.bounds.size.height;
    TPTheaterGeometry=[NSString stringWithFormat:@"Theater %.0fx%.0f; stack %.0fx%.0f; background width %.0f",
        self.bounds.size.width,self.bounds.size.height,stack.bounds.size.width,stack.bounds.size.height,full.size.width];
    self.clipsToBounds=NO;
    TPPlace(stack,self,full,YES);
    if([video isKindOfClass:[UIView class]]) TPAspect(video);
    TPCount(@"theaterFullWidthLayouts");
}
static void TPDiscoveryLayout(UIViewController *self,SEL selector) {
    TPOldDiscoveryLayout(self,selector);
    for(UIViewController *controller=self;controller;controller=controller.parentViewController) {
        UINavigationItem *navigation=controller.navigationItem;
        // Apple ignores hidesSharedBackground for multi-item groups. Split these
        // into one-item groups while retaining each original item, action and menu.
        if([navigation respondsToSelector:@selector(trailingItemGroups)]) {
            NSArray *groups=navigation.trailingItemGroups; BOOL split=NO;
            for(UIBarButtonItemGroup *group in groups) {
                if(group.barButtonItems.count>1) { split=YES; break; }
            }
            if(split) {
                NSMutableArray *single=[NSMutableArray array];
                for(UIBarButtonItemGroup *group in groups)
                    for(UIBarButtonItem *item in group.barButtonItems)
                        [single addObject:[[UIBarButtonItemGroup alloc] initWithBarButtonItems:@[item] representativeItem:nil]];
                navigation.trailingItemGroups=single; TPCount(@"toolbarGroupsSplit");
            }
        }
        for(UIBarButtonItem *item in controller.navigationItem.rightBarButtonItems) {
            if([item respondsToSelector:@selector(setHidesSharedBackground:)] && !item.hidesSharedBackground) item.hidesSharedBackground=YES;
            if([item respondsToSelector:@selector(setSharesBackground:)] && item.sharesBackground) item.sharesBackground=NO;
        }
    }
}
static void TPExistingRoots(UIViewController *controller,NSUInteger depth) {
    if(!controller || depth>16) return;
    if(TPKind(controller,"_TtC6Twitch18RootViewController")) {
        [TPRoots addObject:controller]; TPApplyCompact(controller); [controller.view setNeedsLayout];
    }
    for(UIViewController *child in controller.childViewControllers) TPExistingRoots(child,depth+1);
}
static IMP TPHook(const char *className,SEL selector,IMP replacement) {
    Class class=objc_getClass(className); if(!class) return 0;
    Method method=class_getInstanceMethod(class,selector); if(!method) return 0;
    IMP original=method_getImplementation(method);
    if(!class_addMethod(class,selector,replacement,method_getTypeEncoding(method))) method_setImplementation(method,replacement);
    return original;
}

@interface TwitchPlusFixActions:NSObject
- (void)diagnostics:(UIView *)sender;
- (void)compactChanged:(UISwitch *)sender;
@end
static TwitchPlusFixActions *TPActions;
@implementation TwitchPlusFixActions
- (void)diagnostics:(UIView *)sender {
    NSMutableString *text=[NSMutableString string];
    [text appendString:@"TwitchPlus Beta 4 runtime diagnostics\n"];
    @synchronized(TPLock) {
        for(NSString *key in TPStats) [text appendFormat:@"%@: %@\n",key,TPStats[key]];
    }
    [text appendFormat:@"Ad filter setting (next stream): %d\nCompact wide phone: %d\n%@\n%@\n",TPEnabled(),TPCompactEnabled(),TPGeometry,TPTheaterGeometry];
    UIWindow *window=sender.window;
    [text appendFormat:@"Window %.0fx%.0f; idiom %ld; safe insets L%.0f R%.0f\n",
        window.bounds.size.width,window.bounds.size.height,(long)[UIDevice currentDevice].userInterfaceIdiom,
        window.safeAreaInsets.left,window.safeAreaInsets.right];
    [UIPasteboard generalPasteboard].string=text;
    id responder=sender;
    for(NSUInteger n=0;responder && n<40 && ![responder isKindOfClass:[UIViewController class]];n++) responder=[responder nextResponder];
    if([responder isKindOfClass:[UIViewController class]]) {
        UIAlertController *alert=[UIAlertController alertControllerWithTitle:@"Diagnostics copied" message:text preferredStyle:1];
        [alert addAction:[UIAlertAction actionWithTitle:@"Done" style:0 handler:nil]];
        [(UIViewController *)responder presentViewController:alert animated:YES completion:nil];
    }
}
- (void)compactChanged:(UISwitch *)sender {
    [[NSUserDefaults standardUserDefaults] setBool:sender.on forKey:TPCompactKey];
    for(UIViewController *root in TPRoots.allObjects) { TPApplyCompact(root); [root.view setNeedsLayout]; }
}
@end

__attribute__((visibility("default"))) void tp_add_diagnostics(UIStackView *stack) {
    UILabel *description=[UILabel new]; description.numberOfLines=0; description.textColor=[UIColor labelColor];
    description.text=@"Wide phone layout uses Twitch's compact navigation to avoid the broken tablet sidebar. You can turn it off to test the sidebar layout. Changes apply to this window.";
    UIStackView *row=[UIStackView new]; UILabel *label=[UILabel new]; label.text=@"Compact layout on wide phones"; label.numberOfLines=0; label.textColor=[UIColor labelColor];
    UISwitch *toggle=[UISwitch new]; toggle.on=TPCompactEnabled(); toggle.accessibilityLabel=@"Compact layout on wide phones";
    [toggle addTarget:TPActions action:@selector(compactChanged:) forControlEvents:4096];
    [row addArrangedSubview:label]; [row addArrangedSubview:toggle]; [stack addArrangedSubview:row]; [stack addArrangedSubview:description];
    UIButton *button=[UIButton buttonWithType:1]; [button setTitle:@"Copy runtime diagnostics" forState:0];
    [button addTarget:TPActions action:@selector(diagnostics:) forControlEvents:64];
    [button.heightAnchor constraintEqualToConstant:44].active=YES; [stack addArrangedSubview:button];
}

static BOOL TPInstalled;
static void TPInstall(NSUInteger attempt) {
    if(TPInstalled) return;
    Class delegate=objc_getClass("IVSPlayerURLSessionDelegate");
    Method data=class_getInstanceMethod(delegate,@selector(URLSession:dataTask:didReceiveData:));
    Method complete=class_getInstanceMethod(delegate,@selector(URLSession:task:didCompleteWithError:));
    if(!data || !complete) {
        TPStats[@"networkHooksInstalled"]=@NO;
        if(attempt<20) dispatch_after(dispatch_time(0,250000000),dispatch_get_main_queue(),^{TPInstall(attempt+1);});
        return;
    }
    TPInstalled=YES;
    dlopen("/System/Library/Frameworks/JavaScriptCore.framework/JavaScriptCore",2);
    Class javascript=objc_getClass("JSContext");
    if(javascript) {
        TPJS=[javascript new];
        [TPJS evaluateScript:[NSString stringWithUTF8String:(const char *)TPPlaylistEngineScript]];
        if(TPJS.exception) TPJS=nil;
    }
    TPStats[@"playlistEngineInstalled"]=@(TPJS!=nil);
    // Publish original network IMPs before replacing either method; callbacks
    // already in flight must never observe an uninitialized original pointer.
    TPOldData=(void *)method_getImplementation(data);
    TPOldComplete=(void *)method_getImplementation(complete);
    TPOldData=(void *)TPHook("IVSPlayerURLSessionDelegate",@selector(URLSession:dataTask:didReceiveData:),(IMP)TPData);
    TPOldComplete=(void *)TPHook("IVSPlayerURLSessionDelegate",@selector(URLSession:task:didCompleteWithError:),(IMP)TPComplete);
    TPOldFeedLayout=(void *)TPHook("_TtC6Twitch14FeedPlayerView",@selector(layoutSubviews),(IMP)TPFeedLayout);
    TPOldVideoLayout=(void *)TPHook("_TtC6Twitch15VideoPlayerView",@selector(layoutSubviews),(IMP)TPVideoLayout);
    TPOldRootLayout=(void *)TPHook("_TtC6Twitch18RootViewController",@selector(viewDidLayoutSubviews),(IMP)TPRootLayout);
    TPOldTheaterLayout=(void *)TPHook("_TtC6Twitch11TheaterView",@selector(layoutSubviews),(IMP)TPTheaterLayout);
    TPOldDiscoveryLayout=(void *)TPHook("_TtC6Twitch30DiscoveryFeedTabViewController",@selector(viewDidLayoutSubviews),(IMP)TPDiscoveryLayout);
    @synchronized(TPLock) {
        TPStats[@"networkHooksInstalled"]=@(TPOldData && TPOldComplete);
        TPStats[@"feedHookInstalled"]=@(TPOldFeedLayout!=0);
        TPStats[@"videoHookInstalled"]=@(TPOldVideoLayout!=0);
        TPStats[@"rootHookInstalled"]=@(TPOldRootLayout!=0);
        TPStats[@"theaterHookInstalled"]=@(TPOldTheaterLayout!=0);
    }
    for(UIWindow *window in [UIApplication sharedApplication].windows) TPExistingRoots(window.rootViewController,0);
}
__attribute__((constructor)) static void TPInitialize(void) {
    @autoreleasepool {
        TPLock=[NSObject new]; TPStats=[NSMutableDictionary dictionary];
        TPMappings=[NSMutableDictionary dictionary]; TPChannels=[NSMutableDictionary dictionary];
        TPRoots=[NSHashTable weakObjectsHashTable]; TPActions=[TwitchPlusFixActions new];
        NSURLSessionConfiguration *config=[NSURLSessionConfiguration ephemeralSessionConfiguration];
        config.HTTPShouldSetCookies=NO; config.HTTPCookieStorage=nil; config.URLCredentialStorage=nil; config.URLCache=nil;
        config.timeoutIntervalForRequest=2; config.timeoutIntervalForResource=3;
        TPNetwork=[NSURLSession sessionWithConfiguration:config];
        // Retry on the main queue: avoid depending on executable-class realization
        // order during dyld initialization of an injected library.
        dispatch_async(dispatch_get_main_queue(),^{TPInstall(0);});
    }
}
