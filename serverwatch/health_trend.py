def get_health_trend(current_score, previous_score):
    if not 0 <= current_score <= 100 or not 0 <= previous_score <= 100:
        raise ValueError("score must be between 0 and 100")
    delta = current_score - previous_score
    if delta > 0:
        direction = "improving"
    elif delta < 0:
        direction = "degrading"
    else:
        direction = "stable"
    return {"current": current_score, "previous": previous_score, "delta": delta, "direction": direction}
