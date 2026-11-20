# CTB Public Export Toolkit v0.4.2

## Run a converter with no filenames

1. **Go to https://github.com/jhsonthego-create/CTB-decoder** to create your own **private** `codeplug.cfg` from legitimately installed Motorola CPS1 resources. Never distribute your key, IV, or CPS files.
2. Install dependencies in your chosen package: `python3 -m pip install -r requirements.txt`.
3. Put `codeplug.cfg`, **one source `.ctb`**, and a compatible **genuine donor** (`.rdb` for Connect Systems, `.rcdx` for Hytera) in the working directory. Radio Foundry's six-CSV blank template ZIP is already bundled; no donor CSV is needed.
4. Run the relevant `2_..._Creator.py` without arguments:

| Format | No-argument command | Output |
| --- | --- | --- |
| Connect Systems CS711 / CS811 | `./2_ConnectSystems_RDB_Creator.py` | `<donor>-out.rdb`, per discovered donor model |
| Hytera PD782 | `./2_Hytera_RCDX_Creator.py` | `<donor>-out.rcdx` |
| Radio Foundry six-CSV ZIP | `./2_Foundry_CSV_Creator.py` | `<source>-out.zip` |

When discovery is ambiguous, the converter displays a manual command using `--ctbimport` and `--donor` as applicable; it does **not** ask questions or guess. `codeplug.cfg` search is current working directory first, then script directory. An explicit `--config` overrides discovery. Existing outputs and audit reports are not overwritten. Automatically discovered RDB/CTB output files are excluded from future donor/source selection.

## CTB decode tester — now truly zero-argument

`1_CTB_Decode_Tester.py` verifies a Motorola CPS1 CTB and prints its archive type, verified signature status, and programming record counts. **It is an inspector, not an exporter.** It now finds the single `.ctb` automatically from the working directory (or script directory if none exists in the working directory):

```sh
./1_CTB_Decode_Tester.py
```

If more than one CTB exists, select one without any interactive prompt:

```sh
./1_CTB_Decode_Tester.py --ctbimport radio.ctb
```

The legacy positional syntax `./1_CTB_Decode_Tester.py radio.ctb` is still accepted. If `codeplug.cfg` is missing, the big missing/invalid config banner points to the GitHub instructions.

## Motorola Quick Call II A-B/C-D

The parser supports `CALLFMT_AB`, `CALLFMT_AB_LONG_C`, and **`CALLFMT_AB_CD`**. In A-B/C-D, both A/B and C/D source tone pairs are read, validated, and preserved as separate decoded definitions. Combined Motorola alert behavior may **not** map identically to independent destination decode records. Connect Systems uses source-derived decode entries; Hytera/Foundry continue to report unmapped decode definitions rather than pretending to migrate them. **Destination CPS and radio behavior remain unverified.** Unknown formats or invalid tone values still fail closed.

## Helpers, extractions and safety

`tools/Motorola_TwoTone_Translator.py` is a helper imported automatically. Running it manually only displays the **THIS IS NOT AN INDEPENDENT SCRIPT** ASCII banner and does not convert a radio.

Conversion can create timestamped local extraction folders containing decoded CTB, donor RDB record inventory, or decrypted Hytera RCDX payload. These may contain sensitive radio information; **they are not shipped in the public ZIPs**. Use `--no-extract` on converters to disable extraction. The CTB tester does not create an extracted folder by itself.

The Connect Systems v0.4.1 minimal-donor compatibility changes remain intact. **Donors containing undocumented QCII record types can still be rejected safely**, rather than silently deleting unknown signaling content. The binary QCII mapping is experimental and requires CPS open/save/reopen and radio verification. In general, a successful decode, signature check, and binary readback **do not prove radio programming safety**.

MIT License retained in every package. No private keys, configs, radio sources, vendor DLLs or donor codeplugs are shipped. Package SHA256 hashes are in the manifest.
