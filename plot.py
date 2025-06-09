from pathlib import Path

files = []

for file in Path('./src').rglob('*'):
    if file.is_file() and file.suffix == '.py':
        files.append(file)
files.append('app.py')

cnt = 0
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        cnt += len(f.readlines())
print(f'{len(files)} file, {cnt} lines')