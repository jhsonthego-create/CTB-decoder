# CTB-decoder
CTB codeplug decoder for mainstream DMR radio

## Trademarks & Disclaimer

MOTOROLA, MOTO, MOTOROLA SOLUTIONS, and MOTOTRBO are trademarks or registered trademarks of Motorola Trademark Holdings, LLC. All other trademarks are the property of their respective owners.

This project is an independent work and is not affiliated with, endorsed by, or sponsored by Motorola Solutions, Inc.

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

# Python CPS1 config preparation

****Original project: https://github.com/george-hopkins/codeplug-prepare *****

This independent Python compatibility implementation reads a **locally supplied** `CPS1 cpservices.dll` and prepares a **private** `codeplug.cfg`. It uses only Python's standard library.

WSL: python3 codeplug_prepare.py "/mnt/c/Program Files (x86)/Motorola/MOTOTRBO CPS/cpservices.dll" --resource "/mnt/c/Program Files (x86)/Motorola/MOTOTRBO CPS/resources/mototrbocps"

default
python3 codeplug_prepare.py /path/to/cpservices.dll

If you also have the original `resources/mototrbocps` file, put it in a `resources/` directory next to `cpservices.dll`, or specify `--resource /path/to/mototrbocps`. That enables the additional `signing_key` field. Without it, the script writes the other three fields.

This is **not a general .NET IL parser**: it recognizes the observed CPS1 string layout, validates candidate sizes and Base64 encoding, and refuses to guess if the layout changes. It was tested against a user-supplied DLL, not every CPS version.

**Never commit `codeplug.cfg`, CPS DLLs, radio codeplugs, or other vendor files to a public GitHub repository.** The script doesn't contain the extracted values.

No radio is contacted or modified. No license activation or entitlement changes are performed.

