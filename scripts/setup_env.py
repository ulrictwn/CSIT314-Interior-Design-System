"""Create missing local settings without replacing existing database credentials."""
import os
import re
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / '.env'
existing = path.read_text() if path.exists() else ''
settings = {
    'POSTGRES_USER': 'postgres', 'POSTGRES_DB': 'interior_design',
    'POSTGRES_PASSWORD': secrets.token_hex(32), 'POSTGRES_HOST': 'db', 'POSTGRES_PORT': '5432',
    'SECRET_KEY': secrets.token_hex(32), 'COOKIE_SECURE': 'true' if os.getenv('CODESPACES') == 'true' else 'false',
    'PROFILE_DEVELOPMENT_PREVIEW': 'false',
}
with path.open('a') as stream:
    for key, value in settings.items():
        if not re.search(rf'^{re.escape(key)}=', existing, flags=re.MULTILINE):
            stream.write(f'\n{key}={value}\n')
try:
    path.chmod(0o600)
except OSError:
    pass
print('Local settings are ready. Existing values were preserved. No secret values were printed.')
