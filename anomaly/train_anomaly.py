import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database import Prediction, db
from flask import Flask
from sklearn.ensemble import IsolationForest
import joblib

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///energy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():

    records = Prediction.query.all()

    print("Records Found:", len(records))

    if len(records) < 10:
        print(
            "Need at least 10 predictions before training anomaly model."
        )
        exit()

    values = [
        [row.prediction]
        for row in records
    ]

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    model.fit(values)

    joblib.dump(
        model,
        "anomaly/anomaly_model.pkl"
    )

    print(
        "Anomaly Model Trained Successfully"
    )