import math
from typing import Dict, List, Tuple
from app.assessment.models import Question, Response

# Constants for IRT update
LEARNING_RATE = 0.5  # Max change in theta per question


def calculate_probability(theta: float, a: float, b: float, c: float) -> float:
    """
    Calculate the probability of a correct response using the 3-Parameter Logistic (3PL) IRT model.
    P(correct|theta) = c + (1-c) / (1 + exp(-a*(theta - b)))
    """
    try:
        exp_term = math.exp(-a * (theta - b))
        return c + (1 - c) / (1 + exp_term)
    except OverflowError:
        return c if (theta - b) < 0 else 1.0


def update_theta(theta: float, correct: bool, a: float, b: float, c: float) -> float:
    """
    Update theta (skill level) based on a single response using a simplified gradient ascent.
    """
    p_correct = calculate_probability(theta, a, b, c)
    
    # Simplified likelihood derivative for theta update
    # If correct: theta increases. If incorrect: theta decreases.
    # The change is proportional to how surprising the result was.
    actual = 1.0 if correct else 0.0
    error = actual - p_correct
    
    # Delta theta
    delta = LEARNING_RATE * error * a
    
    # Constrain theta to typical range [-4, 4]
    new_theta = max(-4.0, min(4.0, theta + delta))
    return new_theta


def get_domain_weights(category: str) -> Dict[str, float]:
    """
    Return domain sampling weights based on the user's category.
    """
    cat = (category or "General").lower()
    
    if "science" in cat:
        return {"Math": 0.3, "Logic": 0.25, "Science": 0.25, "Verbal": 0.1, "General": 0.1}
    elif "art" in cat:
        return {"Verbal": 0.3, "Logic": 0.25, "General": 0.25, "Math": 0.1, "Science": 0.1}
    elif "business" in cat:
        return {"Math": 0.2, "Logic": 0.2, "Verbal": 0.2, "General": 0.3, "Science": 0.1}
    elif "technical" in cat:
        return {"Math": 0.3, "Logic": 0.3, "Science": 0.2, "Verbal": 0.1, "General": 0.1}
    elif "visual" in cat:
        return {"Logic": 0.3, "General": 0.3, "Verbal": 0.2, "Math": 0.1, "Science": 0.1}
    else:
        # Balanced default
        return {"Math": 0.2, "Logic": 0.2, "Science": 0.2, "Verbal": 0.2, "General": 0.2}


def get_initial_prior(category: str, domain: str) -> float:
    """
    Sets initial difficulty prior (theta) based on the user's category.
    Instead of starting at 0.0 for everyone, students start with a slight
    advantage in their major domains.
    """
    cat = (category or "General").lower()
    
    if "science" in cat:
        priors = {"Math": 0.5, "Logic": 0.3, "Science": 0.5, "Verbal": -0.2, "General": 0.0}
    elif "art" in cat:
        priors = {"Verbal": 0.5, "Logic": 0.2, "General": 0.3, "Math": -0.3, "Science": -0.3}
    elif "business" in cat:
        priors = {"Math": 0.2, "Logic": 0.3, "Verbal": 0.3, "General": 0.4, "Science": -0.2}
    elif "technical" in cat:
        priors = {"Math": 0.4, "Logic": 0.4, "Science": 0.3, "Verbal": -0.3, "General": -0.1}
    elif "visual" in cat:
        priors = {"Logic": 0.4, "General": 0.4, "Verbal": 0.2, "Math": -0.2, "Science": -0.2}
    else:
        priors = {"Math": 0.0, "Logic": 0.0, "Science": 0.0, "Verbal": 0.0, "General": 0.0}
        
    return priors.get(domain, 0.0)


def analyze_behavior(responses: List[Response]) -> Dict[str, float]:
    """
    Extract behavioral traits from a sequence of responses.
    """
    if not responses:
        return {"Persistence": 0.0, "Processing Speed": 0.0, "Carefulness": 0.0}

    total_time = sum(r.time_taken_seconds for r in responses)
    avg_time = total_time / len(responses)
    
    correct_count = sum(1 for r in responses if r.correct)
    accuracy = correct_count / len(responses)

    # Persistence: high average time and high total attempts implies persistence
    persistence = min(1.0, avg_time / 60.0)  # cap at 60s avg for normalization
    
    # Processing Speed: inverse of time taken, but penalized if wrong
    # (Fast and wrong = low carefulness, fast and right = high speed)
    speed = min(1.0, 30.0 / max(1.0, avg_time)) if accuracy > 0.5 else 0.0
    
    # Carefulness: High accuracy combined with moderate/high time, few hints
    carefulness = accuracy * min(1.0, avg_time / 20.0)

    return {
        "Persistence": persistence,
        "Processing Speed": speed,
        "Carefulness": carefulness
    }
