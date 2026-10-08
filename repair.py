import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


APP_DIR = Path("generated_app")


def generate_with_fallback(prompt):

    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash"
    ]

    for model in models:

        print("Trying model:", model)

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print("Success with:", model)

            return response.text

        except Exception as error:

            print("Model failed:", model)
            print("Reason:", error)
            print()

    raise RuntimeError(
        "All Gemini models are currently unavailable."
    )


def repair_application(test_report):

    html_path = APP_DIR / "index.html"
    css_path = APP_DIR / "style.css"
    js_path = APP_DIR / "script.js"

    html = html_path.read_text(
        encoding="utf-8"
    )

    css = css_path.read_text(
        encoding="utf-8"
    )

    javascript = js_path.read_text(
        encoding="utf-8"
    )

    prompt = f"""
You are the Repair Agent of an autonomous AI Engineering Team.

The Testing Agent tested a web application and found failures.

TEST REPORT:

{test_report}


Your job is to diagnose the failures and repair the application.

CURRENT FILES:

===FILE:index.html===

{html}


===FILE:style.css===

{css}


===FILE:script.js===

{javascript}


IMPORTANT RULES:

1. Fix the problems reported by the Testing Agent.
2. Do not remove working features.
3. Do not redesign the application unnecessarily.
4. Keep the application in English.
5. Keep Indian Rupees (₹).
6. Keep the existing PocketTrack design.
7. Use only HTML, CSS and JavaScript.
8. Return complete replacement versions of all three files.

Return EXACTLY:

===FILE:index.html===

[complete corrected HTML]

===FILE:style.css===

[complete corrected CSS]

===FILE:script.js===

[complete corrected JavaScript]

Do not add explanations.
Do not use Markdown code fences.
Do not add any text outside these three files.
"""

    return generate_with_fallback(prompt)


def save_repaired_files(response):

    markers = {
        "index.html": "===FILE:index.html===",
        "style.css": "===FILE:style.css===",
        "script.js": "===FILE:script.js==="
    }

    for filename, marker in markers.items():

        start = response.find(marker)

        if start == -1:

            print("Could not find:", filename)

            continue

        start += len(marker)

        next_positions = []

        for other_marker in markers.values():

            if other_marker == marker:
                continue

            position = response.find(
                other_marker,
                start
            )

            if position != -1:

                next_positions.append(position)

        if next_positions:

            end = min(next_positions)

        else:

            end = len(response)

        content = response[start:end].strip()

        content = content.replace(
            "```html",
            ""
        )

        content = content.replace(
            "```css",
            ""
        )

        content = content.replace(
            "```javascript",
            ""
        )

        content = content.replace(
            "```js",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        file_path = APP_DIR / filename

        file_path.write_text(
            content.strip(),
            encoding="utf-8"
        )

        print("Repaired:", file_path)


if __name__ == "__main__":

    test_report = """
Testing Agent detected the following failure:

The Add Expense functionality is not working.
When the user enters Tea and ₹20 and clicks Add Expense,
the expense does not appear in Expense History.

The rest of the application appears to load correctly.

Fix the Add Expense functionality without removing
existing features.
"""

    print()
    print("==========================================")
    print("             REPAIR AGENT")
    print("==========================================")
    print()

    print("Analyzing the failure...")
    print()

    repaired_app = repair_application(
        test_report
    )

    print()
    print("Repair Agent generated a fix.")
    print()

    save_repaired_files(
        repaired_app
    )

    print()
    print("==========================================")
    print("             REPAIR COMPLETE")
    print("==========================================")