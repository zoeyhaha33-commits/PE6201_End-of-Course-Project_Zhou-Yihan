"""Human-readable explanation helper.

Explanation is intentionally separate from the core classifier and must
not determine or override model risk scores.
"""

def explain_locally(score, triage_label):
    if triage_label == "Needs Manual Review":
        return f"Borderline screening score ({score:.2f}); routed to analyst review instead of force-classification."
    if triage_label == "High Risk":
        return f"Elevated screening score ({score:.2f}); use as a trigger for deeper due diligence, not an investment decision."
    return f"Lower screening score ({score:.2f}); deprioritized for first-pass review but still subject to normal due diligence."
