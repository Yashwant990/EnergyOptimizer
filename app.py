from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import db, Prediction, User
import joblib
import plotly
import plotly.graph_objs as go
import json
import pandas as pd
import os
from flask import send_file
from report_generator import generate_report
from datetime import datetime

app = Flask(__name__)

app.secret_key = "energy_optimizer_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///energy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load Prediction Model
model = joblib.load("models/ml_model.pkl")

# Load Anomaly Model
anomaly_model = None

latest_report_data = {
    "prediction": 0,
    "cost": 0,
    "efficiency": 0,
    "anomaly_status": "Normal",
    "recommendation": "No prediction generated yet."
}

if os.path.exists("anomaly/anomaly_model.pkl"):
    anomaly_model = joblib.load(
        "anomaly/anomaly_model.pkl"
    )

with app.app_context():
    db.create_all()

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter_by(
            email=email
        ).first()

        if existing:
            return "Email already exists"

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")    

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid Email or Password"
        )

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def home():

    prediction = None
    cost = None
    recommendation = None
    efficiency = None
    latest_anomaly = None

    anomaly_status = "Normal"

    global latest_report_data

    if request.method == "POST":

        machine_name = request.form[
            "machine_name"
        ]

        temperature = float(
            request.form["temperature"]
        )

        humidity = float(
            request.form["humidity"]
        )

        load = float(
            request.form["load"]
        )

        prediction = model.predict(
            [[temperature, humidity, load]]
        )[0]

        prediction = round(
            float(prediction),
            2
        )

        cost = round(
            prediction * 8,
            2
        )

        efficiency = round(
            max(0, 100 - (prediction / 10)),
            2
        )

        if prediction > 700:

            recommendation = (
                "High energy consumption expected. "
                "Consider shifting heavy operations "
                "to off-peak hours."
            )

        elif prediction > 500:

            recommendation = (
                "Normal industrial load. "
                "Operations are within expected range."
            )

        else:

            recommendation = (
                "Low consumption period. "
                "Energy utilization is efficient."
            )

        anomaly_status = "Normal"

        if anomaly_model is not None:

            anomaly_result = anomaly_model.predict(
                [[prediction]]
            )[0]

            if anomaly_result == -1:

                anomaly_status = (
                    "Anomaly Detected"
                )

                latest_anomaly = (
                    "⚠ Abnormal energy pattern detected."
                )

        record = Prediction(
            machine_name=machine_name,
            temperature=temperature,
            humidity=humidity,
            load=load,
            prediction=prediction,
            cost=cost,
            anomaly_status=anomaly_status
        )

        db.session.add(record)
        db.session.commit()

        latest_report_data = {
            "prediction": prediction,
            "cost": cost,
            "efficiency": efficiency,
            "anomaly_status": anomaly_status,
            "recommendation": recommendation
        }

    history = Prediction.query.order_by(
        Prediction.id.asc()
    ).all()

    machines = {}

    for machine in [
        "Machine A",
        "Machine B",
        "Machine C"
    ]:

        latest = Prediction.query.filter_by(
            machine_name=machine
        ).order_by(
            Prediction.id.desc()
        ).first()

        if latest:

            machines[machine] = {

                "prediction":
                latest.prediction,

                "cost":
                latest.cost,

                "status":
                latest.anomaly_status
            }

    total_predictions = len(history)

    if total_predictions > 0:

        predictions = [
            row.prediction
            for row in history
        ]

        costs = [
            row.cost
            for row in history
        ]

        anomaly_count = len(
            [
                row
                for row in history
                if row.anomaly_status ==
                "Anomaly Detected"
            ]
        )


        avg_consumption = round(
            sum(predictions) / total_predictions,
            2
        )

        max_consumption = round(
            max(predictions),
            2
        )

        min_consumption = round(
            min(predictions),
            2
        )

        total_cost = round(
            sum(costs),
            2
        )

    else:

        avg_consumption = 0
        max_consumption = 0
        min_consumption = 0
        total_cost = 0
        anomaly_count = 0

    x_values = [
        row.id
        for row in history
    ]

    y_values = [
        row.prediction
        for row in history
    ]

   # Energy Trend Chart

    graph = go.Figure()

    graph.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name="Energy Consumption"
        )
    )

    graph.update_layout(
        title="Energy Consumption Trend",
        template="plotly_dark"
    )

    graph_json = json.dumps(
        graph,
        cls=plotly.utils.PlotlyJSONEncoder
    )

    # Cost Trend Chart

    cost_graph = go.Figure()

    cost_graph.add_trace(
        go.Bar(
            x=x_values,
            y=[row.cost for row in history],
            name="Cost"
        )
    )

    cost_graph.update_layout(
        title="Cost Trend",
        template="plotly_dark"
    )

    cost_graph_json = json.dumps(
        cost_graph,
        cls=plotly.utils.PlotlyJSONEncoder
    )

    # Machine Comparison Chart

    machine_names = []
    machine_consumption = []

    for machine, data in machines.items():

        machine_names.append(machine)

        machine_consumption.append(
            data["prediction"]
        )

    machine_graph = go.Figure()

    machine_graph.add_trace(
        go.Bar(
            x=machine_names,
            y=machine_consumption,
            name="Machines"
        )
    )

    machine_graph.update_layout(
        title="Machine Comparison",
        template="plotly_dark"
    )

    machine_graph_json = json.dumps(
        machine_graph,
        cls=plotly.utils.PlotlyJSONEncoder
    )

    return render_template(
        "index.html",
        machines=machines,
        prediction=prediction,
        cost=cost,
        recommendation=recommendation,
        efficiency=efficiency,
        history=history,
        graph_json=graph_json,
        cost_graph_json=cost_graph_json,
        machine_graph_json=machine_graph_json,
        total_predictions=total_predictions,
        avg_consumption=avg_consumption,
        max_consumption=max_consumption,
        min_consumption=min_consumption,
        total_cost=total_cost,
        anomaly_count=anomaly_count,
        latest_anomaly=latest_anomaly
    )


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    tables = None

    if request.method == "POST":

        file = request.files["file"]

        if file:

            df = pd.read_csv(file)

            predictions = model.predict(
                df[
                    [
                        "temperature",
                        "humidity",
                        "production_load"
                    ]
                ]
            )

            df[
                "Predicted_Consumption"
            ] = predictions.round(2)

            df[
                "Estimated_Cost"
            ] = (
                df[
                    "Predicted_Consumption"
                ] * 8
            ).round(2)

            tables = df.to_html(
                classes="table",
                index=False
            )

    return render_template(
        "upload.html",
        tables=tables
    )



@app.route("/generate_report")
@login_required
def generate_pdf_report():

    global latest_report_data

    history = Prediction.query.filter_by(
    user_id=current_user.id
).all()
    

    total_predictions = len(history)
    if total_predictions == 0:
        return "Generate at least one prediction first."

    predictions = [
        row.prediction
        for row in history
    ]

    costs = [
        row.cost
        for row in history
    ]

    anomaly_count = len(
        [
            row
            for row in history
            if row.anomaly_status ==
            "Anomaly Detected"
        ]
    )

    avg_consumption = round(
        sum(predictions) /
        total_predictions,
        2
    )

    max_consumption = round(
        max(predictions),
        2
    )

    min_consumption = round(
        min(predictions),
        2
    )

    total_cost = round(
        sum(costs),
        2
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    filename = (
        f"reports/report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    generate_report(
        filename,
        latest_report_data["prediction"],
        latest_report_data["cost"],
        latest_report_data["efficiency"],
        latest_report_data["anomaly_status"],
        latest_report_data["recommendation"],
        total_predictions,
        avg_consumption,
        max_consumption,
        min_consumption,
        total_cost,
        anomaly_count
    )

    return send_file(
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)