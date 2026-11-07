import click
from sqlalchemy import inspect
from infrastructure.database import db
from infrastructure.migrations import upgrade_database
from infrastructure.permissions import DEFAULT_PROFILES, ADMIN_PERMISSIONS
from infrastructure.errors import DomainError
from entity.profile.user_profile import UserProfile
from entity.accounts.user_account import UserAccount
from boundary.validation import username_value, password_value, email_address, required_text as required


def register_commands(app):
    @app.cli.command('upgrade-db')
    def upgrade_db():
        """Preserve existing data and upgrade all Stories 1–48 tables."""
        try:
            upgrade_database()
        except RuntimeError as error:
            raise click.ClickException(str(error)) from error
        click.echo('Database ready. Tables: ' + ', '.join(inspect(db.engine).get_table_names()))
    app.cli.add_command(upgrade_db, 'init-db')

    @app.cli.command('bootstrap-admin')
    @click.option('--username', prompt=True)
    @click.option('--email', prompt=True)
    @click.option('--full-name', default='System Administrator', show_default=True)
    @click.option('--phone-number', prompt=True)
    @click.password_option(envvar='NESTORA_ADMIN_PASSWORD', confirmation_prompt=True)
    def bootstrap_admin(username, email, full_name, phone_number, password):
        """Create an initial User Admin from the trusted server terminal."""
        try:
            username, email, password = username_value(username), email_address(email), password_value(password)
            full_name, phone_number = required(full_name, 'Full name', 120), required(phone_number, 'Phone number', 40)
            if UserAccount.userAccountExists(username) or db.session.execute(db.select(UserAccount.account_id).where(
                    db.func.lower(UserAccount.email) == email)).first():
                raise DomainError('The username or email already exists. Use reset-password for an existing account.')
            for name, permissions in DEFAULT_PROFILES.items():
                if UserProfile.getProfile(name) is None:
                    new_profile = UserProfile()
                    if not new_profile.createUserProfile(name, f'{name} platform role.', 'Active', permissions):
                        raise DomainError(new_profile.error_message)
            profile = UserProfile.getProfile('User Admin')
            profile.status = 'Active'
            profile.permissions = sorted(set(profile.permissions or []) | ADMIN_PERMISSIONS)
            db.session.flush()
            new_account = UserAccount()
            if not new_account.createUserAccount(username, full_name, email, phone_number, profile.profile_id, password=password):
                raise DomainError(new_account.error_message)
            account = UserAccount.getByUsername(username)
        except DomainError as error:
            db.session.rollback()
            raise click.ClickException(str(error)) from error
        click.echo(f'User Admin {username} ({account.account_id}) created. Sign in at /login.')

    @app.cli.command('reset-password')
    @click.option('--username', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def reset_password(username, password):
        try:
            password_value(password)
            account = UserAccount.getByUsername(username)
            if account is None:
                raise DomainError('User account not found.')
            account.set_password(password)
            db.session.commit()
        except DomainError as error:
            raise click.ClickException(str(error)) from error
        click.echo('Password changed.')
