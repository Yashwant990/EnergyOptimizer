from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from datetime import datetime


def generate_report(
    filename,
    prediction,
    cost,
    efficiency,
    anomaly_status,
    recommendation,
    total_predictions,
    avg_consumption,
    max_consumption,
    min_consumption,
    total_cost,
    anomaly_count
):

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    # Cover Page

    content.append(
        Paragraph(
            "Industrial Energy Forecasting Platform",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            "AI-Powered Energy Analytics Report",
            styles["Heading2"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            f"Generated On: {datetime.now()}",
            styles["Normal"]
        )
    )

    content.append(
        PageBreak()
    )

    # Prediction Summary

    content.append(
        Paragraph(
            "Prediction Summary",
            styles["Heading1"]
        )
    )

    content.append(
        Paragraph(
            f"Current Prediction: {prediction} kWh",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Estimated Cost: ₹{cost}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Efficiency Score: {efficiency}%",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Anomaly Status: {anomaly_status}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # Recommendation

    content.append(
        Paragraph(
            "Recommendation",
            styles["Heading1"]
        )
    )

    content.append(
        Paragraph(
            recommendation,
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # Analytics

    content.append(
        Paragraph(
            "Analytics Summary",
            styles["Heading1"]
        )
    )

    content.append(
        Paragraph(
            f"Total Predictions: {total_predictions}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Average Consumption: {avg_consumption} kWh",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Maximum Consumption: {max_consumption} kWh",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Minimum Consumption: {min_consumption} kWh",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Total Cost: ₹{total_cost}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Total Anomalies: {anomaly_count}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # Assessment

    content.append(
        Paragraph(
            "Operational Assessment",
            styles["Heading1"]
        )
    )

    if anomaly_count > 0:

        assessment = (
            "Plant requires attention due to detected anomalies."
        )

    else:

        assessment = (
            "Plant operating within normal parameters."
        )

    content.append(
        Paragraph(
            assessment,
            styles["Normal"]
        )
    )

    pdf.build(content)