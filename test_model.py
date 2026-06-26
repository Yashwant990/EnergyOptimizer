import joblib

model = joblib.load("models/ml_model.pkl")

prediction = model.predict(
    [[30, 60, 80]]
)

print(prediction)