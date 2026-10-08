from coder import coder_agent, save_files

plan = """
Build a simple expense tracker web application.

Features:
- Add an expense
- Enter expense name
- Enter amount
- Select category
- Delete expenses
- Display total amount spent
- Clean and simple interface

Files required:
- index.html
- style.css
- script.js

Testing:
- Add an expense
- Verify it appears
- Delete an expense
- Verify total updates correctly
"""

print("👨‍💻 Coding Agent is working...\n")

response = coder_agent(plan)

print(response)

save_files(response)

print("\n✅ Coding Agent finished.")