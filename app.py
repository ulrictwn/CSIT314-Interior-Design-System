import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import URL, inspect

from infrastructure.database import db
from entity.user_profile import UserProfile


load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host="db",
    port=5432,
    database=os.environ["POSTGRES_DB"]
)

db.init_app(app)


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Tables:", inspect(db.engine).get_table_names())