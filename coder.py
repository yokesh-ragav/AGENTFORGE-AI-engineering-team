import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

APP_DIR = Path("generated_app")
APP_DIR.mkdir(exist_ok=True)


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
        f"All Gemini models failed. Last error: {last_error}"
    )


# =========================================================
# CLEAN GENERATED CODE
# =========================================================

def clean_code(content):

    content = content.strip()

    # Remove accidental markdown code fences
    content = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    return content.strip()


# =========================================================
# SAVE FILES
# =========================================================

def save_generated_files(response_text):

    files = {}

    patterns = {
        "index.html": r"===FILE:index\.html===\s*(.*?)(?====FILE:style\.css===|===FILE:script\.js===|$)",
        "style.css": r"===FILE:style\.css===\s*(.*?)(?====FILE:script\.js===|$)",
        "script.js": r"===FILE:script\.js===\s*(.*)$"
    }

    for filename, pattern in patterns.items():

        match = re.search(
            pattern,
            response_text,
            re.DOTALL
        )

        if match:
            files[filename] = clean_code(match.group(1))

    for filename in ["index.html", "style.css", "script.js"]:

        if filename not in files:
            raise ValueError(
                f"Coder Agent failed to generate {filename}"
            )

        path = APP_DIR / filename

        path.write_text(
            files[filename],
            encoding="utf-8"
        )

        print(f"Created: {path}")

    return files


# =========================================================
# GENERIC CODER AGENT
# =========================================================

def coder_agent(plan):

    prompt = f"""
You are the Coding Agent inside an autonomous AI Engineering Team.

The Planning Agent has analyzed a user's software requirement and
created the following implementation plan:

================ PLAN ================

{plan}

=======================================

Your task is to BUILD THE APPLICATION described by this plan.

IMPORTANT:

The application is NOT fixed to any particular domain.

It could be:
- expense tracker
- attendance system
- quiz application
- portfolio
- task manager
- calculator
- booking system
- dashboard
- or another suitable web application.

You MUST follow the actual plan instead of assuming a particular
application type.

============================================================
TECHNICAL REQUIREMENTS
============================================================

Build a complete working web application using:

- HTML
- CSS
- JavaScript

Do NOT use React.

Do NOT use external frameworks.

Do NOT use external libraries.

Do NOT require a backend unless the plan explicitly requires one.

Prefer a self-contained browser application that can run locally.

The application should be responsive and visually polished.

============================================================
FUNCTIONAL REQUIREMENTS
============================================================

Implement the features described in the plan.

Every important user interaction should actually work.

Buttons must perform their intended actions.

Forms must validate input.

Data required for the application should be handled appropriately.

If the application can reasonably work with browser LocalStorage,
use LocalStorage for persistence.

The application should provide useful empty states and error handling.

============================================================
TESTABILITY
============================================================

Build the application so that an automated browser testing agent
can interact with it.

Use clear:

- IDs
- buttons
- form fields
- labels
- semantic HTML
- predictable UI elements

Important functionality should be accessible through normal clicks
and typing.

============================================================
VISUAL DESIGN
============================================================

Create a clean, modern and professional interface.

Use:

- responsive layout
- readable typography
- consistent spacing
- cards where appropriate
- clear buttons
- good visual hierarchy
- mobile-friendly design

Avoid unnecessary decoration.

============================================================
OUTPUT FORMAT
============================================================

Generate exactly THREE files.

Return them using these exact markers:

===FILE:index.html===

[complete HTML]

===FILE:style.css===

[complete CSS]

===FILE:script.js===

[complete JavaScript]

Do not use Markdown code fences.

Do not explain the code.

Do not add any text before or after the three files.

The generated files must be complete and immediately runnable.
"""

    print("\nGenerating application from the planning agent's requirements...")

    response = generate_with_fallback(prompt)

    print("\nGemini finished generating the application.")

    files = save_generated_files(response)

    return files


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("       AI ENGINEERING TEAM")
    print("          CODING AGENT")
    print("==========================================")

    plan = input(
        "\nEnter the Planner Agent's plan:\n"
    )

    coder_agent(plan)

    print("\n==========================================")
    print("       CODING COMPLETE")
    print("==========================================")

    print("\nGenerated files:")

    print("generated_app/index.html")
    print("generated_app/style.css")
    print("generated_app/script.js")