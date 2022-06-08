import xml.etree.ElementTree as ET
import argparse
import pathlib
import shutil
import androguard.core.bytecodes.axml as axml
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Extract Manifest and NSC from APKTool decodes')
parser.add_argument('in_dir', metavar='in-dir', type=pathlib.Path,
                    help='Directory with app manifests')
parser.add_argument('out_dir', metavar='out-dir', type=pathlib.Path,
                    help='Output directory')

args = parser.parse_args()
no_nsc = 0
has_nsc = 0
filenames = {}
has_targetSdk = {}
no_targetSdk = {}
has_minSdk = {}
no_minSdk = {}
out_dir = args.out_dir
out_dir.mkdir(exist_ok=True,parents=True)
for name in tqdm(args.in_dir.rglob('apktool.yml'), 'Parsed apps'):
    app_dir = name.parent
    manifest_path = app_dir.joinpath('AndroidManifest.xml')
    manifest = ET.parse(manifest_path)
    attr = manifest.find('./application').attrib
    app_name = attr.get('{http://schemas.android.com/apk/res/android}name')
    nsc_res = attr.get('{http://schemas.android.com/apk/res/android}networkSecurityConfig')
    targetSdk = manifest.find('./uses-sdk').attrib.get('{http://schemas.android.com/apk/res/android}targetSdkVersion')
    minSdk = manifest.find('./uses-sdk').attrib.get('{http://schemas.android.com/apk/res/android}minSdkVersion')
    if nsc_res is None or nsc_res[:5] != '@xml/':
        no_nsc += 1
        if (targetSdk is not None and minSdk is not None):
            if (targetSdk not in no_targetSdk):
                no_targetSdk[targetSdk] = 0
            no_targetSdk[targetSdk] += 1
            if (minSdk not in no_minSdk):
                no_minSdk[minSdk] = 0
            no_minSdk[minSdk] += 1
        continue
    has_nsc += 1
    if (targetSdk not in has_targetSdk):
        has_targetSdk[targetSdk] = 0
    has_targetSdk[targetSdk] += 1
    if (minSdk not in has_minSdk):
        has_minSdk[minSdk] = 0
    has_minSdk[minSdk] += 1
    if nsc_res not in filenames:
        filenames[nsc_res] = 0
    filenames[nsc_res] += 1
    nsc_path = app_dir.joinpath('res').joinpath(nsc_res[1:]+'.xml')
    # only seend with Starbucks app, but good to handle in general
    if app_dir.joinpath('res/values/xmls.xml').exists() and not nsc_path.exists():
        xmls = ET.parse(app_dir.joinpath('res/values/xmls.xml'))
        filename = xmls.find(f'./item[@name="{nsc_res[5:]}"]').text
        nsc_path.parent.mkdir(parents=True,exist_ok=True)
        with open(app_dir.joinpath('unknown').joinpath(filename), 'rb') as axml_file:
            xml = axml.AXMLPrinter(axml_file.read()).get_xml()
        with open(nsc_path, 'wb') as out:
            out.write(xml)
    if not nsc_path.exists():
        print(f'Something really weird with app {app_name} ({app_dir}), please check file manually')
    shutil.copy(nsc_path, out_dir.joinpath(str(app_dir.name)[4:-6]+'.xml'))
    
print(f'{no_nsc} have no NSC, {has_nsc} have an NSC')
print('Filename stats:')
for name, count in sorted(sorted(filenames.items()), key=lambda x:x[1], reverse=True):
    print(f'{name}: {count}')
print('Has NSC Target SDK stats:')
for name, count in sorted(sorted(has_targetSdk.items()), key=lambda x:x[1], reverse=True):
    print(f'{name}: {count}')
print('No NSC Target SDK stats:')
for name, count in sorted(sorted(no_targetSdk.items()), key=lambda x:x[1], reverse=True):
    print(f'{name}: {count}')
print('Has NSC Min SDK stats:')
for name, count in sorted(sorted(has_minSdk.items()), key=lambda x:x[1], reverse=True):
    print(f'{name}: {count}')
print('No NSC Min SDK stats:')
for name, count in sorted(sorted(no_minSdk.items()), key=lambda x:x[1], reverse=True):
    print(f'{name}: {count}')