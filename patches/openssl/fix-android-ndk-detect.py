#!/usr/bin/env python3
"""
Patch OpenSSL's 15-android.conf to work with from-source NDK toolchains.

OpenSSL's standalone toolchain detection checks that the clang binary
lives under $ANDROID_NDK_ROOT using a path regex match. Our from-source
NDK has clang directly in $NDK/bin/ which doesn't match the expected
path pattern. This patch relaxes the check to just verify the tool
exists on PATH rather than requiring it under a specific NDK subdirectory.
"""
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <15-android.conf>")
    sys.exit(1)

filepath = sys.argv[1]

with open(filepath, 'r') as f:
    content = f.read()

# Original: if (which("$triarch-$cc") !~ m|^$ndk|) {
#   die "no NDK $triarch-$cc on \$PATH";
# }
#
# Replace with: if (!which("$triarch-$cc")) {
#   die "no $triarch-$cc on \$PATH";
# }
#
# This removes the requirement that the tool must be under $ndk,
# and just checks that it exists on PATH.

old = 'which("$triarch-$cc") !~ m|^$ndk|'
new = '!which("$triarch-$cc")'

if old not in content:
    print(f"WARNING: Pattern not found in {filepath}")
    print("The file may have already been patched or the OpenSSL version changed.")
    sys.exit(0)

content = content.replace(old, new)

# Also fix the die message to match
content = content.replace(
    'die "no NDK $triarch-$cc on \\$PATH"',
    'die "no $triarch-$cc on \\$PATH"'
)

with open(filepath, 'w') as f:
    f.write(content)

print(f"Patched {filepath}: relaxed standalone NDK detection")
