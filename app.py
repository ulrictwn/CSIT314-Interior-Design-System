
import os
from pathlib import Path
import click
from dotenv import load_dotenv
from flask import Flask, g, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from sqlalchemy import URL, event
from infrastructure.database import db
from infrastructure.errors import DomainError, AccessError, NotFoundError
from infrastructure.permissions import PERMISSION_OPTIONS

ROOT = Path(__file__).resolve().parent


class DevelopmentProfileActor:
    """Explicitly enabled local UI preview; never represents a stored account."""
    def has_permission(self, permission):
        return permission in PERMISSION_OPTIONS and permission.startswith('profile.')


def create_app(configuration=None):
    load_dotenv(ROOT / '.env')
    app = Flask(__name__)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        missing = [key for key in ('POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB') if not os.getenv(key)]
        if missing:
            raise RuntimeError('Run python scripts/setup_env.py and check .env. Missing: ' + ', '.join(missing))
        database_url = URL.create('postgresql+psycopg', username=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'], database=os.environ['POSTGRES_DB'],
            host=os.getenv('POSTGRES_HOST', 'db'), port=int(os.getenv('POSTGRES_PORT', '5432')))
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY'), SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False, SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
        PROFILE_DEVELOPMENT_PREVIEW=os.getenv('PROFILE_DEVELOPMENT_PREVIEW', 'false').lower() == 'true',
        PROFILE_ACTOR_LOADER=None)
    if configuration:
        app.config.update(configuration)
    if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'replace-with-a-generated-secret-key':
        raise RuntimeError('Set a generated SECRET_KEY. Run python scripts/setup_env.py.')
    db.init_app(app)
    from entity import models
    with app.app_context():
        if db.engine.dialect.name == 'sqlite':
            @event.listens_for(db.engine, 'connect')
            def foreign_keys(connection, _):
                connection.execute('PRAGMA foreign_keys=ON')
    CSRFProtect(app)

    @app.before_request
    def load_profile_actor():
        loader = app.config.get('PROFILE_ACTOR_LOADER')
        g.profile_actor = loader() if loader else (DevelopmentProfileActor() if app.config['PROFILE_DEVELOPMENT_PREVIEW'] else None)

    @app.context_processor
    def profile_context():
        actor = g.get('profile_actor')
        return dict(permission_labels=PERMISSION_OPTIONS,
            preview_mode=app.config['PROFILE_DEVELOPMENT_PREVIEW'] and not app.config.get('PROFILE_ACTOR_LOADER'),
            can=lambda code: bool(actor and actor.has_permission(code)))

    from boundary.routes import register_routes
    register_routes(app)

    @app.cli.command('upgrade-db')
    def upgrade_db():
        from infrastructure.migrations import upgrade_database
        try:
            upgrade_database()
        except RuntimeError as error:
            raise click.ClickException(str(error)) from error
        click.echo('Profile table ready. Existing data preserved; no account tables created.')
    app.cli.add_command(upgrade_db, 'init-db')

    @app.errorhandler(DomainError)
    def domain_error(error):
        db.session.rollback()
        code = 403 if isinstance(error, AccessError) else 404 if isinstance(error, NotFoundError) else 400
        return render_template('error.html', code=code, message=str(error)), code

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', code=400, message='Reload the page: the form security token is missing or expired.'), 400

    @app.errorhandler(404)
    def missing_page(error):
        return render_template('error.html', code=404, message='Page or profile not found.'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', code=500, message='The operation could not be completed.'), 500

    @app.after_request
    def response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        response.headers['Cache-Control'] = 'no-store'
        return response
    return app


app = create_app()
