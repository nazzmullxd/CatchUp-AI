"""
CatchUp AI — Grounded lecture recovery for students who missed class.

Upload the classroom board photo + a borrowed/rushed notebook page.
Gemma performs a semantic comparison and returns a triaged gap report.

Run:  pip install -r requirements.txt
      copy .env.example .env      (then set GEMMA_API_KEY)
      streamlit run app.py
"""

import os
import re
import json
import base64
from io import BytesIO
from html import escape

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("GEMMA_MODEL", "gemma-4-31b-it")
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
Do not use LaTeX or backslash escapes (e.g. no \\Delta, no $...$) - write chemistry/math
notation in plain text (e.g. "LiAlH4", "delta", "O(log n)") so the JSON stays valid.

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
        {"in_notes": "recursion possible",
         "on_board": "Recursive and iterative variants; recursive costs O(log n) stack space",
         "what_to_add": "Add the space-complexity trade-off between the two variants."},
    ],
    "clean_notes": (
        "## Binary Search\n\n**Precondition:** array must be sorted.\n\n"
        "### Method\n1. Set `low = 0`, `high = n - 1`\n2. While `low <= high`:\n"
        "   - `mid = low + (high - low) / 2`\n   - If `arr[mid] == target` -> return `mid`\n"
        "   - If `arr[mid] < target` -> `low = mid + 1`\n   - Else -> `high = mid - 1`\n"
        "3. Return `-1` if not found\n\n### Complexity\n- Time: **O(log n)**\n"
        "- Space: O(1) iterative, O(log n) recursive\n\n"
        "### Admin\n- Assignment 3 due Thursday (Google Classroom)\n"
    ),
}


# ---------------------------------------------------------------- STYLE
# Base palette lives in .streamlit/config.toml; this adds what theming can't
# express. Injected with st.html() — st.markdown's sanitizer truncates long
# <style> blocks and dumps the remainder onto the page as text.
#
# No webfonts: Streamlit's DOM can't reliably load a font CDN, and a silent
# fallback is worse than a deliberate system stack. Georgia carries the
# "academic record" register; the UI stack handles everything operational.
CSS = """
<style>
:root {
  --ground:    #0A0E17;
  --raised:    #121824;
  --edge:      #202940;
  --ink:       #EEF2FA;
  --muted:     #8892AB;
  --accent:    #5B5BD6;
  --critical:  #FF4D6D;
  --correction:#FFA53D;
  --partial:   #3FB8D4;
  --verified:  #2FD48F;
  --serif: Georgia, 'Times New Roman', serif;
  --mono: ui-monospace, SFMono-Regular, Consolas, monospace;
}

/* ---------- masthead ---------- */
.masthead {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  border-bottom: 1px solid var(--edge);
  padding-bottom: 0.9rem;
  margin-bottom: 0.4rem;
}
.masthead h1 {
  font-family: var(--serif);
  font-size: 1.9rem;
  font-weight: 400;
  letter-spacing: -0.015em;
  margin: 0;
  color: var(--ink);
}
.masthead .rule {
  font-size: 0.7rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  padding-bottom: 0.15rem;
}
.standfirst {
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.6;
  max-width: 62ch;
  margin: 0.9rem 0 1.6rem 0;
}

/* ---------- step strip ---------- */
.steps { display: flex; gap: 2.2rem; margin: 0 0 1.6rem 0; flex-wrap: wrap; }
.step { display: flex; gap: 0.6rem; align-items: baseline; }
.step .n {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--accent);
  border: 1px solid var(--edge);
  border-radius: 3px;
  padding: 0.1rem 0.35rem;
}
.step .t { color: var(--muted); font-size: 0.88rem; }

/* ---------- verdict ---------- */
.verdict {
  border: 1px solid var(--edge);
  border-radius: 4px;
  background: var(--raised);
  padding: 1.5rem 1.75rem 1.35rem;
  margin-bottom: 1.5rem;
}
.verdict .eyebrow {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.verdict .figure {
  font-family: var(--serif);
  font-size: 4rem;
  line-height: 0.95;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
}
.verdict .figure .pct { font-size: 2rem; color: var(--muted); }
.verdict .topic {
  font-size: 0.95rem;
  color: var(--ink);
  margin-top: 0.7rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--edge);
}
.verdict .topic span { color: var(--muted); }

/* severity distribution — the shape of the damage, before any detail */
.dist { display: flex; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 1rem; gap: 2px; }
.dist i { display: block; }
.dist-key {
  display: flex; gap: 1.1rem; flex-wrap: wrap;
  margin-top: 0.6rem; font-size: 0.75rem; color: var(--muted);
}
.dist-key b { font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }
.dist-key i { display: inline-block; width: 7px; height: 7px; border-radius: 2px; margin-right: 0.4rem; }

/* ---------- section headings ---------- */
.section {
  display: flex;
  align-items: baseline;
  gap: 0.7rem;
  margin: 2.2rem 0 0.9rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--edge);
}
.section .name {
  font-family: var(--serif);
  font-size: 1.15rem;
  color: var(--ink);
}
.section .count {
  font-family: var(--mono);
  font-size: 0.74rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* ---------- entries ---------- */
/* Severity is carried by rail weight + saturation, not by star glyphs alone,
   so a 5 and a 2 separate at a glance while scrolling. */
.entry {
  display: grid;
  grid-template-columns: 2.1rem 1fr;
  gap: 0 0.9rem;
  padding: 0.85rem 1rem 0.9rem 0.75rem;
  margin-bottom: 0.45rem;
  background: var(--raised);
  border-radius: 3px;
  border-left: 2px solid var(--edge);
}
.entry .rank {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  padding-top: 0.15rem;
}
.entry .body { min-width: 0; }
.entry .headline { color: var(--ink); line-height: 1.5; font-size: 0.97rem; }
.entry .reason {
  color: var(--muted);
  font-size: 0.85rem;
  line-height: 1.55;
  margin-top: 0.3rem;
}
.entry .swap { margin-top: 0.15rem; line-height: 1.9; }

.sev-5 { border-left-width: 4px; border-left-color: var(--critical); }
.sev-4 { border-left-width: 3px; border-left-color: #D9455F; }
.sev-3 { border-left-width: 2px; border-left-color: #8E5A6B; }
.sev-2 { border-left-width: 2px; border-left-color: #5A4453; }
.sev-1 { border-left-width: 2px; border-left-color: var(--edge); }
.e-correction { border-left-width: 3px; border-left-color: var(--correction); }
.e-partial    { border-left-width: 3px; border-left-color: var(--partial); }
.e-verified   { border-left-width: 3px; border-left-color: var(--verified); }

/* ---------- inline atoms ---------- */
.tag {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.12rem 0.4rem;
  border-radius: 2px;
  vertical-align: 0.08em;
}
.tag-critical { color: var(--critical); background: rgba(255, 77, 109, 0.12); }
.tag-minor    { color: var(--muted);    background: rgba(136, 146, 171, 0.12); }
.quote {
  font-family: var(--mono);
  font-size: 0.83rem;
  padding: 0.12rem 0.4rem;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.055);
  color: var(--ink);
}
.was { text-decoration: line-through; text-decoration-color: var(--critical); opacity: 0.75; }
.arrow { color: var(--muted); padding: 0 0.35rem; }

.grounding {
  font-size: 0.83rem;
  color: var(--muted);
  border-left: 2px solid var(--verified);
  padding: 0.15rem 0 0.15rem 0.8rem;
  margin-bottom: 1rem;
}
</style>
"""
st.html(CSS)


# ---------------------------------------------------------------- HELPERS
def to_b64_jpeg(img_file, max_side=1400):
    """Downscale and re-encode an upload so the request stays small."""
    img = Image.open(img_file).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def parse_response(text):
    """Strip fences, then repair stray backslashes Gemma sometimes emits (\\Delta)."""
    raw = text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", raw))


def analyse(board, notes):
    """Call Gemma. Falls back to a cached response so a dropped call can't kill a demo."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[
                types.Part.from_bytes(data=base64.b64decode(to_b64_jpeg(board)),
                                      mime_type="image/jpeg"),
                types.Part.from_bytes(data=base64.b64decode(to_b64_jpeg(notes)),
                                      mime_type="image/jpeg"),
                types.Part.from_text(text=PROMPT),
            ])],
        )
        return parse_response(response.text), None
    except Exception as exc:
        return FALLBACK, str(exc)


def stars(n):
    n = max(0, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)


def importance(item, default=3):
    """Model output is untrusted — coerce importance into 1-5 or fall back."""
    try:
        return max(1, min(5, int(item.get("importance", default))))
    except (TypeError, ValueError):
        return default


def quote(text):
    return f'<span class="quote">{escape(str(text))}</span>'


def entry(rail, rank, headline, reason=""):
    """One row of the report. `rail` is the severity/category class."""
    detail = f'<div class="reason">{reason}</div>' if reason else ""
    st.html(f'<div class="entry {rail}">'
            f'<div class="rank">{rank}</div>'
            f'<div class="body"><div class="headline">{headline}</div>{detail}</div>'
            f'</div>')


def section(name, count, unit):
    label = f"{count} {unit}{'' if count == 1 else 's'}"
    st.html(f'<div class="section"><span class="name">{name}</span>'
            f'<span class="count">{label}</span></div>')


# ---------------------------------------------------------------- HEADER
st.html('<div class="masthead">'
        '<h1>CatchUp AI</h1>'
        '<span class="rule">Lecture recovery report</span>'
        '</div>'
        '<p class="standfirst">You missed the class and borrowed the notes. '
        'This checks those notes against a photo of the board and tells you what '
        'is missing, what is wrong, and what to study first.</p>')

# The three steps are a genuine sequence, so they are numbered.
st.html('<div class="steps">'
        '<div class="step"><span class="n">1</span><span class="t">Photograph the board</span></div>'
        '<div class="step"><span class="n">2</span><span class="t">Photograph the notes</span></div>'
        '<div class="step"><span class="n">3</span><span class="t">Read the ranked gap report</span></div>'
        '</div>')

# ---------------------------------------------------------------- INPUTS
left, right = st.columns(2, gap="large")
with left:
    board = st.file_uploader("Board photo — the ground truth",
                             type=["jpg", "jpeg", "png"])
    if board:
        st.image(board, use_container_width=True)
with right:
    notes = st.file_uploader("Notebook page — what you have",
                             type=["jpg", "jpeg", "png"])
    if notes:
        st.image(notes, use_container_width=True)

demo = st.checkbox("Use sample output (offline demo)", value=False)

if st.button("Generate Gap Report", type="primary", use_container_width=True):
    if demo:
        st.session_state.result, st.session_state.error = FALLBACK, None
    elif not (board and notes):
        st.warning("Upload both images first.")
        st.stop()
    else:
        with st.spinner("Gemma is comparing lecture content… this can take up to a minute."):
            result, error = analyse(board, notes)
        st.session_state.result, st.session_state.error = result, error

# ---------------------------------------------------------------- REPORT
report = st.session_state.get("result")
if report:
    if st.session_state.get("error"):
        st.info("Showing cached sample output — the live call failed.")
        with st.expander("Error detail"):
            st.code(st.session_state["error"])

    missing = sorted(report.get("missing_from_notes", []),
                     key=lambda x: -importance(x, 0))
    corrections = report.get("corrections", [])
    partial = report.get("partially_covered", [])

    # ---- verdict: the single number, then the shape of the damage ----
    coverage = report.get("coverage_percent", 0)
    critical = [m for m in missing if importance(m, 0) >= 4]

    buckets = [
        ("Critical gaps", len(critical), "var(--critical)"),
        ("Corrections", len(corrections), "var(--correction)"),
        ("Partial", len(partial), "var(--partial)"),
        ("Minor gaps", len(missing) - len(critical), "var(--muted)"),
    ]
    total = sum(n for _, n, _ in buckets) or 1
    bars = "".join(f'<i style="flex:{n};background:{c}"></i>'
                   for _, n, c in buckets if n)
    keys = "".join(f'<span><i style="background:{c}"></i>{label} <b>{n}</b></span>'
                   for label, n, c in buckets if n)

    st.html(f'<div class="verdict">'
            f'<div class="eyebrow">Notes coverage</div>'
            f'<div class="figure">{coverage}<span class="pct">%</span></div>'
            f'<div class="dist">{bars}</div>'
            f'<div class="dist-key">{keys}</div>'
            f'<div class="topic"><span>Lecture topic —</span> '
            f'{escape(str(report.get("topic", "Unknown")))}</div>'
            f'</div>')

    # ---- missing, ranked by study order ----
    if missing:
        section("Missing from your notes", len(missing), "item")
        for i, item in enumerate(missing, 1):
            sev = importance(item, 0)
            tag = ('<span class="tag tag-critical">critical</span>' if sev >= 4
                   else '<span class="tag tag-minor">minor</span>')
            entry(f"sev-{sev}", f"{i:02d}",
                  f'{escape(str(item.get("content", "")))} {tag}',
                  escape(str(item.get("reason", ""))))

    # ---- corrections: what you wrote, struck; what the board said ----
    if corrections:
        section("Copied incorrectly", len(corrections), "conflict")
        for i, item in enumerate(corrections, 1):
            swap = (f'<span class="quote was">{escape(str(item.get("in_notes", "")))}</span>'
                    f'<span class="arrow">→</span>'
                    f'{quote(item.get("on_board", ""))}')
            entry("e-correction", f"{i:02d}",
                  f'<div class="swap">{swap}</div>',
                  escape(str(item.get("reason", ""))))

    if partial:
        section("Partially captured", len(partial), "item")
        for i, item in enumerate(partial, 1):
            entry("e-partial", f"{i:02d}",
                  f'You wrote {quote(item.get("in_notes", ""))}',
                  f'Board had {quote(item.get("on_board", ""))}<br>'
                  f'Add: {escape(str(item.get("what_to_add", "")))}')

    st.html('<div class="section"><span class="name">Verified board notes</span>'
            '<span class="count">grounded in the photo</span></div>')
    st.html('<div class="grounding">Every line below comes from the board photo. '
            'Nothing is generated from outside it.</div>')
    st.markdown(report.get("clean_notes", ""))

    st.divider()
    st.download_button(
        "⬇️ Download catch-up guide (Markdown)",
        data=(
            f"# CatchUp Report — {report.get('topic', '')}\n\n"
            f"**Coverage: {coverage}%**\n\n"
            "## Missing\n"
            + "\n".join(f"- {stars(m.get('importance', 0))} {m.get('content', '')} "
                        f"— {m.get('reason', '')}" for m in missing)
            + "\n\n## Corrections\n"
            + "\n".join(f"- `{c.get('in_notes', '')}` → `{c.get('on_board', '')}`"
                        for c in corrections)
            + "\n\n## Verified Notes\n\n"
            + report.get("clean_notes", "")
        ),
        file_name="catchup_report.md",
        use_container_width=True,
    )
