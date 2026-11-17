# Python CPS1 config preparation

Original project: https://github.com/george-hopkins/codeplug-prepare

This independent Python compatibility implementation reads a **locally supplied** `cpservices.dll` and prepares a **private** `codeplug.cfg`. It uses only Python's standard library.
default:
python3 codeplug_prepare.py "/mnt/c/Program Files (x86)/Motorola/MOTOTRBO CPS/cpservices.dll" --resource "/mnt/c/Program Files (x86)/Motorola/MOTOTRBO CPS/resources/mototrbocps"
python3 codeplug_prepare.py /path/to/cpservices.dll


If you also have the original `resources/mototrbocps` file, put it in a `resources/` directory next to `cpservices.dll`, or specify `--resource /path/to/mototrbocps`. That enables the additional `signing_key` field. Without it, the script writes the other three fields.

This is **not a general .NET IL parser**: it recognizes the observed CPS1 string layout, validates candidate sizes and Base64 encoding, and refuses to guess if the layout changes. It was tested against a user-supplied DLL, not every CPS version.

**Never commit `codeplug.cfg`, CPS DLLs, radio codeplugs, or other vendor files to a public GitHub repository.** The script doesn't contain the extracted values.

No radio is contacted or modified. No license activation or entitlement changes are performed.
