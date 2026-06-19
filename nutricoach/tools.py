# tools.py — STEP C: the two tools the agent can call
#
#   calculate_nutrition_needs()  -> INTERNAL tool (pure Python math, no internet)
#   food_lookup()                -> EXTERNAL tool (calls the USDA web API)
#
# A "tool" here is just a function that takes inputs and returns a dict.
# Returning a dict (not a printed string) matters: later, agent.py hands this
# structured data to the LLM to phrase a friendly answer.

import os
import requests
from dotenv import load_dotenv

load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")


# ---------- INTERNAL TOOL ----------
def calculate_nutrition_needs(weight_kg, height_cm, age, sex="male", activity="moderate"):
    """BMI + estimated daily calories using the Mifflin-St Jeor equation.

    This is the kind of question RAG CANNOT answer: it's arithmetic on the
    user's own numbers, not a fact found in a document.
    """
    # --- BMI: weight relative to height ---
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    # --- BMR: calories your body burns at complete rest (Mifflin-St Jeor) ---
    if sex.lower().startswith("m"):
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # --- TDEE: BMR scaled by how active you are = daily calories to maintain ---
    factors = {"sedentary": 1.2, "light": 1.375,
               "moderate": 1.55, "active": 1.725, "very_active": 1.9}
    tdee = round(bmr * factors.get(activity, 1.55))

    # --- Interpret the BMI number into a category ---
    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal weight"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obese"

    return {
        "bmi": bmi,
        "bmi_category": category,
        "maintenance_calories": tdee,
        "note": "Estimate using the Mifflin-St Jeor equation.",
    }


# ---------- EXTERNAL TOOL ----------
def food_lookup(food_name):
    """Look up nutrition facts for a food from the USDA FoodData Central API.

    This is the kind of question RAG can't reliably answer either: a precise,
    up-to-date fact ("protein in 100g of X") that lives in an external database.
    """
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": food_name, "pageSize": 1, "api_key": USDA_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()  # turn HTTP errors (401, 500...) into exceptions
        data = r.json()

        if not data.get("foods"):
            return {"error": f"No data found for '{food_name}'."}

        food = data["foods"][0]
        # We only care about the four headline macros:
        wanted = {"Energy", "Protein", "Total lipid (fat)",
                  "Carbohydrate, by difference"}
        nutrients = {}
        for n in food.get("foodNutrients", []):
            if n.get("nutrientName") in wanted:
                nutrients[n["nutrientName"]] = f'{n.get("value")} {n.get("unitName", "").lower()}'

        return {"food": food.get("description", food_name),
                "per_100g": nutrients}

    # Error handling is itself a requirement of the agent guide: an external API
    # can fail (no internet, bad key, rate limit) and the agent must cope.
    except Exception as e:
        return {"error": f"API request failed: {e}"}


if __name__ == "__main__":
    print("--- INTERNAL TOOL: calculate_nutrition_needs ---")
    print(calculate_nutrition_needs(75, 178, 22, "male", "moderate"))

    print("\n--- EXTERNAL TOOL: food_lookup ---")
    print(food_lookup("chicken breast"))
