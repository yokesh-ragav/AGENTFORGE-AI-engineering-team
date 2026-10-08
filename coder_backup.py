import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


# ------------------------------------------------------------
# GEMINI MODEL WITH FALLBACK
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# CODING AGENT
# ------------------------------------------------------------

def coder_agent(plan):

    prompt = f"""
You are the Coding Agent of an autonomous AI Engineering Team.

Your job is to convert the software requirement and development
plan below into a polished, working web application.

DEVELOPMENT PLAN:

{plan}


============================================================
APPLICATION IDENTITY
============================================================

Application name:

PocketTrack

Subtitle:

Smart Expense Tracker for College Students


============================================================
LANGUAGE AND REGION
============================================================

The entire user interface MUST be in English.

This is an Indian college student application.

Use Indian Rupees (₹) everywhere.

NEVER use:

$
USD
dollar
Hindi words
Hindi sentences
Hindi transliteration

Do NOT use words such as:

Chillar
Kharcha
Kharche
Chai

Use normal English words such as:

Expense
Expense Tracker
Tea
Coffee
Food
Transport
Shopping
Education


============================================================
DESIGN
============================================================

Create a clean, modern and professional student-finance UI.

The previous version became too visually crowded.

Keep the design simple.

Use:

- White/light background
- One strong primary accent color
- Rounded cards
- Clean typography
- Good spacing
- Clear hierarchy
- Subtle shadows
- Responsive layout
- Professional dashboard appearance

Do NOT create unnecessary decorative elements.

Do NOT create excessive dashboard cards.


============================================================
HEADER
============================================================

Create a header containing:

PocketTrack

Smart Expense Tracker for College Students

A small badge:

₹ INR


============================================================
SUMMARY
============================================================

Create three compact summary cards:

1. Total Spent

Example:

₹1,240

2. Transactions

Example:

12

3. Top Category

Example:

🍔 Food

₹520


============================================================
ADD EXPENSE
============================================================

Create an Add Expense form.

Fields:

Expense Name
Amount
Category

Example placeholder:

Tea
Coffee
Bus
Petrol
Books
Movie

The amount must display:

₹


============================================================
AUTOMATIC EXPENSE VISUAL
============================================================

When the user enters an expense name, automatically select
a suitable emoji/icon.

Examples:

Tea -> ☕
Coffee -> ☕
Pizza -> 🍕
Burger -> 🍔
Food -> 🍛
Maggi -> 🍜
Bus -> 🚌
Auto -> 🛺
Train -> 🚆
Petrol -> ⛽
Shopping -> 🛍️
Movie -> 🎬
Books -> 📚
College -> 🎓
Medicine -> 💊
Hotel -> 🏨
Travel -> ✈️
Other -> 💰

The emoji should appear inside the expense card.

Do NOT download external images.

The application must work completely offline.


============================================================
EXPENSE HISTORY
============================================================

Create an Expense History section.

Each expense should appear as a clean card.

Example:

☕  Tea

Food · Today

₹20

Include a delete button.

Add a search field:

Search expenses...


============================================================
CATEGORIES
============================================================

Use useful student categories:

Food
Transport
Education
Shopping
Entertainment
Health
Bills
Other


============================================================
SPENDING BREAKDOWN
============================================================

Create a simple Spending by Category section.

Show categories with:

Category name
Emoji
Amount
Percentage

Use simple horizontal bars.

Do not make the chart overly complicated.


============================================================
SMART INSIGHT
============================================================

Create a small section called:

Smart Insight

It should automatically calculate a useful observation
from the user's expenses.

Examples:

"You spent ₹420 on Food, making it your highest category."

or

"You have recorded 5 expenses so far."

The insight must update when expenses change.

Do not pretend that an external AI service is being used
inside the application.

This is a local intelligent feature.


============================================================
FUNCTIONALITY
============================================================

The application MUST actually work.

Users must be able to:

- Add expenses
- Delete expenses
- Search expenses
- Filter by category
- Calculate total spending
- Count transactions
- Calculate top category
- Calculate category percentages
- Generate smart insight
- Automatically select expense emoji


============================================================
TECHNICAL REQUIREMENTS
============================================================

Use ONLY:

HTML
CSS
JavaScript

Do NOT use:

React
Vue
Angular
Bootstrap
Tailwind
external frameworks
external libraries
external APIs

The application must work by simply opening:

index.html

No server should be required.

No backend is required.

Do not use external images.

Do not use external fonts.


============================================================
VERY IMPORTANT OUTPUT RULE
============================================================

Return ONLY the three files.

Do NOT write explanations.

Do NOT use Markdown headings.

Do NOT use ###.

Do NOT use ```.

Do NOT add commentary before or after the files.

Use EXACTLY these markers:

===FILE:index.html===
[HTML CODE]

===FILE:style.css===
[CSS CODE]

===FILE:script.js===
[JAVASCRIPT CODE]

The markers must appear exactly as written.

There must be no other text outside the three files.

Make sure all HTML, CSS and JavaScript is complete and functional.
"""


    return generate_with_fallback(prompt)


# ------------------------------------------------------------
# SAVE GENERATED FILES
# ------------------------------------------------------------

def save_files(response):

    output_dir = Path("generated_app")

    output_dir.mkdir(exist_ok=True)

    files = {
        "index.html": "===FILE:index.html===",
        "style.css": "===FILE:style.css===",
        "script.js": "===FILE:script.js==="
    }

    for filename, marker in files.items():

        start = response.find(marker)

        if start == -1:

            print("Could not find:", filename)

            continue

        start = start + len(marker)

        next_positions = []

        for other_marker in files.values():

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

        # Remove accidental Markdown fences if Gemini ignores
        # the output instruction.
        content = content.replace("```html", "")
        content = content.replace("```css", "")
        content = content.replace("```javascript", "")
        content = content.replace("```js", "")
        content = content.replace("```", "")

        # Remove accidental Markdown headings.
        content = re.sub(
            r"^#+\s*",
            "",
            content,
            flags=re.MULTILINE
        )

        content = content.strip()

        file_path = output_dir / filename

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        print("Created:", file_path)


# ------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------

if __name__ == "__main__":

    plan = """
Build a polished expense tracker for Indian college students.

The application should allow students to record daily
expenses such as Tea, Coffee, Food, Bus, Auto, Petrol,
Shopping, Movies, Books and College expenses.

The application should calculate spending totals and
provide useful visual summaries.

The application must be simple enough to demonstrate
during a hackathon.
"""

    print()
    print("==========================================")
    print("       AI ENGINEERING TEAM")
    print("          CODING AGENT")
    print("==========================================")
    print()

    print("Generating PocketTrack...")
    print()

    result = coder_agent(plan)

    print()
    print("Gemini finished generating the application.")
    print()

    save_files(result)

    print()
    print("==========================================")
    print("       CODING COMPLETE")
    print("==========================================")
    print()

    print("Generated files:")
    print("generated_app/index.html")
    print("generated_app/style.css")
    print("generated_app/script.js")