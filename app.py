"""Stories 1–48: administration, designer/customer portals and platform management."""
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, g, render_template
from sqlalchemy import URL, event
from infrastructure.database import db
from infrastructure.errors import DomainError, NotFoundError
from infrastructure.permissions import PERMISSION_OPTIONS

ROOT = Path(__file__).resolve().parent


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
        SQLALCHEMY_TRACK_MODIFICATIONS=False)
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

    from infrastructure.auth import load_account
    from infrastructure.navigation import navigation
    app.before_request(load_account)

    @app.context_processor
    def profile_context():
        return dict(permission_labels=PERMISSION_OPTIONS, current_user=g.get('current_user'),
            navigation=navigation())

    from boundary.routes import register_routes
    from infrastructure.commands import register_commands
    register_routes(app)
    register_commands(app)

    @app.errorhandler(DomainError)
    def domain_error(error):
        db.session.rollback()
        code = 404 if isinstance(error, NotFoundError) else 400
        return render_template('error.html', code=code, message=str(error)), code

    @app.errorhandler(404)
    def missing_page(error):
        return render_template('error.html', code=404, message='Page or profile not found.'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', code=500, message='The operation could not be completed.'), 500

    return app


app = create_app()
