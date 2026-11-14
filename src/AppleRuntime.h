// Minimal declarations of public Apple APIs used by the injected component.
// This is an ABI bridge, not an Apple SDK or an implementation of these APIs.
#ifndef TWITCHPLUS_APPLE_RUNTIME_H
#define TWITCHPLUS_APPLE_RUNTIME_H
#ifdef TP_USE_APPLE_SDK
#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <JavaScriptCore/JavaScriptCore.h>
#import <objc/runtime.h>
#import <dispatch/dispatch.h>
#include <dlfcn.h>
#include "TwitchPlusCore.h"
#define TPDispatchRetain(value) ((void)0)
#define TPDispatchRelease(value) ((void)0)
#else
#include "TwitchPlusCore.h"
#include <stdint.h>
typedef signed char BOOL;
typedef unsigned long NSUInteger;
typedef long NSInteger;
typedef double NSTimeInterval;
typedef struct NSRange { NSUInteger location,length; } NSRange;
#define YES ((BOOL)1)
#define NO ((BOOL)0)
#define nil ((id)0)
#define NSNotFound ((NSUInteger)0x7fffffffffffffffUL)
typedef void (*IMP)(void);
typedef void *Method;
typedef void *Ivar;
extern Class objc_getClass(const char *);
extern Class object_getClass(id);
extern const char *class_getName(Class);
extern Method class_getInstanceMethod(Class,SEL);
extern BOOL class_addMethod(Class,SEL,IMP,const char *);
extern IMP method_getImplementation(Method);
extern IMP method_setImplementation(Method,IMP);
extern const char *method_getTypeEncoding(Method);
extern Ivar class_getInstanceVariable(Class,const char *);
extern ptrdiff_t ivar_getOffset(Ivar);
extern id object_getIvar(id,Ivar);
extern id objc_getAssociatedObject(id,const void *);
extern void objc_setAssociatedObject(id,const void *,id,NSUInteger);
extern void *dlsym(void *,const char *);
extern void *dlopen(const char *,int);
typedef void *dispatch_queue_t;
typedef void *dispatch_group_t;
typedef void *dispatch_semaphore_t;
typedef uint64_t dispatch_time_t;
extern dispatch_queue_t dispatch_get_global_queue(long, unsigned long);
extern dispatch_queue_t dispatch_get_main_queue(void);
extern void dispatch_async(dispatch_queue_t,void (^)(void));
extern void dispatch_after(dispatch_time_t,dispatch_queue_t,void (^)(void));
extern dispatch_time_t dispatch_time(dispatch_time_t,int64_t);
extern dispatch_group_t dispatch_group_create(void);
extern void dispatch_group_async(dispatch_group_t,dispatch_queue_t,void (^)(void));
extern long dispatch_group_wait(dispatch_group_t,dispatch_time_t);
extern dispatch_semaphore_t dispatch_semaphore_create(long);
extern long dispatch_semaphore_wait(dispatch_semaphore_t,dispatch_time_t);
extern long dispatch_semaphore_signal(dispatch_semaphore_t);
extern void dispatch_release(void *);
extern void dispatch_retain(void *);
#define TPDispatchRetain(value) dispatch_retain(value)
#define TPDispatchRelease(value) dispatch_release(value)

@protocol NSCopying @end
@protocol NSFastEnumeration
- (NSUInteger)countByEnumeratingWithState:(void *)state objects:(id __unsafe_unretained *)buffer count:(NSUInteger)len;
@end
@class NSString,NSArray,NSDictionary,NSData,NSURL,NSError,UIView,UIViewController,UIWindow,NSLayoutConstraint,NSLayoutAnchor,NSLayoutDimension,UIFont,UIColor,UIImage,UIEvent,UITraitCollection;
__attribute__((objc_root_class)) @interface NSObject
+ (instancetype)alloc;
+ (instancetype)new;
+ (Class)class;
- (instancetype)init;
- (BOOL)isKindOfClass:(Class)classObject;
- (BOOL)respondsToSelector:(SEL)selector;
- (BOOL)isEqual:(id)other;
- (id)copy;
- (id)mutableCopy;
- (id)nextResponder;
@end
@interface NSString:NSObject<NSCopying>
+ (instancetype)stringWithUTF8String:(const char *)text;
+ (instancetype)stringWithFormat:(NSString *)format,...;
- (instancetype)initWithData:(NSData *)data encoding:(NSUInteger)encoding;
@property(readonly) const char *UTF8String;
@property(readonly) NSUInteger length;
@property(readonly) NSString *lowercaseString;
- (BOOL)isEqualToString:(NSString *)other;
- (BOOL)hasPrefix:(NSString *)prefix;
- (BOOL)hasSuffix:(NSString *)suffix;
- (BOOL)containsString:(NSString *)text;
- (NSArray *)componentsSeparatedByString:(NSString *)separator;
- (NSString *)stringByAppendingString:(NSString *)text;
- (NSString *)stringByReplacingOccurrencesOfString:(NSString *)old withString:(NSString *)newText;
- (NSString *)substringFromIndex:(NSUInteger)index;
- (NSString *)substringToIndex:(NSUInteger)index;
- (NSString *)substringWithRange:(NSRange)range;
- (NSRange)rangeOfString:(NSString *)text;
- (NSData *)dataUsingEncoding:(NSUInteger)encoding;
@end
@interface NSMutableString:NSString
+ (instancetype)string;
- (void)appendString:(NSString *)text;
- (void)appendFormat:(NSString *)format,...;
- (void)replaceCharactersInRange:(NSRange)range withString:(NSString *)text;
@end
@interface NSArray:NSObject<NSCopying,NSFastEnumeration>
+ (instancetype)array;
+ (instancetype)arrayWithObjects:(const id [])objects count:(NSUInteger)count;
@property(readonly) NSUInteger count;
- (id)objectAtIndexedSubscript:(NSUInteger)index;
- (BOOL)containsObject:(id)object;
- (NSString *)componentsJoinedByString:(NSString *)separator;
@end
@interface NSMutableArray:NSArray
+ (instancetype)array;
- (void)addObject:(id)object;
- (void)removeObject:(id)object;
@end
@interface NSDictionary:NSObject<NSCopying,NSFastEnumeration>
+ (instancetype)dictionaryWithObjects:(const id [])objects forKeys:(const id [])keys count:(NSUInteger)count;
- (id)objectForKeyedSubscript:(id)key;
@property(readonly) NSUInteger count;
@end
@interface NSMutableDictionary:NSDictionary
+ (instancetype)dictionary;
- (void)setObject:(id)object forKeyedSubscript:(id)key;
- (void)removeObjectForKey:(id)key;
- (void)removeAllObjects;
@end
@interface NSNumber:NSObject
+ (instancetype)numberWithBool:(BOOL)value;
+ (instancetype)numberWithInt:(int)value;
+ (instancetype)numberWithLong:(long)value;
+ (instancetype)numberWithUnsignedLong:(unsigned long)value;
+ (instancetype)numberWithUnsignedInteger:(NSUInteger)value;
+ (instancetype)numberWithInteger:(NSInteger)value;
+ (instancetype)numberWithDouble:(double)value;
@property(readonly) BOOL boolValue;
@property(readonly) double doubleValue;
@property(readonly) NSUInteger unsignedIntegerValue;
@end
@interface NSData:NSObject<NSCopying>
@property(readonly) NSUInteger length;
@property(readonly) const void *bytes;
@end
@interface NSMutableData:NSData
+ (instancetype)data;
- (void)appendData:(NSData *)data;
@end
@interface NSDate:NSObject
+ (NSTimeInterval)timeIntervalSinceReferenceDate;
@end
@interface NSUUID:NSObject
+ (instancetype)UUID;
@property(readonly) NSString *UUIDString;
@end
@interface NSUserDefaults:NSObject
+ (instancetype)standardUserDefaults;
- (id)objectForKey:(NSString *)key;
- (BOOL)boolForKey:(NSString *)key;
- (void)setBool:(BOOL)value forKey:(NSString *)key;
@end
@interface NSURL:NSObject<NSCopying>
+ (instancetype)URLWithString:(NSString *)text;
+ (instancetype)URLWithString:(NSString *)text relativeToURL:(NSURL *)base;
@property(readonly) NSURL *absoluteURL;
@property(readonly) NSString *absoluteString,*scheme,*host,*path,*pathExtension,*lastPathComponent;
@end
@interface NSURLQueryItem:NSObject
+ (instancetype)queryItemWithName:(NSString *)name value:(NSString *)value;
@end
@interface NSURLComponents:NSObject
+ (instancetype)componentsWithString:(NSString *)text;
@property(copy) NSString *scheme,*host,*path;
@property(copy) NSArray *queryItems;
@property(readonly) NSURL *URL;
@end
@interface NSURLRequest:NSObject<NSCopying>
@property(readonly) NSURL *URL;
@end
@interface NSMutableURLRequest:NSURLRequest
+ (instancetype)requestWithURL:(NSURL *)URL;
@property(copy) NSString *HTTPMethod;
@property(copy) NSData *HTTPBody;
@property NSTimeInterval timeoutInterval;
@property BOOL HTTPShouldHandleCookies;
- (void)setValue:(NSString *)value forHTTPHeaderField:(NSString *)field;
@end
@interface NSURLResponse:NSObject
@property(readonly) NSURL *URL;
@end
@interface NSHTTPURLResponse:NSURLResponse
@property(readonly) NSInteger statusCode;
@end
@interface NSURLSessionConfiguration:NSObject
+ (instancetype)ephemeralSessionConfiguration;
@property NSTimeInterval timeoutIntervalForRequest,timeoutIntervalForResource;
@property BOOL HTTPShouldSetCookies;
@property(strong) id HTTPCookieStorage,URLCredentialStorage,URLCache;
@end
@interface NSURLSessionTask:NSObject
@property(readonly) NSURLRequest *currentRequest,*originalRequest;
@property(readonly) NSURLResponse *response;
- (void)resume;
- (void)cancel;
@end
@interface NSOperationQueue:NSObject
- (void)addOperationWithBlock:(void (^)(void))block;
@end
@interface NSURLSession:NSObject
+ (instancetype)sessionWithConfiguration:(NSURLSessionConfiguration *)configuration;
- (NSURLSessionTask *)dataTaskWithRequest:(NSURLRequest *)request completionHandler:(void (^)(NSData *,NSURLResponse *,NSError *))handler;
@property(readonly) NSOperationQueue *delegateQueue;
@end
@interface NSJSONSerialization:NSObject
+ (NSData *)dataWithJSONObject:(id)object options:(NSUInteger)options error:(NSError **)error;
+ (id)JSONObjectWithData:(NSData *)data options:(NSUInteger)options error:(NSError **)error;
@end
@interface NSThread:NSObject
+ (BOOL)isMainThread;
@end
@interface NSHashTable:NSObject
+ (instancetype)weakObjectsHashTable;
- (void)addObject:(id)object;
@property(readonly) NSArray *allObjects;
@end
@class JSValue;
@interface JSContext:NSObject
- (JSValue *)evaluateScript:(NSString *)script;
- (JSValue *)objectForKeyedSubscript:(id)key;
@property(strong) JSValue *exception;
@end
@interface JSValue:NSObject
- (JSValue *)objectForKeyedSubscript:(id)key;
- (JSValue *)callWithArguments:(NSArray *)arguments;
- (id)toObject;
@end

@interface NSLayoutAnchor:NSObject
- (NSLayoutConstraint *)constraintEqualToAnchor:(NSLayoutAnchor *)other constant:(double)constant;
@end
@interface NSLayoutDimension:NSLayoutAnchor
- (NSLayoutConstraint *)constraintEqualToConstant:(double)constant;
@end
@interface NSLayoutConstraint:NSObject
@property double constant;
@property(getter=isActive) BOOL active;
@property(readonly) id firstItem,secondItem;
@property(readonly) NSInteger firstAttribute,secondAttribute;
+ (void)activateConstraints:(NSArray *)constraints;
+ (void)deactivateConstraints:(NSArray *)constraints;
@end
@interface UILayoutGuide:NSObject
@property(readonly) UIView *owningView;
@end
@interface UIView:NSObject
- (instancetype)initWithFrame:(CGRect)frame;
@property CGRect frame,bounds;
@property(readonly) UIView *superview;
@property(readonly) UIWindow *window;
@property(readonly) NSArray *subviews,*constraints;
@property(getter=isHidden) BOOL hidden;
@property BOOL clipsToBounds,userInteractionEnabled,translatesAutoresizingMaskIntoConstraints;
@property double alpha;
@property NSInteger contentMode;
@property(strong) UIColor *backgroundColor,*tintColor;
@property(copy) NSString *accessibilityLabel;
@property(readonly) UIEdgeInsets safeAreaInsets;
@property(readonly) UITraitCollection *traitCollection;
@property(readonly) id layer;
@property(readonly) NSArray *gestureRecognizers;
@property(readonly) NSLayoutAnchor *leadingAnchor,*trailingAnchor,*topAnchor,*bottomAnchor,*centerXAnchor,*centerYAnchor;
@property(readonly) NSLayoutDimension *widthAnchor,*heightAnchor;
- (CGRect)convertRect:(CGRect)rect toView:(UIView *)view;
- (void)addSubview:(UIView *)view;
- (void)setNeedsLayout;
- (void)layoutIfNeeded;
- (void)removeFromSuperview;
@end
@interface UIColor:NSObject
+ (instancetype)systemBackgroundColor;
+ (instancetype)labelColor;
@end
@interface UIFont:NSObject
+ (instancetype)systemFontOfSize:(double)size;
@end
@interface UILabel:UIView
@property(copy) NSString *text;
@property NSInteger numberOfLines;
@property(strong) UIFont *font;
@property(strong) UIColor *textColor;
@end
@interface UIStackView:UIView
- (void)addArrangedSubview:(UIView *)view;
@end
@interface UIControl:UIView
@property(getter=isEnabled) BOOL enabled;
- (void)addTarget:(id)target action:(SEL)action forControlEvents:(NSUInteger)events;
- (void)sendActionsForControlEvents:(NSUInteger)events;
@end
@interface UIButton:UIControl
+ (instancetype)buttonWithType:(NSInteger)type;
- (void)setTitle:(NSString *)title forState:(NSUInteger)state;
- (void)setImage:(UIImage *)image forState:(NSUInteger)state;
@end
@interface UISwitch:UIControl
@property(getter=isOn) BOOL on;
@end
@interface UIScrollView:UIView
@property double zoomScale;
@end
@interface UIImage:NSObject
+ (instancetype)systemImageNamed:(NSString *)name;
@end
@interface UIImageView:UIView
- (instancetype)initWithImage:(UIImage *)image;
@end
@interface UITraitCollection:NSObject
@property(readonly) NSInteger horizontalSizeClass;
@end
@interface UITraitOverrides:NSObject
@property NSInteger horizontalSizeClass;
- (void)removeTrait:(Class)trait;
@end
@interface UIBarButtonItem:NSObject
@property BOOL hidesSharedBackground;
@property BOOL sharesBackground;
@property(strong) UIView *customView;
@property(strong) UIImage *image;
@property(copy) NSString *title;
@property double width;
@end
@interface UIBarButtonItemGroup:NSObject
- (instancetype)initWithBarButtonItems:(NSArray *)items representativeItem:(UIBarButtonItem *)item;
@property(readonly) NSArray *barButtonItems;
@end
@interface UINavigationItem:NSObject
@property(copy) NSArray *rightBarButtonItems;
@property(copy) NSArray *trailingItemGroups;
@end
@interface UIViewController:NSObject
@property(strong) UIView *view;
@property(readonly) UIViewController *parentViewController;
@property(readonly) UINavigationItem *navigationItem;
@property(readonly) UITraitOverrides *traitOverrides;
@property(readonly) UITraitCollection *traitCollection;
@property(readonly) NSArray *childViewControllers;
- (void)presentViewController:(UIViewController *)viewController animated:(BOOL)animated completion:(void (^)(void))completion;
@end
@interface UIApplication:NSObject
+ (instancetype)sharedApplication;
@property(readonly) NSArray *windows;
@end
@interface UIWindow:UIView
@property(strong) UIViewController *rootViewController;
@end
@interface UIDevice:NSObject
+ (instancetype)currentDevice;
@property(readonly) NSInteger userInterfaceIdiom;
@end
@interface UIPasteboard:NSObject
+ (instancetype)generalPasteboard;
@property(copy) NSString *string;
@end
@interface UIAlertController:UIViewController
+ (instancetype)alertControllerWithTitle:(NSString *)title message:(NSString *)message preferredStyle:(NSInteger)style;
- (void)addAction:(id)action;
@end
@interface UIAlertAction:NSObject
+ (instancetype)actionWithTitle:(NSString *)title style:(NSInteger)style handler:(void (^)(id))handler;
@end
#endif
#endif
