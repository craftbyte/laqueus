# Laqueus

## Automated analysis of Android Network Security Configurations

This project was made as part of the [Mobile Security](https://www.iaik.tugraz.at/course/mobile-security-705012-sommersemester-2022/) class at TU Graz in 2022. You can find the results on [GitHub Pages](https://craftbyte.github.io/laqueus/).

Files:

 - `process.sh` - Extract files using apktool
 - `extract_nsc.py` - Read apktool dumps and extract the NSCs, also prints some info about the files
 - `analyze.py` - Will analyze a folder of NSCs to print some stats and create a CSV

Usage:

```bash
pip3 install androguard tqdm
./process.sh in_dir out_dir_apk
python3 extract_nsc.py out_dir_apk out_dir_nsc
python3 analyze.py out_dir_nsc csv_path
```
