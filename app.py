"""Stories 1–48: administration, designer/customer portals and platform management."""
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, g, render_template
from sqlalchemy import URL, event
# infrastructure/database.py: provides the shared SQLAlchemy database object.
from infrastructure.database import db
# infrastructure/errors.py: defines expected validation, missing-record and access errors.
from infrastructure.errors import DomainError, NotFoundError, AccessDeniedError
# infrastructure/permissions.py: defines display labels and supported permission choices.
from infrastructure.permissions import PERMISSION_OPTIONS

ROOT = Path(__file__).resolve().parent


def create_app(configuration=None):
    """Build Flask, initialize the database and register BCE routes from boundary/routes.py."""
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
    # entity/models.py: registers the model tables in entity/models.py.
    from entity import models
    with app.app_context():
        if db.engine.dialect.name == 'sqlite':
            @event.listens_for(db.engine, 'connect')
            def foreign_keys(connection, _):
                """Enable foreign-key enforcement for each SQLite connection."""
                connection.execute('PRAGMA foreign_keys=ON')

    # infrastructure/auth.py: loads session accounts and checks portal access.
    from infrastructure.auth import load_account, require_portal_access
    # infrastructure/navigation.py: builds sidebar links and selects role dashboards.
    from infrastructure.navigation import navigation
    app.before_request(load_account)
    app.before_request(require_portal_access)

    @app.context_processor
    def profile_context():
        """Make account, permission labels and sidebar links available to HTML templates."""
        return dict(permission_labels=PERMISSION_OPTIONS, current_user=g.get('current_user'),
            navigation=navigation())

    # boundary/routes.py: provides the boundary classes used by these routes.
    from boundary.routes import register_routes
    # infrastructure/commands.py: registers trusted setup and database CLI commands.
    from infrastructure.commands import register_commands
    register_routes(app)
    register_commands(app)

    @app.errorhandler(DomainError)
    def domain_error(error):
        """Roll back a failed operation and display its expected error as HTML or JSON."""
        db.session.rollback()
        code = 403 if isinstance(error, AccessDeniedError) else 404 if isinstance(error, NotFoundError) else 400
        # boundary/designer/presentation.py: chooses designer HTML/JSON responses.
        from boundary.designer.presentation import wants_html
        if not wants_html():
            return dict(ok=False, message=str(error), errors=getattr(error, 'field_errors', {})), code
        return render_template('error.html', code=code, message=str(error)), code

    @app.errorhandler(404)
    def missing_page(error):
        """Display the common page-not-found response."""
        return render_template('error.html', code=404, message='Page or profile not found.'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Roll back an unexpected database operation and display the common error page."""
        db.session.rollback()
        return render_template('error.html', code=500, message='The operation could not be completed.'), 500

    return app


app = create_app()
