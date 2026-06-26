from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


class Prediction(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    machine_name = db.Column(
        db.String(50)
    )

    temperature = db.Column(
        db.Float
    )

    humidity = db.Column(
        db.Float
    )

    load = db.Column(
        db.Float
    )

    prediction = db.Column(
        db.Float
    )

    cost = db.Column(
        db.Float
    )

    anomaly_status = db.Column(
        db.String(20),
        default="Normal"
    )