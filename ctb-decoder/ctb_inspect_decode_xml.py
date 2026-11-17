#!/usr/bin/env python3
"""Motorola CPS 16 / CPS 1 legacy .CTB AES decoder -> valid XML.

Run:
    python3 ctb_inspect_decode_xml.py cps16codeplug.ctb --prompt-keys
    python3 ctb_inspect_decode_xml.py cps16codeplug.ctb --config /private/path/codeplug.cfg

The script includes NO AES key or IV. For a single-file workflow use
--prompt-keys (masked prompts; no shell command history). Keep locally supplied
configuration outside public repositories. Never commit decoded output.

The source .ctb and key config are never modified. If the decoded XML
contains invalid numeric character references, the tool escapes only those
references to preserve their literal text in an XML-safe document, and also
preserves an exact raw version. Existing output files are not overwritten
unless --overwrite is explicitly provided.

Requires cryptography: python3 -m pip install cryptography
"""
import argparse
import base64
import configparser
import getpass
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib

BAD_CHAR_REF = re.compile(rb'&#(?:x[0-9A-Fa-f]+|[0-9]+);')

def xml_codepoint_valid(cp):
    return cp in (9, 10, 13) or (32 <= cp <= 0xD7FF) or (0xE000 <= cp <= 0xFFFD) or (0x10000 <= cp <= 0x10FFFF)

def normalize_numeric_refs(data):
    fixed = 0
    def replace(match):
        nonlocal fixed
        token = match.group()
        try:
            n = int(token[3:-1], 16) if token[2:3] == b'x' else int(token[2:-1], 10)
        except ValueError:
            return token
        if xml_codepoint_valid(n):
            return token
        fixed += 1
        # Escape the ampersand. Parsed element text still contains the literal
        # string '&#xFFFF;' rather than losing the original information.
        return b'&amp;' + token[1:]
    return BAD_CHAR_REF.sub(replace, data), fixed

def save(path, data, overwrite):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not overwrite:
        with path.open('xb') as f:
            f.write(data)
        return
    fd, tmp = tempfile.mkstemp(prefix='.ctb-', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path, help='Input CPS1 .ctb file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config', type=Path, help='Local private INI file containing [codeplug] key and iv')
    group.add_argument('--prompt-keys', action='store_true', help='Prompt privately for Base64 AES key and IV (no config needed)')
    parser.add_argument('--output', type=Path, help='XML path (default: <source>.decoded.xml)')
    parser.add_argument('--overwrite', action='store_true', help='Allow replacing existing XML output, never the source CTB or key config')
    parser.add_argument('--serial', help='Optional known serial number to locate in decoded XML')
    parser.add_argument('--password', help='Optional known password to locate in decoded XML')
    args = parser.parse_args()
    source = args.source.resolve()
    cfgpath = None
    if args.config:
        cfgpath = args.config.resolve()
    elif not args.prompt_keys:
        # Backward compatibility: discover a local configuration only.
        # Nothing here generates, discovers, or embeds encryption keys.
        candidates = []
        for directory in (source.parent, Path(__file__).resolve().parent):
            for name in ('codeplug.cfg', 'codeplug(1).cfg'):
                p = directory / name
                if p.is_file() and p.resolve() not in candidates:
                    candidates.append(p.resolve())
        if len(candidates) != 1:
            parser.error('Use --prompt-keys or --config /private/path/codeplug.cfg (found {} local files)'.format(len(candidates)))
        cfgpath = candidates[0]
    dest = (args.output if args.output else source.with_name(source.stem + '.decoded.xml')).resolve()
    if dest == source or (cfgpath is not None and dest == cfgpath):
        parser.error('Output must not overwrite source CTB or key configuration')
    raw_dest = dest.with_name(dest.stem + '.raw.xml')
    if raw_dest == source or raw_dest == dest or (cfgpath is not None and raw_dest == cfgpath):
        parser.error('Raw XML backup path conflicts with an input file')
    if dest.exists() and not args.overwrite:
        parser.error('Output already exists: {} (use --overwrite if intentional)'.format(dest))

    data = source.read_bytes()
    radio_archive = ET.fromstring(data)
    if radio_archive.tag != 'ARCHIVE':
        raise ValueError('Not a legacy Motorola CTB ARCHIVE XML file')
    radio = radio_archive.find('RADIO')
    if radio is None or radio.get('ENCODING', '').lower() != 'base64':
        raise ValueError('Missing Base64 RADIO payload')
    enc = base64.b64decode(''.join(radio.itertext()), validate=True)
    if not enc or len(enc) % 16:
        raise ValueError('Invalid AES payload length')
    if args.prompt_keys:
        key_b64 = getpass.getpass('Base64 AES key (not echoed): ').strip()
        iv_b64 = getpass.getpass('Base64 IV (not echoed): ').strip()
    else:
        cfg = configparser.ConfigParser()
        with cfgpath.open('r', encoding='utf-8-sig') as cf:
            cfg.read_file(cf)
        key_b64 = cfg.get('codeplug', 'key').strip()
        iv_b64 = cfg.get('codeplug', 'iv').strip()
    key = base64.b64decode(key_b64, validate=True)
    iv = base64.b64decode(iv_b64, validate=True)
    if len(key) not in (16, 24, 32) or len(iv) != 16:
        raise ValueError('Invalid AES key or IV length')

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    context = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()  # cryptography API
    padded = context.update(enc) + context.finalize()
    if not padded.startswith(b'\x1f\x8b\x08'):
        raise ValueError('Decoding did not produce a GZIP header; check CPS key/IV')
    # zlib ignores the possible trailing AES padding, as in the prior decoder.
    decoded = zlib.decompress(padded, wbits=16 + zlib.MAX_WBITS)
    if decoded.startswith(b'\xef\xbb\xbf'):
        decoded = decoded[3:]
    signature = decoded.rfind(b'<SIGNATURE>')
    if signature >= 0:
        decoded = decoded[:signature]
    valid_xml, replacements = normalize_numeric_refs(decoded)
    try:
        root = ET.fromstring(valid_xml)
    except ET.ParseError as exc:
        raise ValueError('XML is still malformed after checking numeric references: {}'.format(exc)) from exc

    if replacements and raw_dest.exists() and not args.overwrite:
        parser.error('Raw backup already exists: {} (use --overwrite if intentional)'.format(raw_dest))
    if replacements:
        save(raw_dest, decoded, args.overwrite)
    save(dest, valid_xml, args.overwrite)
    print('CTB SOURCE: {}'.format(source.name))
    print('ARCHIVE TYPE: {}'.format(radio_archive.get('TYPE')))
    print('DECODING: SUCCESS')
    print('XML ROOT: {}'.format(root.tag))
    print('XML SIZE: {} bytes'.format(len(valid_xml)))
    print('XML SHA256: {}'.format(hashlib.sha256(valid_xml).hexdigest()))
    print('INVALID XML CHARACTER REFERENCES ESCAPED: {}'.format(replacements))
    print('XML OUTPUT: {}'.format(dest))
    if replacements:
        print('EXACT RAW DECODING BACKUP: {}'.format(raw_dest))
    for label, needle in [('SERIAL', args.serial), ('PASSWORD', args.password)]:
        if needle:
            print('{} PRESENT IN XML: {}'.format(label, needle.encode('utf-8') in valid_xml))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, ET.ParseError, configparser.Error, zlib.error) as e:
        sys.exit('ERROR: {}'.format(e))
