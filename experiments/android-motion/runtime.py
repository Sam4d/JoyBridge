"""Download official Android components into JoyBridge's own user directory."""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath

REPOSITORY = 'https://dl.google.com/android/repository/'
SOURCES = [(REPOSITORY + 'repository2-3.xml', 'emulator'),
           (REPOSITORY + 'repository2-3.xml', 'platform-tools'),
           (REPOSITORY + 'sys-img/google_apis_playstore/sys-img2-3.xml',
            'system-images;android-35;google_apis_playstore;x86_64')]


def parse_package(data, url, package):
    root = ET.fromstring(data)
    # Namespace-insensitive parsing across Google's repository schema versions.
    for element in root.iter():
        element.tag = element.tag.split('}')[-1]
    licenses = {item.get('id'): ''.join(item.itertext()) for item in root.findall('license')}
    for item in root.findall('remotePackage'):
        if item.get('path') != package or item.find('obsolete') is not None:
            continue
        channel = item.find('channelRef')
        if channel is not None and channel.get('ref') != 'channel-0':
            continue
        for archive in item.findall('./archives/archive'):
            host = archive.findtext('host-os')
            if host and host != 'windows':
                continue
            complete = archive.find('complete')
            if complete is None:
                continue
            checksum = complete.find('checksum')
            if checksum is None:
                raise ValueError('Google did not supply a download checksum.')
            algorithm = checksum.get('type', 'sha1').lower().replace('-', '')
            if algorithm not in ('sha1', 'sha256'):
                raise ValueError('Unsupported download checksum.')
            download = urllib.parse.urljoin(url, complete.findtext('url', ''))
            parsed = urllib.parse.urlparse(download)
            if parsed.scheme != 'https' or parsed.hostname != 'dl.google.com':
                raise ValueError('Unexpected Android download source.')
            license_node = item.find('uses-license')
            license_text = licenses.get(license_node.get('ref') if license_node is not None else '', '')
            if not license_text.strip():
                raise ValueError('The Android license text is missing.')
            return dict(package=package, url=download, size=int(complete.findtext('size')),
                        algorithm=algorithm, checksum=checksum.text.strip(), license=license_text)
    raise ValueError('The required Android component is unavailable: ' + package)


def catalog():
    cache = {}
    result = []
    for url, package in SOURCES:
        if url not in cache:
            with urllib.request.urlopen(url, timeout=30) as response:
                cache[url] = response.read(8 * 1024 * 1024)
        result.append(parse_package(cache[url], url, package))
    return result


def extract_checked(archive, destination):
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            path = PurePosixPath(item.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in item.filename
                    or ':' in item.filename or (item.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Unsafe Android archive entry.')
        bundle.extractall(destination)


def install(root, packages, report, cancelled):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(root).free < 16 * 1024**3:
        raise RuntimeError('Please free at least 16 GB on this drive, then try again.')
    sdk = root / 'sdk'
    sdk.mkdir(exist_ok=True)
    for package in packages:
        if cancelled.is_set():
            raise RuntimeError('Setup cancelled. You can run it again later.')
        name = package['package']
        target = sdk / ('system-images/android-35/google_apis_playstore/x86_64' if name.startswith('system-images;') else name)
        marker = target / '.joybridge-package.json'
        if marker.exists() and json.loads(marker.read_text()).get('checksum') == package['checksum']:
            report('Already prepared: ' + name.split(';')[0])
            continue
        with tempfile.TemporaryDirectory(prefix='download-', dir=root) as temp:
            archive = Path(temp) / 'component.zip'
            digest = hashlib.new(package['algorithm'])
            received = 0
            with urllib.request.urlopen(package['url'], timeout=30) as response, archive.open('wb') as output:
                while block := response.read(1024 * 1024):
                    if cancelled.is_set():
                        raise RuntimeError('Setup cancelled. You can run it again later.')
                    output.write(block)
                    digest.update(block)
                    received += len(block)
                    if received > package['size']:
                        raise RuntimeError('The download size did not match. Please retry.')
                    report(f"Downloading {name.split(';')[0]}: {received * 100 // package['size']}%")
            if received != package['size'] or digest.hexdigest().lower() != package['checksum'].lower():
                raise RuntimeError('Download verification failed. Please retry.')
            report('Unpacking ' + name.split(';')[0] + '…')
            unpack = Path(temp) / 'unpack'
            extract_checked(archive, unpack)
            expected = 'x86_64' if name.startswith('system-images;') else name
            source = unpack / expected
            required = {'emulator':'emulator.exe', 'platform-tools':'adb.exe', 'x86_64':'system.img'}[expected]
            if not (source / required).is_file():
                raise RuntimeError('Android archive layout changed. An app update is needed.')
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(source), str(target))
            marker.write_text(json.dumps({k: v for k, v in package.items() if k != 'license'}, indent=2))
    create_phone(root)
    (root / 'accepted-licenses.txt').write_text('\n\n'.join(dict.fromkeys(p['license'] for p in packages)), encoding='utf-8')


def create_phone(root):
    avds = Path(root) / 'phones'
    phone = avds / 'JoyBridge.avd'
    phone.mkdir(parents=True, exist_ok=True)
    (avds / 'JoyBridge.ini').write_text('avd.ini.encoding=UTF-8\npath=' + str(phone.resolve()) + '\ntarget=android-35\n')
    config = phone / 'config.ini'
    if not config.exists():
        config.write_text('''avd.ini.encoding=UTF-8
AvdId=JoyBridge
avd.ini.displayname=JoyBridge Phone
abi.type=x86_64
hw.cpu.arch=x86_64
hw.cpu.ncore=2
hw.ramSize=2048
hw.lcd.width=720
hw.lcd.height=1280
hw.lcd.density=320
hw.gpu.enabled=yes
hw.gpu.mode=auto
hw.keyboard=yes
hw.accelerometer=yes
hw.gyroscope=yes
hw.sensors.orientation=yes
hw.audioInput=yes
hw.mainKeys=no
PlayStore.enabled=true
tag.id=google_apis_playstore
tag.display=Google Play
image.sysdir.1=system-images/android-35/google_apis_playstore/x86_64/
disk.dataPartition.size=6G
showDeviceFrame=no
skin.dynamic=yes
fastboot.forceColdBoot=yes
''')


def environment(root):
    env = os.environ.copy()
    env['ANDROID_HOME'] = str(Path(root) / 'sdk')
    env['ANDROID_AVD_HOME'] = str(Path(root) / 'phones')
    return env


def run(command, **kwargs):
    return subprocess.run([str(x) for x in command], capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=30,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), **kwargs)
