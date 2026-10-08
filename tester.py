# ============================================================
# tester.py
# AI ENGINEERING TEAM - EXECUTABLE AI TESTER
# ============================================================

import os
import sys
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from playwright.async_api import async_playwright


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

APP_DIR = Path("generated_app")
INDEX_FILE = APP_DIR / "index.html"

MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]


# ============================================================
# GEMINI
# ============================================================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)


def ask_gemini(prompt):

    for model in MODELS:

        try:

            print(f"🤖 Trying {model}...")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                print(f"✅ {model} responded.")

                return response.text

        except Exception as e:

            print(
                f"⚠️ {model} failed: "
                f"{str(e)[:180]}"
            )

    return ""


# ============================================================
# READ GENERATED APPLICATION
# ============================================================

def read_application():

    files = {}

    for filename in [
        "index.html",
        "style.css",
        "script.js"
    ]:

        path = APP_DIR / filename

        if path.exists():

            try:

                files[filename] = path.read_text(
                    encoding="utf-8"
                )

            except Exception as e:

                files[filename] = (
                    f"ERROR READING FILE: {e}"
                )

    return files


# ============================================================
# EXTRACT JSON FROM GEMINI
# ============================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):

        lines = text.splitlines()

        if lines:

            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):

            lines = lines[:-1]

        text = "\n".join(lines)

    # Find JSON array
    start = text.find("[")

    end = text.rfind("]")

    if start != -1 and end != -1:

        text = text[start:end + 1]

    try:

        return json.loads(text)

    except Exception as e:

        print(
            "⚠️ Could not parse Gemini JSON:"
        )

        print(str(e))

        return None


# ============================================================
# CREATE EXECUTABLE TEST PLAN
# ============================================================

def create_executable_tests(
    planner_output,
    application
):

    html = application.get(
        "index.html",
        ""
    )

    css = application.get(
        "style.css",
        ""
    )

    js = application.get(
        "script.js",
        ""
    )

    prompt = f"""
You are the QA automation architect of an autonomous
AI software engineering team.

Your job is to convert the Planner's test plan into
REAL executable browser tests.

============================================================
PLANNER TEST PLAN
============================================================

{planner_output}

============================================================
GENERATED APPLICATION
============================================================

--- index.html ---

{html}

--- style.css ---

{css}

--- script.js ---

{js}

============================================================
YOUR TASK
============================================================

Analyze the actual generated application.

Create 5 to 7 executable browser tests.

IMPORTANT:

The tests MUST match the actual application.

Do not invent buttons, labels, fields, or text that
do not exist in the generated application.

Use visible text, labels, IDs, placeholders, or
accessible roles that actually exist in the HTML.

Return ONLY valid JSON.

The JSON must have this exact structure:

[
  {{
    "name": "Test name",
    "steps": [
      {{
        "action": "click_text",
        "value": "Exact visible button text"
      }},
      {{
        "action": "wait",
        "value": 1000
      }},
      {{
        "action": "assert_text",
        "value": "Expected visible text"
      }}
    ]
  }}
]

============================================================
SUPPORTED ACTIONS
============================================================

1. click_text

Clicks a visible element containing the exact text.

Example:

{{
  "action": "click_text",
  "value": "Arriving Home"
}}

------------------------------------------------------------

2. click_id

Clicks an element using its HTML ID.

Example:

{{
  "action": "click_id",
  "value": "arriving-home-btn"
}}

------------------------------------------------------------

3. fill_placeholder

Fills an input using its placeholder.

Example:

{{
  "action": "fill_placeholder",
  "value": "100°F"
}}

------------------------------------------------------------

4. fill_id

Fills an input using its ID.

Example:

{{
  "action": "fill_id",
  "value": "temperature-input",
  "text": "100"
}}

------------------------------------------------------------

5. select_text

Selects an option from a visible select element.

Example:

{{
  "action": "select_text",
  "value": "Peak"
}}

------------------------------------------------------------

6. wait

Waits for a specified number of milliseconds.

Example:

{{
  "action": "wait",
  "value": 1000
}}

------------------------------------------------------------

7. assert_text

Checks that the specified text becomes visible.

Example:

{{
  "action": "assert_text",
  "value": "Conflict Detected"
}}

------------------------------------------------------------

8. assert_visible

Checks that an element containing the specified text
is visible.

Example:

{{
  "action": "assert_visible",
  "value": "Security Guardian"
}}

------------------------------------------------------------

9. assert_url_contains

Checks that the current URL contains a string.

Example:

{{
  "action": "assert_url_contains",
  "value": "dashboard"
}}

============================================================
IMPORTANT RULES
============================================================

- Only use elements that actually exist.
- Prefer IDs when they are clearly available.
- Otherwise use exact visible button text.
- Never click hidden elements.
- Never click destructive buttons such as Delete,
  Remove, Reset, Logout, etc.
- Do not use unsupported actions.
- Do not create tests requiring external services.
- Keep each test between 2 and 8 steps.
- Use realistic user workflows.
- Tests must be independent where possible.
- Return ONLY JSON.
"""

    response = ask_gemini(prompt)

    tests = extract_json(response)

    if not tests:

        print(
            "❌ Failed to create executable tests."
        )

        return []

    return tests


# ============================================================
# TEST RESULT MANAGER
# ============================================================

class TestResults:

    def __init__(self):

        self.results = []

    def record(
        self,
        name,
        passed,
        details=""
    ):

        self.results.append({
            "name": name,
            "passed": passed,
            "details": details
        })

        if passed:

            print(
                f"✅ {name}"
            )

        else:

            print(
                f"❌ {name}"
            )

            if details:

                print(
                    f"   └── {details}"
                )

    def all_passed(self):

        if not self.results:

            return False

        return all(
            result["passed"]
            for result in self.results
        )

    def summary(self):

        total = len(self.results)

        passed = sum(
            1
            for result in self.results
            if result["passed"]
        )

        failed = total - passed

        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        print(
            f"Total Tests : {total}"
        )

        print(
            f"Passed      : {passed}"
        )

        print(
            f"Failed      : {failed}"
        )

        print()

        for result in self.results:

            status = (
                "PASS"
                if result["passed"]
                else "FAIL"
            )

            print(
                f"[{status}] "
                f"{result['name']}"
            )

            if result["details"]:

                print(
                    f"       "
                    f"{result['details']}"
                )

        print("=" * 60)

        return failed == 0


# ============================================================
# SAFE TEXT LOCATOR
# ============================================================

async def visible_text_locator(
    page,
    text
):

    locator = page.get_by_text(
        text,
        exact=True
    )

    count = await locator.count()

    for i in range(count):

        candidate = locator.nth(i)

        try:

            if await candidate.is_visible():

                return candidate

        except Exception:

            continue

    # Fallback: text containing the value
    locator = page.get_by_text(
        text,
        exact=False
    )

    count = await locator.count()

    for i in range(count):

        candidate = locator.nth(i)

        try:

            if await candidate.is_visible():

                return candidate

        except Exception:

            continue

    return None


# ============================================================
# EXECUTE ONE TEST STEP
# ============================================================

async def execute_step(
    page,
    step
):

    action = step.get(
        "action",
        ""
    )

    value = step.get(
        "value",
        ""
    )

    # --------------------------------------------------------
    # CLICK TEXT
    # --------------------------------------------------------

    if action == "click_text":

        locator = await visible_text_locator(
            page,
            str(value)
        )

        if locator is None:

            raise Exception(
                f"Visible text not found: {value}"
            )

        await locator.click(
            timeout=5000
        )

        return

    # --------------------------------------------------------
    # CLICK ID
    # --------------------------------------------------------

    elif action == "click_id":

        locator = page.locator(
            f"#{value}"
        )

        if not await locator.count():

            raise Exception(
                f"Element ID not found: {value}"
            )

        locator = locator.first

        if not await locator.is_visible():

            raise Exception(
                f"Element #{value} is hidden."
            )

        await locator.click(
            timeout=5000
        )

        return

    # --------------------------------------------------------
    # FILL PLACEHOLDER
    # --------------------------------------------------------

    elif action == "fill_placeholder":

        locator = page.get_by_placeholder(
            str(value),
            exact=True
        )

        count = await locator.count()

        if count == 0:

            raise Exception(
                f"Placeholder not found: {value}"
            )

        locator = locator.first

        if not await locator.is_visible():

            raise Exception(
                f"Placeholder element is hidden: {value}"
            )

        text = step.get(
            "text",
            "Test input"
        )

        await locator.fill(
            str(text)
        )

        return

    # --------------------------------------------------------
    # FILL ID
    # --------------------------------------------------------

    elif action == "fill_id":

        locator = page.locator(
            f"#{value}"
        )

        if not await locator.count():

            raise Exception(
                f"Input ID not found: {value}"
            )

        locator = locator.first

        if not await locator.is_visible():

            raise Exception(
                f"Input #{value} is hidden."
            )

        text = step.get(
            "text",
            "Test input"
        )

        await locator.fill(
            str(text)
        )

        return

    # --------------------------------------------------------
    # SELECT TEXT
    # --------------------------------------------------------

    elif action == "select_text":

        locator = page.locator(
            "select:visible"
        )

        count = await locator.count()

        if count == 0:

            raise Exception(
                "No visible select element found."
            )

        selected = False

        for i in range(count):

            select = locator.nth(i)

            try:

                await select.select_option(
                    label=str(value)
                )

                selected = True
                break

            except Exception:

                continue

        if not selected:

            raise Exception(
                f"Could not select option: {value}"
            )

        return

    # --------------------------------------------------------
    # WAIT
    # --------------------------------------------------------

    elif action == "wait":

        milliseconds = int(
            value
        )

        await page.wait_for_timeout(
            milliseconds
        )

        return

    # --------------------------------------------------------
    # ASSERT TEXT
    # --------------------------------------------------------

    elif action == "assert_text":

        locator = await visible_text_locator(
            page,
            str(value)
        )

        if locator is None:

            raise Exception(
                f"Expected text not found: {value}"
            )

        return

    # --------------------------------------------------------
    # ASSERT VISIBLE
    # --------------------------------------------------------

    elif action == "assert_visible":

        locator = await visible_text_locator(
            page,
            str(value)
        )

        if locator is None:

            raise Exception(
                f"Expected visible element not found: {value}"
            )

        return

    # --------------------------------------------------------
    # URL CHECK
    # --------------------------------------------------------

    elif action == "assert_url_contains":

        current_url = page.url

        if str(value) not in current_url:

            raise Exception(
                f"Expected URL to contain "
                f"'{value}', got '{current_url}'"
            )

        return

    # --------------------------------------------------------
    # UNKNOWN ACTION
    # --------------------------------------------------------

    else:

        raise Exception(
            f"Unsupported test action: {action}"
        )


# ============================================================
# EXECUTE AI GENERATED TESTS
# ============================================================

async def execute_ai_tests(
    tests,
    page,
    results
):

    print()
    print("=" * 60)
    print("🤖 EXECUTING AI-GENERATED TESTS")
    print("=" * 60)

    for test_index, test in enumerate(
        tests,
        start=1
    ):

        name = test.get(
            "name",
            f"AI Test {test_index}"
        )

        steps = test.get(
            "steps",
            []
        )

        print()
        print(
            f"🧪 TEST {test_index}: {name}"
        )

        print(
            f"   Steps: {len(steps)}"
        )

        test_passed = True
        failure_reason = ""

        try:

            for step_index, step in enumerate(
                steps,
                start=1
            ):

                print(
                    f"   → Step {step_index}: "
                    f"{step.get('action')} "
                    f"{step.get('value', '')}"
                )

                await execute_step(
                    page,
                    step
                )

                # Small pause after actions
                await page.wait_for_timeout(
                    300
                )

            print(
                f"   ✅ Test completed"
            )

        except Exception as e:

            test_passed = False

            failure_reason = str(e)

            print(
                f"   ❌ Test failed: "
                f"{failure_reason}"
            )

        results.record(
            name,
            test_passed,
            failure_reason
        )


# ============================================================
# GENERIC SAFETY TESTS
# ============================================================

async def run_safety_tests(
    page,
    results
):

    print()
    print("=" * 60)
    print("🔍 BASIC APPLICATION SAFETY TESTS")
    print("=" * 60)

    # --------------------------------------------------------
    # Page content
    # --------------------------------------------------------

    try:

        body_text = await page.locator(
            "body"
        ).inner_text()

        results.record(
            "Application has visible content",
            bool(body_text.strip()),
            "Page body contains visible content."
        )

    except Exception as e:

        results.record(
            "Application has visible content",
            False,
            str(e)
        )

    # --------------------------------------------------------
    # Interactive elements
    # --------------------------------------------------------

    try:

        buttons = page.locator(
            "button:visible"
        )

        inputs = page.locator(
            "input:visible, "
            "textarea:visible, "
            "select:visible"
        )

        button_count = await buttons.count()

        input_count = await inputs.count()

        interactive = (
            button_count +
            input_count
        )

        results.record(
            "Interactive UI exists",
            interactive > 0,
            f"{button_count} visible buttons, "
            f"{input_count} visible form fields."
        )

    except Exception as e:

        results.record(
            "Interactive UI exists",
            False,
            str(e)
        )


# ============================================================
# MAIN BROWSER TESTING
# ============================================================

async def run_tests(
    planner_output
):

    results = TestResults()

    # --------------------------------------------------------
    # Check generated app
    # --------------------------------------------------------

    if not INDEX_FILE.exists():

        results.record(
            "Generated application exists",
            False,
            "generated_app/index.html not found."
        )

        return results.all_passed()

    results.record(
        "Generated application exists",
        True,
        "generated_app/index.html found."
    )

    # --------------------------------------------------------
    # Read application
    # --------------------------------------------------------

    application = read_application()

    # --------------------------------------------------------
    # Generate executable tests
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("🧠 AI TEST DESIGNER")
    print("=" * 60)

    tests = create_executable_tests(
        planner_output,
        application
    )

    if not tests:

        results.record(
            "AI executable test generation",
            False,
            "Gemini did not return a valid executable test plan."
        )

        return results.summary()

    print()
    print(
        f"✅ Generated "
        f"{len(tests)} executable tests."
    )

    # --------------------------------------------------------
    # Display tests
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("📋 EXECUTABLE AI TEST PLAN")
    print("=" * 60)

    print(
        json.dumps(
            tests,
            indent=2,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Launch browser
    # --------------------------------------------------------

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        console_errors = []
        page_errors = []

        # ----------------------------------------------------
        # Browser console
        # ----------------------------------------------------

        def handle_console(message):

            if message.type == "error":

                console_errors.append(
                    message.text
                )

        page.on(
            "console",
            handle_console
        )

        # ----------------------------------------------------
        # Page errors
        # ----------------------------------------------------

        def handle_page_error(error):

            page_errors.append(
                str(error)
            )

        page.on(
            "pageerror",
            handle_page_error
        )

        # ----------------------------------------------------
        # Load application
        # ----------------------------------------------------

        print()
        print(
            "=" * 60
        )
        print(
            "🌐 LOADING GENERATED APPLICATION"
        )
        print(
            "=" * 60
        )

        try:

            file_url = (
                INDEX_FILE
                .resolve()
                .as_uri()
            )

            await page.goto(
                file_url,
                wait_until="domcontentloaded"
            )

            results.record(
                "Application loads",
                True,
                "index.html loaded successfully."
            )

        except Exception as e:

            results.record(
                "Application loads",
                False,
                str(e)
            )

            await browser.close()

            return results.summary()

        # ----------------------------------------------------
        # Basic tests
        # ----------------------------------------------------

        await run_safety_tests(
            page,
            results
        )

        # ----------------------------------------------------
        # Execute AI tests
        # ----------------------------------------------------

        await execute_ai_tests(
            tests,
            page,
            results
        )

        # ----------------------------------------------------
        # Check browser errors
        # ----------------------------------------------------

        await page.wait_for_timeout(
            500
        )

        if console_errors:

            results.record(
                "No JavaScript console errors",
                False,
                " | ".join(
                    console_errors[:5]
                )
            )

        elif page_errors:

            results.record(
                "No JavaScript page errors",
                False,
                " | ".join(
                    page_errors[:5]
                )
            )

        else:

            results.record(
                "No JavaScript console errors",
                True,
                "No browser JavaScript errors detected."
            )

        # ----------------------------------------------------
        # Final application check
        # ----------------------------------------------------

        try:

            body_text = await page.locator(
                "body"
            ).inner_text()

            results.record(
                "Application remains usable",
                bool(body_text.strip()),
                "Application remained available after AI tests."
            )

        except Exception as e:

            results.record(
                "Application remains usable",
                False,
                str(e)
            )

        # ----------------------------------------------------
        # Close browser
        # ----------------------------------------------------

        await browser.close()

    return results.summary()


# ============================================================
# MAIN
# ============================================================

async def main():

    print()
    print("=" * 60)
    print("🧪 AI ENGINEERING TEAM — EXECUTABLE TESTER")
    print("=" * 60)

    # --------------------------------------------------------
    # Receive Planner output
    # --------------------------------------------------------

    planner_output = sys.stdin.read()

    if not planner_output.strip():

        print(
            "❌ No Planner output received."
        )

        return 1

    print()
    print(
        "📋 Planner test plan received."
    )

    # --------------------------------------------------------
    # Run tests
    # --------------------------------------------------------

    passed = await run_tests(
        planner_output
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print()

    if passed:

        print("=" * 60)
        print("🎉 TESTING RESULT: PASSED")
        print("=" * 60)

        return 0

    else:

        print("=" * 60)
        print("❌ TESTING RESULT: FAILED")
        print("=" * 60)

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        exit_code = asyncio.run(
            main()
        )

        sys.exit(
            exit_code
        )

    except KeyboardInterrupt:

        print()
        print(
            "⚠️ Testing interrupted."
        )

        sys.exit(1)

    except Exception as e:

        print()
        print("=" * 60)
        print("❌ TESTER AGENT CRASHED")
        print("=" * 60)

        print(
            str(e)
        )

        sys.exit(1)