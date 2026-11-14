// Real UIKit/Auto Layout/hit-testing fixture, not the Twitch executable or an
// IVS playback test. Shares the shipping layout implementation verbatim.
#define TP_LAYOUT_TEST 1
#include "../src/TwitchPlusFixes.m"
#include <stdlib.h>
#include <math.h>

static void Check(BOOL condition,NSString *message) {
    if(!condition) [NSException raise:@"LayoutRegression" format:@"%@",message];
}
static BOOL Near(double a,double b) { return fabs(a-b)<.5; }

@interface TPTestWindow:UIWindow @end
@implementation TPTestWindow
- (UITraitCollection *)traitCollection {
    return [UITraitCollection traitCollectionWithTraitsFromCollections:@[[super traitCollection],
        [UITraitCollection traitCollectionWithHorizontalSizeClass:UIUserInterfaceSizeClassRegular]]];
}
@end
@interface TPTestTheater:UIView {
@public
    UIView *videoPlayerStackView,*videoPlayerView,*controlsContainerView,*controlsView,*accessoryContainerView;
    UIGestureRecognizer *tapGesture,*doubleTapGesture;
}
@end
@implementation TPTestTheater
- (void)layoutSubviews { [super layoutSubviews]; TPFitTheater(self); }
@end

static void Flush(TPTestTheater *theater) {
    [theater setNeedsLayout]; [theater layoutIfNeeded];
    [theater layoutIfNeeded];
}
static void CheckSurfaces(TPTestTheater *t,double width) {
    CGRect video=[t->videoPlayerStackView convertRect:t->videoPlayerStackView.bounds toView:t];
    CGRect controls=[t->controlsView convertRect:t->controlsView.bounds toView:t];
    Check(Near(video.size.width,width),@"Video viewport has stale width");
    Check(Near(video.origin.x,controls.origin.x) && Near(video.origin.y,controls.origin.y) &&
          Near(video.size.width,controls.size.width) && Near(video.size.height,controls.size.height),
          @"Controls and video do not share the final solved rectangle");
    CGPoint point={video.origin.x+video.size.width-8,video.origin.y+video.size.height*.5};
    UIView *hit=[t hitTest:point withEvent:nil];
    Check(TPDescendant(hit,t->controlsView),@"Trailing video region is not hittable through the controls hierarchy");
    Check(t->tapGesture.view==t && t->tapGesture.enabled,@"Native tap gesture was detached or disabled");
    Check(!t->doubleTapGesture.enabled,@"Disabled native gesture preference changed");
}
static NSArray *RunFixtures(UIWindow *window) {
    window.bounds=CGRectMake(0,0,1000,1000);
    window.rootViewController.view.frame=window.bounds;
    TPLock=[NSObject new]; TPStats=[NSMutableDictionary dictionary];
    TPOldTheaterFrame=(void *)TPHook("TPTestTheater",@selector(setFrame:),(IMP)TPTheaterSetFrame);
    TPOldTheaterBounds=(void *)TPHook("TPTestTheater",@selector(setBounds:),(IMP)TPTheaterSetBounds);
    TPTestTheater *t=[[TPTestTheater alloc] initWithFrame:CGRectMake(0,0,1000,700)];
    [window.rootViewController.view addSubview:t];
    t->videoPlayerStackView=[UIView new]; t->videoPlayerView=[UIView new];
    t->controlsContainerView=[UIView new]; t->controlsView=[UIView new];
    t->accessoryContainerView=[[UIView alloc] initWithFrame:CGRectMake(700,0,300,700)];
    t->accessoryContainerView.hidden=YES;
    [t addSubview:t->videoPlayerStackView]; [t->videoPlayerStackView addSubview:t->videoPlayerView];
    [t addSubview:t->controlsContainerView]; [t->controlsContainerView addSubview:t->controlsView];
    [t addSubview:t->accessoryContainerView];
    t->tapGesture=[[UITapGestureRecognizer alloc] init]; [t addGestureRecognizer:t->tapGesture];
    t->doubleTapGesture=[[UITapGestureRecognizer alloc] init]; t->doubleTapGesture.enabled=NO;
    [t addGestureRecognizer:t->doubleTapGesture];
    for(UIView *v in @[t->videoPlayerStackView,t->controlsContainerView,t->controlsView]) v.translatesAutoresizingMaskIntoConstraints=NO;
    // Twitch keeps the native constraint set alive. Deliberately reproduce the
    // user's narrower/stale controls and native portrait aspect-ratio constraint.
    NSLayoutConstraint *height=[t->videoPlayerStackView.heightAnchor constraintEqualToConstant:650];
    NSLayoutConstraint *aspect=[t->videoPlayerStackView.heightAnchor constraintEqualToAnchor:t->videoPlayerStackView.widthAnchor multiplier:9.0/16.0];
    NSArray *native=@[
        [t->videoPlayerStackView.leadingAnchor constraintEqualToAnchor:t.leadingAnchor],
        [t->videoPlayerStackView.topAnchor constraintEqualToAnchor:t.topAnchor constant:30],
        [t->videoPlayerStackView.widthAnchor constraintEqualToConstant:650],height,
        [t->controlsContainerView.leadingAnchor constraintEqualToAnchor:t.leadingAnchor],
        [t->controlsContainerView.topAnchor constraintEqualToAnchor:t.topAnchor constant:30],
        [t->controlsContainerView.widthAnchor constraintEqualToConstant:640],
        [t->controlsContainerView.heightAnchor constraintEqualToConstant:400],
        [t->controlsView.leadingAnchor constraintEqualToAnchor:t->controlsContainerView.leadingAnchor],
        [t->controlsView.trailingAnchor constraintEqualToAnchor:t->controlsContainerView.trailingAnchor],
        [t->controlsView.topAnchor constraintEqualToAnchor:t->controlsContainerView.topAnchor],
        [t->controlsView.bottomAnchor constraintEqualToAnchor:t->controlsContainerView.bottomAnchor]];
    [NSLayoutConstraint activateConstraints:native]; Flush(t);
    CheckSurfaces(t,1000);
    NSUInteger count=t.constraints.count;
    for(NSUInteger i=0;i<30;i++) {
        t->accessoryContainerView.hidden=NO; Flush(t); CheckSurfaces(t,700);
        Check([t hitTest:CGPointMake(900,300) withEvent:nil]==t->accessoryContainerView,@"Video steals chat touches");
        t->accessoryContainerView.hidden=YES; Flush(t); CheckSurfaces(t,1000);
    }
    Check(t.constraints.count==count,@"Chat toggles accumulate constraints");
    for(NSUInteger i=0;i<12;i++) {
        TPReleaseTheater(t); height.active=NO; aspect.active=YES;
        t.frame=CGRectMake(0,0,700,1000); Flush(t); TPRefreshTheater(t,YES); Flush(t);
        CheckSurfaces(t,700);
        Check(Near(t->controlsView.bounds.size.height,700*9.0/16.0),@"Portrait controls retain pre-solve height");
        TPReleaseTheater(t); aspect.active=NO; height.active=YES;
        t.frame=CGRectMake(0,0,1000,700); Flush(t); TPRefreshTheater(t,YES); Flush(t);
        CheckSurfaces(t,1000);
    }
    TPReleaseTheater(t); [t layoutIfNeeded];
    for(NSLayoutConstraint *constraint in native) Check(constraint.active,@"Native constraints not restored before transition");
    Check(Near(t->controlsContainerView.bounds.size.width,640),@"Native geometry was not restored");

    // When Twitch replaces a constraint set for chat, obsolete constraints must
    // expire rather than being resurrected by the next rotation.
    UIView *child=[UIView new]; [t addSubview:child]; child.translatesAutoresizingMaskIntoConstraints=NO;
    __weak NSLayoutConstraint *expired;
    @autoreleasepool {
        NSLayoutConstraint *old=[child.widthAnchor constraintEqualToConstant:250]; old.active=YES; expired=old;
        TPPlace(child,t,CGRectMake(0,0,400,200),NO);
    }
    Check(expired==nil,@"Old native constraints are retained after replacement");
    NSLayoutConstraint *current=[child.widthAnchor constraintEqualToConstant:350]; current.active=YES;
    TPPlace(child,t,CGRectMake(0,0,500,200),NO); TPReleasePlacement(child);
    Check(current.active,@"Current native constraint not restored");
    [child removeFromSuperview];
    return @[@"video-controls-hit-area",@"30-chat-toggle-cycles",@"chat-hit-isolation",@"bounded-constraints",
        @"12-portrait-landscape-cycles",@"portrait-aspect-height",@"native-constraint-restoration",
        @"obsolete-constraint-expiry",@"native-gesture-preservation"];
}

@interface TPFixtureDelegate:UIResponder<UIApplicationDelegate>
@property(strong,nonatomic) UIWindow *window;
@end
@implementation TPFixtureDelegate
- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)options {
    (void)application; (void)options;
    self.window=[[TPTestWindow alloc] initWithFrame:CGRectMake(0,0,1000,1000)];
    self.window.rootViewController=[UIViewController new]; [self.window makeKeyAndVisible];
    dispatch_async(dispatch_get_main_queue(),^{
        NSDictionary *report;
        @try { report=@{@"passed":@YES,@"checks":RunFixtures(self.window),@"scope":@"UIKit fixture; no Twitch playback or physical device"}; }
        @catch(NSException *error) { report=@{@"passed":@NO,@"error":error.reason?:@"Unknown exception"}; }
        NSString *file=[NSHomeDirectory() stringByAppendingPathComponent:@"Documents/layout-fixture.json"];
        [[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil] writeToFile:file atomically:YES];
        fprintf(stderr,"UIKit layout fixture: %s\n",[report.description UTF8String]);
        exit([report[@"passed"] boolValue]?0:1);
    });
    return YES;
}
@end
int main(int argc,char **argv) {
    @autoreleasepool { return UIApplicationMain(argc,argv,nil,NSStringFromClass([TPFixtureDelegate class])); }
}
