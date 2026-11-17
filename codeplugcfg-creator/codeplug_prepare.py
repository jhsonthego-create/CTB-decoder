#!/usr/bin/env python3
# Original project: https://github.com/george-hopkins/codeplug-prepare
# Independent Python implementation of local CPS1 key discovery.
# The original project is MIT-licensed; see ORIGINAL-PROJECT-NOTICE.md.
"""Read a locally supplied CPS1 cpservices.dll and prepare a private config.

This implementation scans .NET UTF-16 string data and validates the candidate
values; it does not execute Motorola code or copy a vendor DLL into the output.
The original uses dnlib to inspect static constructors, so this is an
independent compatibility implementation, not a byte-for-byte port.
"""
import argparse
import base64
import binascii
import os
from pathlib import Path
import re
import sys

UTF16_ASCII = re.compile(rb'(?:[\x20-\x7e]\x00){8,}')
MARKER = "mototrbocps"


def scan_strings(data):
    return [(m.start(), m.group().decode("utf-16le")) for m in UTF16_ASCII.finditer(data)]


def validate_b64(raw, expected_bytes):
    try:
        decoded = base64.b64decode(raw + "=" * (-len(raw) % 4), validate=True)
    except (ValueError, binascii.Error):
        return False
    return len(decoded) == expected_bytes


def find_values(data):
    strings = scan_strings(data)
    marks = [i for i, (_, s) in enumerate(strings) if s == MARKER]
    if len(marks) != 1:
        raise ValueError("Expected exactly one mototrbocps marker; found %d" % len(marks))
    mark = marks[0]
    # The original C# selects string literals from a particular static
    # constructor, which can contain unrelated constants. We use the local
    # cluster of candidate literals and stop if the layout is unexpected.
    nearby = strings[max(0, mark-16):mark+8]
    long_candidates = [(p,s) for p,s in nearby if len(s) == 43 and validate_b64(s, 32)]
    short_candidates = [(p,s) for p,s in nearby if len(s) == 22 and validate_b64(s, 16)]
    if len(long_candidates) != 3 or len(short_candidates) < 4:
        raise ValueError("Unexpected key-string layout near marker; refusing to guess")
    # This layout matches the original tool's selection rule for the supplied DLL:
    # first 43-char string -> key; first 22-char string -> IV;
    # the fourth 22-char string -> signing_password.
    # Require the strings to be ordered in the expected cluster.
    if not (long_candidates[0][0] < long_candidates[1][0] < long_candidates[2][0]
            < short_candidates[0][0] < short_candidates[1][0]
            < short_candidates[2][0] < strings[mark][0] < short_candidates[3][0]):
        raise ValueError("Candidate layout is not recognized; refusing to guess")
    return long_candidates[0][1] + "=", short_candidates[0][1] + "==", short_candidates[3][1] + "=="


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dll", type=Path, help="Path to your locally installed CPS1 cpservices.dll")
    ap.add_argument("--resource", type=Path, help="Optional CPS1 resources/mototrbocps file")
    ap.add_argument("--output", type=Path, default=Path("codeplug.cfg"),
                    help="Private output config (default: ./codeplug.cfg)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing config")
    args = ap.parse_args()
    if not args.dll.is_file():
        ap.error("DLL not found: %s" % args.dll)
    data = args.dll.read_bytes()
    if data[:2] != b"MZ":
        ap.error("Input is not a Windows DLL/PE file")
    try:
        key, iv, signing_password = find_values(data)
    except ValueError as e:
        ap.error(str(e))
    resource = args.resource
    if resource is None:
        candidate = args.dll.parent / "resources" / "mototrbocps"
        if candidate.is_file():
            resource = candidate
    if args.output.exists() and not args.force:
        ap.error("Output already exists; use --force to replace it")
    lines = ["[codeplug]", "key = " + key, "iv = " + iv,
             "signing_password = " + signing_password]
    if resource is not None:
        if not resource.is_file():
            ap.error("Resource not found: %s" % resource)
        encoded = base64.b64encode(resource.read_bytes()).decode("ascii")
        if not encoded:
            ap.error("Resource is empty")
        chunks = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
        lines += ["signing_key = " + chunks[0]]
        lines += [" " + s for s in chunks[1:]]
    else:
        print("NOTE: resources/mototrbocps not found; signing_key omitted.", file=sys.stderr)
        print("This config may suffice for reading, but is not a full original-style config.",
              file=sys.stderr)
    # Private output, created with restrictive permissions on POSIX.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if args.force else os.O_EXCL)
    fd = os.open(args.output, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    if os.name != "nt":
        os.chmod(args.output, 0o600)
    print("Prepared private configuration:", args.output)
    print("Key material intentionally not displayed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
