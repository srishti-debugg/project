def predict_fraud(age, bmi, smoker):
    fraud = 0
    reasons = []

    if bmi > 35:
        fraud = 1
        reasons.append("High BMI")

    if smoker == 1:
        fraud = 1
        reasons.append("Smoker risk")

    if age > 60:
        reasons.append("Higher age risk")

    if fraud == 1:
        return "Denied", ", ".join(reasons)
    else:
        return "Accepted", "Low risk profile"