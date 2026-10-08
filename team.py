import subprocess
import sys
import os
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# =========================================================
# TEAM STATE
# =========================================================

class TeamState(TypedDict):
    requirement: str
    plan: str
    coder_output: str
    test_output: str
    test_passed: bool
    repair_output: str
    attempts: int


# =========================================================
# RUN PYTHON SCRIPT SAFELY
# =========================================================

def run_script(script, input_text=""):

    env = os.environ.copy()

    # Fix Windows Unicode output
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, script],
        input=input_text,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    output = result.stdout

    if result.stderr:
        output += "\n" + result.stderr

    return result.returncode, output


# =========================================================
# PLANNER AGENT
# =========================================================

def planner_node(state: TeamState):

    print("\n" + "=" * 60)
    print("PLANNER AGENT")
    print("=" * 60)

    code, output = run_script(
        "planner.py",
        state["requirement"] + "\n"
    )

    print(output)

    return {
        "plan": output
    }


# =========================================================
# CODER AGENT
# =========================================================

def coder_node(state: TeamState):

    print("\n" + "=" * 60)
    print("CODER AGENT")
    print("=" * 60)

    code, output = run_script(
        "coder.py",
        state["plan"] + "\n"
    )

    print(output)

    return {
        "coder_output": output
    }


# =========================================================
# TESTING AGENT
# =========================================================

def tester_node(state: TeamState):

    print("\n" + "=" * 60)
    print("TESTING AGENT")
    print("=" * 60)

    # Pass the Planner's test plan to the Testing Agent
    test_plan = state["plan"]

    code, output = run_script(
        "tester.py",
        test_plan
    )

    print(output)

    passed = code == 0

    if passed:
        print("\nTESTING RESULT: PASSED")
    else:
        print("\nTESTING RESULT: FAILED")

    return {
        "test_output": output,
        "test_passed": passed,
        "attempts": state.get("attempts", 0) + 1
    }

# =========================================================
# DECISION NODE
# =========================================================

def decide_next(state: TeamState):

    if state["test_passed"]:
        print("\nTests passed. Moving to deployment.")
        return "deploy"

    if state["attempts"] >= 3:
        print("\nMaximum repair attempts reached.")
        return "deploy"

    print("\nTests failed. Sending application to Repair Agent.")

    return "repair"


# =========================================================
# REPAIR AGENT
# =========================================================

def repair_node(state: TeamState):

    print("\n" + "=" * 60)
    print("REPAIR AGENT")
    print("=" * 60)

    code, output = run_script("repair.py")

    print(output)

    return {
        "repair_output": output
    }


# =========================================================
# DEPLOYMENT AGENT
# =========================================================

def deploy_node(state: TeamState):

    print("\n" + "=" * 60)
    print("DEPLOYMENT AGENT")
    print("=" * 60)

    if state["test_passed"]:
        print("Application passed all tests.")
        print("Ready for deployment.")
    else:
        print("Application did not fully pass testing.")
        print("Deployment skipped.")

    return {}


# =========================================================
# LANGGRAPH TEAM
# =========================================================

graph = StateGraph(TeamState)

graph.add_node("planner", planner_node)
graph.add_node("coder", coder_node)
graph.add_node("tester", tester_node)
graph.add_node("repair", repair_node)
graph.add_node("deploy", deploy_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "coder")
graph.add_edge("coder", "tester")

graph.add_conditional_edges(
    "tester",
    decide_next,
    {
        "repair": "repair",
        "deploy": "deploy"
    }
)

graph.add_edge("repair", "tester")
graph.add_edge("deploy", END)

team = graph.compile()


# =========================================================
# START TEAM
# =========================================================

if __name__ == "__main__":

    print()
    print("============================================================")
    print("       AUTONOMOUS AI ENGINEERING TEAM")
    print("============================================================")

    requirement = input(
        "\nEnter software requirement:\n> "
    )

    initial_state = {
        "requirement": requirement,
        "plan": "",
        "coder_output": "",
        "test_output": "",
        "test_passed": False,
        "repair_output": "",
        "attempts": 0
    }

    result = team.invoke(initial_state)

    print("\n" + "=" * 60)
    print("ENGINEERING TEAM FINISHED")
    print("=" * 60)

    print(f"Testing attempts: {result['attempts']}")

    if result["test_passed"]:
        print("FINAL STATUS: APPLICATION PASSED TESTING")
    else:
        print("FINAL STATUS: TESTING NOT FULLY PASSED")