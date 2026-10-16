"""Package only tracked application sources after CI has passed."""
from pathlib import Path, PurePosixPath
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / 'dist' / 'nestora-user-profiles.zip'
output.parent.mkdir(exist_ok=True)
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
allowed_folders = {'boundary', 'control', 'entity', 'infrastructure', 'static', 'templates', 'scripts', 'docs', 'tests', '.github'}
allowed_files = {'app.py', 'README.md', 'requirements.txt', 'requirements.lock', 'requirements-dev.txt', 'pytest.ini', '.env.example', '.gitignore'}
denied_parts = {'__pycache__', '.venv', '.postgres-data', 'uploads', 'instance', 'backups'}
count = 0
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for name in tracked:
        if not name:
            continue
        relative = PurePosixPath(name)
        path = root / name
        if not path.is_file() or path.is_symlink() or any(part in denied_parts for part in relative.parts):
            continue
        if relative.name.startswith('.env') and relative.name != '.env.example':
            continue
        if relative.suffix in {'.pyc', '.sqlite', '.sqlite3', '.db', '.pem', '.key'}:
            continue
        if len(relative.parts) == 1 and name not in allowed_files:
            continue
        if len(relative.parts) > 1 and relative.parts[0] not in allowed_folders:
            continue
        archive.write(path, name)
        count += 1
    if not count:
        raise RuntimeError('No tracked application source files were found.')
print(f'Packaged {count} tracked source files into {output.relative_to(root)}. No application deployment was performed.')
