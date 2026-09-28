"""Car recommendation agent built with Google ADK, using a Groq-hosted LLM via LiteLLM.

Run from the AIfundamentals/ folder:
    adk run simpleaget      (CLI)
    adk web                 (web UI, then pick "simpleaget")
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(Path(__file__).parent / ".env")

MODEL = os.getenv("GROQ_MODEL", "groq/openai/gpt-oss-120b")

# Ex-showroom prices in INR (approximate).
CARS = [
    {"model": "Maruti Suzuki Alto K10", "body": "hatchback", "fuel": "petrol", "price": 400000, "mileage_kmpl": 24.4, "seats": 5},
    {"model": "Renault Kwid", "body": "hatchback", "fuel": "petrol", "price": 470000, "mileage_kmpl": 21.7, "seats": 5},
    {"model": "Maruti Suzuki Wagon R", "body": "hatchback", "fuel": "petrol", "price": 555000, "mileage_kmpl": 24.4, "seats": 5},
    {"model": "Tata Tiago", "body": "hatchback", "fuel": "petrol", "price": 565000, "mileage_kmpl": 20.1, "seats": 5},
    {"model": "Maruti Suzuki Swift", "body": "hatchback", "fuel": "petrol", "price": 650000, "mileage_kmpl": 24.8, "seats": 5},
    {"model": "Tata Punch", "body": "suv", "fuel": "petrol", "price": 610000, "mileage_kmpl": 20.1, "seats": 5},
    {"model": "Hyundai i20", "body": "hatchback", "fuel": "petrol", "price": 705000, "mileage_kmpl": 20.0, "seats": 5},
    {"model": "Maruti Suzuki Dzire", "body": "sedan", "fuel": "petrol", "price": 680000, "mileage_kmpl": 24.8, "seats": 5},
    {"model": "Honda Amaze", "body": "sedan", "fuel": "petrol", "price": 800000, "mileage_kmpl": 18.6, "seats": 5},
    {"model": "Tata Nexon", "body": "suv", "fuel": "petrol", "price": 800000, "mileage_kmpl": 17.4, "seats": 5},
    {"model": "Maruti Suzuki Brezza", "body": "suv", "fuel": "petrol", "price": 850000, "mileage_kmpl": 19.8, "seats": 5},
    {"model": "Maruti Suzuki Ertiga", "body": "muv", "fuel": "cng", "price": 1070000, "mileage_kmpl": 26.1, "seats": 7},
    {"model": "Tata Tiago EV", "body": "hatchback", "fuel": "electric", "price": 800000, "mileage_kmpl": 0, "seats": 5},
    {"model": "Tata Nexon EV", "body": "suv", "fuel": "electric", "price": 1250000, "mileage_kmpl": 0, "seats": 5},
    {"model": "Hyundai Creta", "body": "suv", "fuel": "diesel", "price": 1300000, "mileage_kmpl": 21.8, "seats": 5},
    {"model": "Kia Seltos", "body": "suv", "fuel": "petrol", "price": 1100000, "mileage_kmpl": 17.0, "seats": 5},
    {"model": "Honda City", "body": "sedan", "fuel": "petrol", "price": 1200000, "mileage_kmpl": 18.4, "seats": 5},
    {"model": "Mahindra XUV700", "body": "suv", "fuel": "diesel", "price": 1400000, "mileage_kmpl": 16.0, "seats": 7},
    {"model": "Toyota Innova Hycross", "body": "muv", "fuel": "hybrid", "price": 1900000, "mileage_kmpl": 23.2, "seats": 7},
    {"model": "Toyota Fortuner", "body": "suv", "fuel": "diesel", "price": 3350000, "mileage_kmpl": 10.0, "seats": 7},
]


def search_cars(max_budget: int, min_budget: int = 0, body_type: str = "any", fuel_type: str = "any", min_seats: int = 0) -> dict:
    """Search car models that fit the user's budget and preferences.

    Args:
        max_budget: Maximum price the user can pay, in INR (e.g. 800000 for 8 lakh).
        min_budget: Minimum price in INR. Defaults to 0.
        body_type: One of "hatchback", "sedan", "suv", "muv", or "any".
        fuel_type: One of "petrol", "diesel", "cng", "electric", "hybrid", or "any".
        min_seats: Minimum number of seats required. Defaults to 0.

    Returns:
        A dict with the matching cars sorted by price (highest within budget first).
    """
    body, fuel = body_type.lower(), fuel_type.lower()
    matches = [
        c for c in CARS
        if min_budget <= c["price"] <= max_budget
        and (body == "any" or c["body"] == body)
        and (fuel == "any" or c["fuel"] == fuel)
        and c["seats"] >= min_seats
    ]
    matches.sort(key=lambda c: c["price"], reverse=True)
    return {"status": "success", "count": len(matches), "cars": matches}


def get_car_details(model: str) -> dict:
    """Get details for a specific car model by (partial) name.

    Args:
        model: Car model name, e.g. "Nexon" or "Honda City".

    Returns:
        A dict with the matching car(s) or an error message.
    """
    found = [c for c in CARS if model.lower() in c["model"].lower()]
    if not found:
        return {"status": "error", "message": f"No car found matching '{model}'."}
    return {"status": "success", "cars": found}


root_agent = LlmAgent(
    name="car_advisor",
    # Groq rejects 'reasoning_content' when ADK replays history, so don't return it.
    model=LiteLlm(model=MODEL, extra_body={"include_reasoning": False}),
    description="Suggests car models based on the user's budget and preferences.",
    instruction=(
        "You are a friendly car buying advisor. "
        "1. Ask for the user's budget if not given (convert lakh to INR: 1 lakh = 100000). "
        "2. Optionally ask about body type, fuel type, and seats needed. "
        "3. Call `search_cars` to find matching models; use `get_car_details` for specific models. "
        "4. Recommend the top 3 options with price, fuel, mileage, seats, and a one-line reason for each. "
        "If nothing matches, suggest relaxing filters or a slightly higher budget. "
        "Only recommend cars returned by the tools; never invent prices."
    ),
    tools=[search_cars, get_car_details],
)
