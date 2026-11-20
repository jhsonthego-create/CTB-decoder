# CTB Public Export Toolkit v0.4.2 — CTB tester/QCII fix

## Fixes in all three public exporters

- Script `1_CTB_Decode_Tester.py` no longer requires positional `source_ctb` when exactly one `.ctb` is discoverable. Same CWD-first, script-directory-second candidate search as the converters. `--ctbimport radio.ctb` and the old positional form remain supported.
- Multiple candidate CTBs produce an unambiguous manual command and a nonzero status; no filenames are guessed or prompted for.
- Motorola `CALLFMT_AB_CD` Quick Call II decoding now preserves BOTH A/B and C/D tone pairs as two source definitions, with separate frequencies and audit count. Invalid/missing tones or unknown formats are still rejected.
- Unhandled source-validation `ValueError` in the optional tester now produces a short error instead of a Python traceback. An invalid/missing `codeplug.cfg` retains the existing large instructions banner.
- Updated package READMEs and added five synthetic regression tests per format; Connect Systems includes one additional QCII binary-patching test.

## Preserved from earlier releases

- Connect Systems v0.4.1 model-specific minimal-donor handling and CS711/CS811 no-argument discovery.
- Hytera/Foundry v0.4.0 converter functionality; Foundry's bundled six-CSV template.
- Donor identity retention, no-overwrite safeguards, timestamped extraction, MIT license, public-key signature check, SHA256 release manifest, and exclusion of all private source or decrypted materials.

## Verification and limitations

- Unit suites: Connect Systems **25**, Hytera **10**, Radio Foundry **10**, all passed.
- End-to-end: the user's supplied CTB was signature-verified and decoded successfully by the no-argument tester in all three packages; **32 channels, 12 contacts, 2 zones, 2 Quick Call II decode definitions**. Radio Foundry exported six CSVs in one ZIP. A different, recognized CS811 donor converted and binary-readback passed.
- The user's separate CS811 RDB donor contains an undocumented QCII decode kind `0x0004` and encode flag `0x0015`. The existing safety checks still reject that donor's QCII records pending verified interpretation. This is distinct from the CTB A-B/C-D parsing bug; **we have not claimed it fixed**.
- Destination CPS acceptance and on-air radio operation have not been verified.

No private key, source CTB, RDB/RCDX donor, normalized XML, or extracted programming data appears in this release.
