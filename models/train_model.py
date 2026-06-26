import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

df = pd.read_csv("data/energy.csv")

X = df[
    [
        "temperature",
        "humidity",
        "production_load"
    ]
]

y = df["consumption"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = XGBRegressor()

model.fit(X_train, y_train)

joblib.dump(
    model,
    "models/ml_model.pkl"
)

print("Model Saved Successfully")