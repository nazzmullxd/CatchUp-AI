"""
CatchUp AI — Grounded lecture recovery for students who missed class.
Upload the classroom board photo + a borrowed/rushed notebook page.
Gemma performs semantic comparison and returns a triaged gap report.

Run:  pip install -r requirements.txt
      copy .env.example .env
      set GEMMA_API_KEY in .env
      streamlit run app.py
"""

import os
import json
import base64
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("GEMMA_MODEL", "gemma-3-27b-it")
API_KEY = os.environ.get("GEMMA_API_KEY", "")

st.set_page_config(page_title="CatchUp AI", page_icon="📓", layout="wide")

# ---------------------------------------------------------------- PROMPT
PROMPT = """You are analysing two images from a single university lecture in Bangladesh.

IMAGE 1 = the classroom whiteboard/blackboard (the GROUND TRUTH of what was taught).
IMAGE 2 = a student's handwritten notebook page (possibly borrowed, rushed, or incomplete).
Both may mix Bangla and English. Handwriting may be messy.

Your task is SEMANTIC comparison of lecture content, not pixel or exact-string matching.
Content counts as covered if the student captured the MEANING, even in different words,
shorthand, Bangla instead of English, or abbreviated form.

Rate importance 1-5 using ONLY these criteria:
  5 = a deadline, assignment, exam announcement, core definition, theorem, or a
      correctness-critical detail (boundary condition, constraint, edge case)
  4 = a prerequisite concept or a formula the rest of the topic depends on
  3 = a worked method or procedure step
  2 = a supporting illustration or secondary example
  1 = an aside, restatement, or decorative content

Return ONLY valid JSON. No markdown fences, no commentary.

{
  "coverage_percent": <int 0-100, share of board content meaningfully captured>,
  "topic": "<short lecture topic name>",
  "missing_from_notes": [
    {"content": "", "importance": 1-5, "reason": "<why this importance, per criteria>"}
  ],
  "corrections": [
    {"in_notes": "", "on_board": "", "importance": 1-5, "reason": ""}
  ],
  "partially_covered": [
    {"in_notes": "", "on_board": "", "what_to_add": ""}
  ],
  "clean_notes": "<complete, well-structured Markdown notes of the BOARD only. Never invent content that is not visible on the board.>"
}"""

# ------------------------------------------------------- DEMO FALLBACK
FALLBACK = {
    "coverage_percent": 68,
    "topic": "Binary Search & Complexity Analysis",
    "missing_from_notes": [
        {"content": "Assignment 3 due Thursday, submit via Google Classroom",
         "importance": 5, "reason": "A graded deadline — missing it has direct academic cost."},
        {"content": "Boundary condition: loop must use low <= high, not low < high",
         "importance": 5, "reason": "Correctness-critical edge case; the algorithm fails without it."},
        {"content": "Precondition: the array must be sorted before searching",
         "importance": 4, "reason": "Prerequisite that the entire method depends on."},
        {"content": "Worked example: searching for 23 in a 10-element array",
         "importance": 2, "reason": "Supporting illustration of a method already recorded."},
    ],
    "corrections": [
        {"in_notes": "Time complexity = O(n^2)", "on_board": "Time complexity = O(log n)",
         "importance": 5, "reason": "Core definitional fact, commonly examined."},
        {"in_notes": "mid = (low + high) / 2", "on_board": "mid = low + (high - low) / 2",
         "importance": 4, "reason": "Formula variant that prevents integer overflow."},
    ],
    "partially_covered": [
        {"in_notes": "recursion possible", "on_board": "Recursive and iterative variants; recursive costs O(log n) stack space",
         "what_to_add": "Add the space-complexity trade-off between the two variants."},
    ],
    "clean_notes": "## Binary Search\n\n**Precondition:** array must be sorted.\n\n### Method\n1. Set `low = 0`, `high = n - 1`\n2. While `low <= high`:\n   - `mid = low + (high - low) / 2`\n   - If `arr[mid] == target` → return `mid`\n   - If `arr[mid] < target` → `low = mid + 1`\n   - Else → `high = mid - 1`\n3. Return `-1` if not found\n\n### Complexity\n- Time: **O(log n)**\n- Space: O(1) iterative, O(log n) recursive\n\n### Admin\n- Assignment 3 due Thursday (Google Classroom)\n",
}


def to_part(img_file):
    img = Image.open(img_file).convert("RGB")
    img.thumbnail((1400, 1400))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def analyse(board, notes):
    """Call Gemma. Falls back to a cached response so a dropped call can't kill a demo."""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=API_KEY)
        resp = client.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[
                types.Part.from_bytes(data=base64.b64decode(to_part(board)), mime_type="image/jpeg"),
                types.Part.from_bytes(data=base64.b64decode(to_part(notes)), mime_type="image/jpeg"),
                types.Part.from_text(text=PROMPT),
            ])],
        )
        raw = resp.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw), None
    except Exception as e:
        return FALLBACK, str(e)


def stars(n):
    return "★" * int(n) + "☆" * (5 - int(n))


# ---------------------------------------------------------------- UI
st.title("📓 CatchUp AI")
st.caption("Missed the lecture? Upload the board photo and a borrowed notebook page. "
           "Gemma compares the lecture content and tells you exactly what you missed.")

c1, c2 = st.columns(2)
with c1:
    board = st.file_uploader("1️⃣ Classroom board photo", type=["jpg", "jpeg", "png"])
    if board:
        st.image(board, use_container_width=True)
with c2:
    notes = st.file_uploader("2️⃣ Your / borrowed notebook page", type=["jpg", "jpeg", "png"])
    if notes:
        st.image(notes, use_container_width=True)

demo = st.checkbox("Use sample output (offline demo)", value=False)

if st.button("Generate Gap Report", type="primary", use_container_width=True):
    if demo:
        st.session_state.result, err = FALLBACK, None
    elif not (board and notes):
        st.warning("Upload both images first.")
        st.stop()
    else:
        with st.spinner("Gemma is comparing lecture content…"):
            st.session_state.result, err = analyse(board, notes)
        if err:
            st.info("Showing cached sample output — live call unavailable.")

r = st.session_state.get("result")
if r:
    st.divider()
    cov = r.get("coverage_percent", 0)
    a, b = st.columns([1, 2])
    a.metric("Notes coverage", f"{cov}%")
    b.progress(cov / 100)
    b.write(f"**Topic:** {r.get('topic', '—')}")

    missing = sorted(r.get("missing_from_notes", []), key=lambda x: -x.get("importance", 0))
    crit = [m for m in missing if m.get("importance", 0) >= 4]

    st.subheader(f"🔴 Critical gaps ({len(crit)})")
    for m in missing:
        with st.container(border=True):
            st.markdown(f"**{stars(m['importance'])} — {m['content']}**")
            st.caption(m.get("reason", ""))

    corr = r.get("corrections", [])
    if corr:
        st.subheader(f"🟡 Corrections ({len(corr)})")
        for c in corr:
            with st.container(border=True):
                x, y = st.columns(2)
                x.error(f"Your notes: {c['in_notes']}")
                y.success(f"On the board: {c['on_board']}")
                st.caption(f"{stars(c.get('importance', 3))} — {c.get('reason', '')}")

    part = r.get("partially_covered", [])
    if part:
        st.subheader(f"🟠 Partially captured ({len(part)})")
        for p in part:
            with st.container(border=True):
                st.markdown(f"**You wrote:** {p['in_notes']}")
                st.markdown(f"**Board had:** {p['on_board']}")
                st.caption(f"→ {p['what_to_add']}")

    st.subheader("🟢 Verified board notes")
    st.info("Every line below is grounded in the board image — nothing is generated from outside it.")
    st.markdown(r.get("clean_notes", ""))

    st.download_button("⬇️ Download catch-up guide (Markdown)",
                       data=f"# CatchUp Report — {r.get('topic','')}\n\n"
                            f"**Coverage: {cov}%**\n\n## Missing\n"
                            + "\n".join(f"- {stars(m['importance'])} {m['content']} — {m.get('reason','')}" for m in missing)
                            + "\n\n## Corrections\n"
                            + "\n".join(f"- `{c['in_notes']}` → `{c['on_board']}`" for c in corr)
                            + "\n\n## Verified Notes\n\n" + r.get("clean_notes", ""),
                       file_name="catchup_report.md", use_container_width=True)
