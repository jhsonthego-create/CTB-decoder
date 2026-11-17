# Legacy CPS1 `.ctb` XML decoder

Independent, read-only Python tool to inspect legacy Motorola CPS1/16 `.ctb`
archives using **key material supplied locally by the user**. Not affiliated
with, endorsed by, or supported by Motorola Solutions.

The repository contains **no proprietary keys, Motorola binaries, codeplug
samples, entitlement responses, or license-generation functionality**.

## Requirements

- Python 3.9 or later
- `python3 -m pip install cryptography`

## Use without a configuration file

```bash
python3 ctb_inspect_decode_xml.py YOUR_ARCHIVE.ctb --prompt-keys
```

The script requests the Base64-encoded AES key and IV through masked prompts.
These values are not placed in your shell command history or written to output.
Use only key material you are authorized to use. The script does **not** recover
keys from Motorola products, and does **not** validate entitlement rights.

## Use an existing private local config (optional)

```bash
python3 ctb_inspect_decode_xml.py YOUR_ARCHIVE.ctb --config /path/outside/repository/codeplug.cfg
```

Copy `codeplug.cfg.example` to a **private location outside the repository**,
then fill in your authorized Base64 values. The script also supports its original
local `codeplug.cfg` auto-detection for compatibility, but keeping the file
outside the repository is strongly preferred.

## Behavior

- Reads a legacy XML `ARCHIVE` envelope with a Base64 `RADIO` payload.
- Decodes locally supplied AES-CBC data, checks the GZIP header, and expands XML.
- Preserves the original archive unchanged.
- Escapes only invalid numeric XML character references, preserving the exact
  unmodified decoded XML in a separate `.raw.xml` backup when needed.
- Refuses to overwrite existing outputs unless `--overwrite` is explicit.
- Does not support CPS2 `.xctb`/`.ctb2`, writing radio archives, installing radio
  features, generating keys or bypassing product licensing.

**Output confidentiality:** Decoded files may contain radio programming data,
passwords, RAS/enhanced-privacy keys, radio serials, and contact information.
Never upload decoded files or real-world archives to a public repository.

## GitHub publication checklist

1. Create a **fresh** repository with only these reviewed files. Do not publish
   a repository whose history ever contained real keys or private codeplugs.
2. Do not include any actual `codeplug.cfg`, copied CPS DLL/EXE, real codeplug,
   customer archive, licensed feature blob, or derived encryption key/IV.
3. Check `git status --short` and `git ls-files` before publishing. A `.gitignore`
   protects against accidental new adds, not against files committed earlier.
4. Review documentation and tests for serial numbers, passwords, tokens, and
   data copied from proprietary code.
5. Add an appropriate open-source license **only if you have the rights to grant it**;
   the author has to decide licensing of the supplied code.
6. Consider an IP attorney's review before publishing a tool that decodes an
   access-controlled vendor format. Merely omitting keys does not guarantee
   immunity under copyright, trade-secret, or anti-circumvention laws.

See [PUBLICATION-NOTICE.md](PUBLICATION-NOTICE.md) for limitations.

## Offline synthetic test

```bash
python3 -m unittest discover -s tests -v
```

The test creates a synthetic archive using dummy keys. It does not
contain or request authentic vendor key material.
