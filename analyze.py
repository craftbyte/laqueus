import xml.etree.ElementTree as ET
import argparse
import pathlib
import csv
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Parse a directory if NSC XMLs')
parser.add_argument('in_dir', metavar='in-dir', type=pathlib.Path,
                    help='Directory with NSCs')
parser.add_argument('out_file', metavar='out-csv', type=argparse.FileType('w', encoding='UTF-8'),
                    help='CSV file to output to')
args = parser.parse_args()

# Set up counters
appCount = 0
hasEmptyConfig = 0
hasPinning = 0
hasExpiringPinning = 0
hasBsc = 0
hasBaseClear = 0
hasBaseConfigTrustAnchors = 0
hasBaseUserCerts = 0
hasBaseSystemCerts = 0
hasBaseCustomCerts = 0
hasDomainConfigs = 0
hasDomainConfigClear = 0
hasNestedDomainConfigs = 0
hasNestedDomainConfigClear = 0
hasCrazyDomainConfigs = 0
hasDebug = 0
hasDebugUserCerts = 0
hasDebugSystemCerts = 0
hasDebugCustomCerts = 0
pinsetCount = 0
hasExpire = 0

writer = csv.writer(args.out_file)

header = ['appName', 'hasConfig', 'pinSetCount', 'expiringPinSetCount', 'hasBaseConfig', 'hasBaseConfigClear',
            'hasBaseConfigTrustAnchors', 'hasBaseConfigUserCerts', 'hasBaseConfigSystemCerts',
            'hasBaseConfigCustomCerts', 'baseConfigCustomCertCount', 'hasDomainConfigs', 'domainConfigsPermitClear',
            'domainConfigsNestedPermitClear', 'hasDebugOverrides', 'hasDebugUserCerts', 'hasDebugSystemCerts',
            'hasDebugCustomCerts', 'debugCustomCertCount']

writer.writerow(header)

for name in tqdm(args.in_dir.rglob('*.xml'), 'Parsed apps'):
    appCount += 1
    appName = name.stem

    nsc = ET.parse(name)

    emptyConfig = len(list(nsc.getroot())) == 0
    if emptyConfig:
        hasEmptyConfig += 1
        continue

    pinSets = nsc.findall('.//pin-set')
    pinsetCount += len(pinSets)
    pinsetsPresent = len(pinSets) > 0
    expiringPinSets = 0
    if pinsetsPresent:
        hasPinning += 1
        for pinset in pinSets:
            if ('expiration' in pinset.attrib.keys()):
                hasExpire += 1
                expiringPinSets += 1
        if len(pinSets) == expiringPinSets:
            hasExpiringPinning += 1

    bsc = nsc.find('./base-config')
    baseConfigPresent = bsc is not None
    baseTrustAnchorsPresent = False
    customBaseCertCount = 0
    customCerts = False
    baseUserCerts = False
    baseSystemCerts = False
    baseClear = False
    if baseConfigPresent:
        hasBsc += 1
        clear = bsc.attrib.get('cleartextTrafficPermitted')
        baseClear = clear is not None and clear == 'true'
        if baseClear:
            hasBaseClear += 1
        certs = bsc.findall('./trust-anchors/certificates')
        for cert in certs:
            baseTrustAnchorsPresent = True
            src = cert.attrib.get('src')
            if src == 'user':
                baseUserCerts = True
                continue
            if src == 'system':
                baseSystemCerts = True
                continue
            customCerts = True
            customBaseCertCount += 1
    if baseTrustAnchorsPresent:
        hasBaseConfigTrustAnchors += 1
    if baseSystemCerts:
        hasBaseSystemCerts += 1
    if baseUserCerts:
        hasBaseUserCerts += 1
    if customCerts:
        hasBaseCustomCerts += 1

    domainConfigs = nsc.findall('./domain-config')
    domainConfigsPresent = len(domainConfigs) > 0
    if domainConfigsPresent:
        hasDomainConfigs += 1
    if nsc.find('./domain-config/domain-config') is not None:
        hasNestedDomainConfigs += 1
    if nsc.find('./domain-config/domain-config/domain-config') is not None:
        hasCrazyDomainConfigs += 1
    domainConfigsPermitClear = False
    domainConfigsNestedPermitClear = False
    for conf in domainConfigs:
        allowClear = conf.attrib.get('cleartextTrafficPermitted')
        if allowClear == 'true':
            domainConfigsPermitClear = True
        else: 
            for conf2 in conf.findall('./domain-config'):
                allowClear = conf2.attrib.get('cleartextTrafficPermitted')
                if allowClear == 'true':
                    domainConfigsNestedPermitClear = True
    if domainConfigsPermitClear:
        hasDomainConfigClear += 1
    if domainConfigsNestedPermitClear:
        hasNestedDomainConfigClear += 1
    
    debug = nsc.find('./debug-overrides')
    debugOverridesPresent = debug is not None
    debugUserCerts = False
    debugSystemCerts = False
    customDebugCerts = False
    customDebugCount = 0
    if debugOverridesPresent:
        hasDebug += 1
        certificates = debug.findall('./trust-anchors/certificates')
        for cert in certificates:
            src = cert.attrib.get('src')
            if src == 'user':
                debugUserCerts = True
                continue
            if src == 'system':
                debugSystemCerts = True
                continue
            customDebugCerts = True
            customDebugCount += 1
    if debugUserCerts:
        hasDebugUserCerts += 1
    if debugSystemCerts:
        hasDebugSystemCerts += 1
    if customDebugCerts:
        hasDebugCustomCerts += 1

    writer.writerow([appName, not emptyConfig, len(pinSets), expiringPinSets, baseConfigPresent, baseClear, baseTrustAnchorsPresent,
                    baseUserCerts, baseSystemCerts, customCerts, customBaseCertCount, domainConfigsPresent, domainConfigsPermitClear,
                    domainConfigsNestedPermitClear, debugOverridesPresent, debugUserCerts, debugSystemCerts, customDebugCerts,
                    customDebugCount])

args.out_file.close()

print(f'{appCount} app NSCs analyzed')
print(f'{hasEmptyConfig} have completely empty configs')
print(f'{hasBsc} have base config, {hasBaseClear} of which allow clear text and {hasBaseConfigTrustAnchors} set trust anchors')
print(f'{hasBaseUserCerts} allow user certs and {hasBaseSystemCerts} allow system certs')
print(f'{hasBaseCustomCerts} have custom base certs')
print(f'{hasDomainConfigs} have at least one domain config, {hasNestedDomainConfigs} have nested domain configs, {hasCrazyDomainConfigs} have crazy domain configs')
print(f'{hasDomainConfigClear} domain configs allow clear text, {hasNestedDomainConfigClear} nested domain configs allow clear text on non-clear domains')
print(f'{hasDebug} have debug overrides')
print(f'{hasDebugSystemCerts} debug overrides add system certs, {hasDebugUserCerts} add user certs and {hasDebugCustomCerts} custom certs')
print(f'{hasPinning} apps have pin sets, {hasExpiringPinning} of which have all sets expiring')
print(f'{hasExpire}/{pinsetCount} pinsets have expiration set')