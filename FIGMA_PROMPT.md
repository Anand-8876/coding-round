Design a complete, high-fidelity web app UI in Figma for **CodeArena**, a CodeChef/LeetCode-style platform for practising Data Structures & Algorithms. Deliver desktop frames (1440×900) for every screen, plus mobile frames (390×844) for the Login, Problems and Problem screens. Use auto layout everywhere and build reusable components with variants.

## Product summary
- Users sign up and solve **100 DSA problems** (40 Easy, 35 Medium, 25 Hard) **in a fixed order**.
- Only problem 1 is open at first. A problem unlocks when the previous one is **solved** or its **solution has been viewed**.
- Users write code in the browser in **Python or JavaScript**:
  - **Run** checks the code against the sample tests.
  - **Submit** checks it against all tests, including hidden ones.
- Correct submission: they see a success screen and go on to the next problem.
- Wrong submission: they can try again or **reveal the reference solution** in their chosen language, together with an explanation.
  - Revealing it marks the problem "solution viewed", which gives half points if they solve it later.
- Points: Easy 10, Medium 20, Hard 40.

## Visual style
- A modern, focused developer tool, in the spirit of LeetCode, Linear and Vercel.
- **Dark mode is primary.** Also create a light-mode version of the Problems and Problem screens.
- Dark palette:
  - background #0F1117, surface #171A23, raised surface #1E2230, border #2A2F3F
  - text #E6E8EF, muted text #9097AD
  - accent indigo #818CF8
- Difficulty colours:
  - Easy: green #34D399
  - Medium: amber #FBBF24
  - Hard: red #F87171
  - Each has a matching dark tinted background for its pill.
- Status colours: success green, error red, warning amber.
- Fonts: Inter for the interface; JetBrains Mono for code, test input/output and keyboard shortcuts.
- 8-pt spacing grid, 10px radius on cards, 8px on buttons and inputs, soft shadows, 1px borders.
- Logo: a small indigo rounded square containing `</>`, followed by the wordmark "CodeArena".

## Components (build as variants)
- **Button:**
  - variants: Primary (indigo), Success (green, used for Submit), Secondary, Ghost, Danger
  - sizes: Small and Medium
  - states: default, hover, disabled, loading (spinner)
- **Difficulty pill:** Easy / Medium / Hard
- **Topic tag:** small grey pill, e.g. "arrays", "dynamic programming", "graphs"
- **Status icon:**
  - Solved: green ✔
  - Solution viewed: amber eye
  - Attempted: amber dot
  - Unlocked: indigo empty circle
  - Locked: padlock
- **Verdict label:**
  - Accepted (green)
  - Wrong Answer, Runtime Error, Time Limit Exceeded, Compilation Error (all red)
- **Test-case chip:** Case 1 / Case 2, with default, active, passed (✔ green outline) and failed (✘ red outline) variants
- **Code block:** monospace text on a darker surface, with a label above it: INPUT, EXPECTED OUTPUT, YOUR OUTPUT or ERROR
- **Progress bar:** a thin bar in indigo, green, amber or red
- **Stat card:** label, large number with a "/ total" suffix, and a progress bar
- **Text input:** label, placeholder and error state
- **Tabs:** underline style for the panes; segmented style for Login/Sign up
- **Modal:** large icon, title, body text and two buttons
- **Toast:** small dark pill at the bottom centre

## Screens

### 1. Login / Sign up
- A centred card on the dark background with the logo and the tagline "100 DSA problems from easy to hard. Solve one to unlock the next."
- A segmented control switches between **Log in** and **Sign up**.
- Log in fields: username or email, password.
- Sign up fields: username, email, password (hint: "At least 6 characters").
- A full-width primary button.
- Show an error state with red helper text, e.g. "Wrong username/email or password".

### 2. Top navigation (on every signed-in screen)
- Logo on the left.
- Nav links: **Problems**, **Submissions**, **Leaderboard**; the active one uses an indigo tinted background.
- On the right: an amber points badge (e.g. "120 pts"), the username and a **Log out** ghost button.

### 3. Problems dashboard
- **Four stat cards in a row:**
  - Overall progress: "12 / 100 solved", a progress bar, and "120 points · 2 solutions viewed" underneath
  - Easy: 10 / 40
  - Medium: 2 / 35
  - Hard: 0 / 25
- **"Up next" banner** (indigo tinted): "#13 Two Sum", an Easy pill, and a **Continue →** button.
  - Also design the variant for when everything is done: "🏆 You've completed all 100 problems!"
- **Filter bar:** a search field ("Search problems or topics…"), a difficulty dropdown and a status dropdown (All / Solved / Not solved / Solution viewed / Locked).
- **Problem table** with columns: status icon, #, Title, Topics (up to 3 tags), Difficulty.
  - Show about 15 rows covering every status.
  - Locked rows are dimmed to 50%.
  - Show the row hover state.
  - Include an empty state: "No problems match your filters."

### 4. Problem workspace (main screen)
A full-height two-pane layout below the nav, split roughly 45 / 55.

**Left pane**
- Tabs: **Description | Submissions | Solution**.
  - The Solution tab only appears after a failed submission. Show one frame without it and one with it.
- **Description tab:**
  - Title "1. Sum of Array", with ‹ › previous/next buttons on the right.
  - A row with the difficulty pill, topic tags, and "Time limit: 2.0 s" aligned right.
  - Sections: statement, **Input Format**, **Output Format**, **Constraints** (bullet list), then **Example 1 / Example 2**. Each example shows INPUT and OUTPUT code blocks side by side.
  - Footer note: "Your code reads from standard input and prints to standard output. Submissions are checked against 11 tests (9 hidden)."
  - Banner variants at the top:
    - green: "✔ You solved this problem. Next problem →"
    - amber: "👁 You viewed the solution. You can still solve it yourself, or move on to the next problem →"
- **Submissions tab:** a table of When / Verdict (coloured) / Lang / Tests (e.g. 6/11) / a "Load code" button.
- **Solution tab:**
  - An amber info banner: "This is a reference solution. Try to understand it, then write it yourself — you can still submit!"
  - An "Approach" section with the explanation text and complexity, e.g. **O(n)**.
  - A code box with tabs **Python 3 | JavaScript (Node.js)** and a **Copy to editor** action.
  - A primary button: **Continue to next problem →**.

**Right pane**
- **Toolbar:**
  - left: language dropdown (Python 3 / JavaScript (Node.js)) and a **Reset** ghost button
  - right: **▶ Run** (secondary) and **Submit** (green)
- **Code editor area:** VS Code / Monaco style, with line numbers, syntax highlighting and a dark theme, showing about 10 lines of sample Python.
- **Bottom console** (about 35% of the height):
  - Tabs: **Sample tests | Result | Custom input**.
  - Keyboard hints on the right: `Ctrl+Enter` run · `Ctrl+Shift+Enter` submit.
- **Console states** (one frame each):
  1. **Sample tests:** Case 1 / Case 2 chips, then INPUT and EXPECTED OUTPUT blocks.
  2. **Running:** a spinner with "Judging against 11 tests…".
  3. **Run result:** "Sample tests passed · 2/2 sample tests · 48 ms", passed case chips, and the input, expected output and your output.
  4. **Submit – Wrong Answer:**
     - Red "✘ Wrong Answer" with "6/11 tests passed".
     - "Failed on test 7 (hidden)."
     - The INPUT and YOUR OUTPUT blocks. For hidden tests the expected output is **not** shown.
     - Buttons: **Try again** (secondary) and **👁 Show solution** (primary).
  5. **Submit – Runtime Error:** as above, plus a red ERROR block containing a Python traceback.
  6. **Submit – Accepted:** green "✔ Accepted · 11/11 tests passed · max 52 ms" and a **Next problem →** button.
  7. **Custom input:** a monospace textarea, a "▶ Run with this input" button, and an output block showing "· 31 ms".

### 5. Modals
- **Show the solution?**
  - Eye icon.
  - Body: "This problem will be marked as 'solution viewed' and you'll earn only half the points if you solve it afterwards. The next problem will be unlocked."
  - Buttons: **Keep trying** (secondary) and **Show solution** (primary).
- **Accepted! 🎉**
  - Body: "All 11 tests passed (max 52 ms). You've solved 13 of 100 problems."
  - Buttons: **Stay here** and **Next problem →**.
- **Reset code?**
  - Body: "Your current Python 3 code will be replaced with the starter template."
  - Buttons: **Cancel** and **Reset** (danger).
- **Locked problem toast:** "🔒 Solve the previous problem to unlock this one".

### 6. Submissions page
- Title "Your recent submissions".
- A table with columns When (e.g. "5 min ago") / Problem (link) / Verdict (coloured) / Language / Tests / Time.
- Include an empty state: "No submissions yet — pick a problem."

### 7. Leaderboard
- A table with columns Rank / User / Solved / Solved without hints.
- The top three ranks get 🥇 🥈 🥉.
- The current user's row is highlighted with an indigo tint.
- Include an empty state.

## Responsive (mobile, 390px)
- The nav collapses: hide the points and username, keep the links.
- Stat cards go into a 2×2 grid.
- The table hides the Topics column.
- On the Problem screen, the panes stack vertically: description first, then the editor and console.
- Sample input/output blocks stack vertically.

## Deliverables
- A **Cover** page.
- A **Design System** page: colour tokens for dark and light, type scale, spacing, and all components with their variants.
- A **Screens** page containing every frame listed above, named clearly (e.g. "Problem / Console / Wrong Answer").
- A clickable **prototype** of this flow:
  Login → Problems → Problem → Submit (Wrong Answer) → Show solution modal → Solution tab → Next problem → Submit (Accepted) → Accepted modal → Next problem.
- Use realistic content throughout: problem titles such as "Two Sum", "Valid Parentheses", "Merge Intervals", "Dijkstra's Shortest Paths", and "Edit Distance", real-looking code, test inputs and verdicts. No lorem ipsum.
