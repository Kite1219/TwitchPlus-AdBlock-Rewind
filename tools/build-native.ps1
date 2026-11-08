param([Parameter(Mandatory=$true)][string]$CompilerRoot)
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
$buildRoot=Join-Path $repoRoot 'build'
New-Item -ItemType Directory -Path $buildRoot -Force | Out-Null
$rustc=Join-Path $CompilerRoot 'bin/rustc.exe'
$linker=Join-Path $CompilerRoot 'lib/rustlib/x86_64-pc-windows-gnu/bin/gcc-ld/ld64.lld.exe'
$oldBootstrap=$env:RUSTC_BOOTSTRAP
$oldTarget=$env:IPHONEOS_DEPLOYMENT_TARGET
try {
 $env:RUSTC_BOOTSTRAP='1';$env:IPHONEOS_DEPLOYMENT_TARGET='16.4'
 foreach($name in @('NativeRewind','NativeChat','ForcedFollow')) {
  $object=Join-Path $buildRoot ($name+'.o')
  & $rustc --edition 2024 --target aarch64-apple-ios --crate-type lib --emit=obj -C panic=abort -C opt-level=s -C overflow-checks=no (Join-Path $repoRoot ('src/'+$name+'.rs')) -o $object
  if($LASTEXITCODE -ne 0){throw "Compilation failed: $name"}
  & $linker -dylib -arch arm64 -platform_version ios 16.4 16.4 -install_name "@executable_path/Frameworks/$name.dylib" -undefined dynamic_lookup -no_adhoc_codesign -o (Join-Path $buildRoot ($name+'.dylib')) $object
  if($LASTEXITCODE -ne 0){throw "Linking failed: $name"}
 }
} finally {$env:RUSTC_BOOTSTRAP=$oldBootstrap;$env:IPHONEOS_DEPLOYMENT_TARGET=$oldTarget}
