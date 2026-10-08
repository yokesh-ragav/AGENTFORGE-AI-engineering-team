import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)


# =========================================================
# GEMINI FALLBACK
# =========================================================

def generate_with_fallback(prompt):

    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash"
    ]

    last_error = None

    for model in models:

        print(f"\nTrying model: {model}")

        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"Success with: {model}")

            return response.text

        except Exception as e:

            print(f"Model failed: {model}")
            print(f"Reason: {e}")

            last_error = e

    raise RuntimeError(
        f"All Gemini fallback models failed. Last error: {last_error}"
    )


# =========================================================
# PLANNER AGENT
# =========================================================

def planner_agent(requirement):

    prompt = f"""
You are the Planning Agent of an autonomous AI Engineering Team.

Your job is to analyze a software requirement and create a clear
implementation plan for the Coder Agent.

SOFTWARE REQUIREMENT:
{requirement}

Create a practical engineering plan containing:

1. Application overview
2. Main features
3. User interface requirements
4. Data/state requirements
5. Technology approach
6. File structure
7. Implementation steps

8. TEST PLAN

For the TEST PLAN, define 5-10 concrete user behaviors that
an automated browser should verify.

Each test should contain:
- Test name
- User action
- Expected result

The tests must be specific to the requested application.

For example, if the requirement is a quiz application:
- Start quiz
- Select an answer
- Move to next question
- Submit quiz
- Verify score

Do NOT create tests for an application type that was not requested.
Keep the plan clear and actionable.

Do not write the actual source code.
The next Coder Agent will use your plan to build the application.
"""

    return generate_with_fallback(prompt)


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    requirement = input("Enter software requirement: ")

    print("\nPLANNER AGENT\n")

    result = planner_agent(requirement)

    print(result)