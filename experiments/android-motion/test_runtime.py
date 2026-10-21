import tempfile
import unittest
import zipfile
from pathlib import Path
from runtime import parse_package, extract_checked, create_phone

XML = b'''<repository><license id="terms">Example terms</license>
<remotePackage path="emulator"><uses-license ref="terms"/><channelRef ref="channel-2"/><archives><archive><host-os>windows</host-os><complete><size>99</size><checksum type="sha1">preview</checksum><url>preview.zip</url></complete></archive></archives></remotePackage>
<remotePackage path="emulator"><uses-license ref="terms"/><channelRef ref="channel-0"/><archives>
<archive><host-os>linux</host-os><complete><size>1</size><checksum type="sha1">linux</checksum><url>linux.zip</url></complete></archive>
<archive><host-os>windows</host-os><complete><size>100</size><checksum type="sha1">abc</checksum><url>stable.zip</url></complete></archive>
</archives></remotePackage></repository>'''


class RuntimeTests(unittest.TestCase):
    def test_stable_windows_package(self):
        result = parse_package(XML, 'https://dl.google.com/android/repository/repository2-3.xml', 'emulator')
        self.assertEqual(result['url'], 'https://dl.google.com/android/repository/stable.zip')
        self.assertEqual(result['size'], 100)
        self.assertEqual(result['license'], 'Example terms')

    def test_foreign_host_rejected(self):
        with self.assertRaises(ValueError):
            parse_package(XML.replace(b'stable.zip', b'https://evil.example/file.zip'), 'https://dl.google.com/repo.xml', 'emulator')

    def test_missing_license_rejected(self):
        with self.assertRaises(ValueError):
            parse_package(XML.replace(b'Example terms', b''), 'https://dl.google.com/repo.xml', 'emulator')

    def test_traversal_rejected_before_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'input.zip'
            for bad in ('../escape', '/absolute', 'C:/escape', 'x\\..\\escape'):
                with zipfile.ZipFile(archive, 'w') as bundle:
                    bundle.writestr('good/file', 'content')
                    bundle.writestr(bad, 'bad')
                with self.assertRaises(ValueError):
                    extract_checked(archive, Path(tmp) / 'out')
                self.assertFalse((Path(tmp) / 'out/good/file').exists())

    def test_phone_config_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            create_phone(tmp)
            config = Path(tmp) / 'phones/JoyBridge.avd/config.ini'
            self.assertIn('PlayStore.enabled=true', config.read_text())
            config.write_text('custom configuration')
            create_phone(tmp)
            self.assertEqual(config.read_text(), 'custom configuration')


if __name__ == '__main__':
    unittest.main()
