"""Synthetic, self-contained test data. No Motorola files or real keys."""
import base64
import gzip
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SCRIPT = Path(__file__).resolve().parents[1] / 'ctb_inspect_decode_xml.py'


class DecoderTests(unittest.TestCase):
    def test_synthetic_ctb_and_no_overwrite(self):
        key, iv = bytes(range(32)), bytes(range(16))
        plaintext = (b'<RadioConfiguration><RadioAlias>SYNTHETIC</RadioAlias>'
                     b'<Invalid>Bad numeric &#x0; reference</Invalid>'
                     b'</RadioConfiguration><SIGNATURE>TEST</SIGNATURE>')
        zipped = gzip.compress(plaintext)
        padding = 16 - len(zipped) % 16
        encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
        encrypted = encryptor.update(zipped + bytes([padding]) * padding) + encryptor.finalize()
        archive = (b'<ARCHIVE TYPE="CTB"><RADIO ENCODING="base64">' +
                   base64.b64encode(encrypted) + b'</RADIO></ARCHIVE>')
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            source = root / 'synthetic.ctb'
            source.write_bytes(archive)
            config = root / 'private.cfg'
            config.write_text('[codeplug]\nkey = ' + base64.b64encode(key).decode() +
                              '\niv = ' + base64.b64encode(iv).decode() + '\n')
            args = [sys.executable, str(SCRIPT), str(source), '--config', str(config)]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), archive)
            self.assertIn(b'&amp;#x0;', (root / 'synthetic.decoded.xml').read_bytes())
            self.assertEqual((root / 'synthetic.decoded.raw.xml').read_bytes(),
                             plaintext.split(b'<SIGNATURE>')[0])
            result2 = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(result2.returncode, 0)
            self.assertIn('already exists', result2.stderr)


if __name__ == '__main__':
    unittest.main()
