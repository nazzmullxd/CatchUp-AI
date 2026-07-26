# CatchUp AI — Project Context for Claude Code

## What this project is

**CatchUp AI** is a submission for the **Build With Gemma @ Bangladesh** hackathon
(Multimodal Track). It's an AI-powered lecture recovery assistant: a student uploads
a photo of the classroom whiteboard and a photo of their (often borrowed) notebook
page, and Gemma Vision performs a **semantic comparison** between the two — not OCR,
not note generation — to produce a triaged gap report showing what's missing, what's
incorrect, and what to study first, ranked by importance.

Core positioning: it **verifies learning instead of generating content**. The board
image is treated as ground truth; nothing in the output is invented outside it.

## Deadline situation

This is a live hackathon with a hard deadline. Time is the scarce resource — prefer
finishing and shipping over polishing. Do not add new features, scope, or model calls
beyond what's described below (e.g. no quiz loops, no teacher dashboards, no multi-user
support — those are explicitly Future Work only, not to be built).

## Repo contents (already created, do not redesign)

- **`app.py`** — the working Streamlit app. Two file uploaders (board photo, notes
  photo) → one Gemma vision call → strict JSON response → rendered gap report UI
  (coverage %, critical missing items sorted by importance with star ratings,
  corrections, partially-covered items, clean grounded notes) → Markdown download.
  Has a built-in `FALLBACK` cached JSON response and a "Use sample output" checkbox
  so a dropped API call can never break a live demo or recording.
- **`catchup_ai_notebook.ipynb`** — the Kaggle notebook deliverable. Same prompt and
  same Gemma call as `app.py`, but narrated in notebook cells (setup → load images →
  show prompt → call Gemma → parse JSON → render report → discussion of how Gemma is
  used → limitations/future work). Currently references placeholder image paths
  `/kaggle/input/catchup-samples/board.jpg` and `.../notes.jpg` — these need real
  sample images once we have them.
- **`README.md`** — the GitHub repo README, already written in full pitch-and-setup
  form. Should stay as the source of truth for the project's framing/copy.
- **`requirements.txt`** — `streamlit`, `google-genai`, `pillow`.

## Environment / secrets

- `GEMMA_API_KEY` — already configured locally as an env var. **Never hardcode it
  into any file. Never commit it.** Check before every commit that no key leaked
  into a cell output, a script, or a config file.
- `GEMMA_MODEL` — optional env var, defaults to `gemma-3-27b-it` in the code.
- Kaggle: already authenticated (Kaggle API/CLI configured locally).
- GitHub: already authenticated via `gh`, and this repo is already cloned locally
  with a remote configured.

## The JSON schema Gemma must return (frozen — do not change)

```json
{
  "coverage_percent": 0,
  "topic": "",
  "missing_from_notes": [
    {"content": "", "importance": 1, "reason": ""}
  ],
  "corrections": [
    {"in_notes": "", "on_board": "", "importance": 1, "reason": ""}
  ],
  "partially_covered": [
    {"in_notes": "", "on_board": "", "what_to_add": ""}
  ],
  "clean_notes": ""
}
```

Importance is rated 1-5 against explicit criteria embedded in the prompt (5 =
deadline/definition/boundary condition, 1 = aside/decoration) — this rubric exists
so the score is explainable, not arbitrary. Don't let this drift.

## What's already done

- [x] `app.py` written and working (needs one real end-to-end test with real photos)
- [x] `catchup_ai_notebook.ipynb` written, validated as well-formed JSON
- [x] `README.md` written
- [x] `requirements.txt` written
- [x] GitHub repo cloned locally, git/gh authenticated
- [x] Kaggle and Gemma API keys configured

## What's left to do (in priority order)

1. **Copy/confirm all four files (`app.py`, `README.md`, `requirements.txt`,
   `catchup_ai_notebook.ipynb`) are in this repo folder**, then `git add`, commit,
   and push. Confirm the GitHub repo visibility is **Public** — this is the
   "Public Project Link" hackathon deliverable.
2. **Get or create two real sample images**: a whiteboard/lecture-board photo and a
   corresponding notebook photo (can be staged/real, doesn't need to be from an
   actual class as long as it's a realistic lecture topic — e.g. binary search,
   like the fallback example already in `app.py`). Save as `board.jpg` and
   `notes.jpg`.
3. **Run `streamlit run app.py` locally with those real images** (uncheck the demo
   checkbox) and confirm the live Gemma API call returns valid parseable JSON.
   This is the highest-risk step — if the model wraps output in markdown fences,
   adds commentary, or the schema doesn't parse, fix the prompt or the parsing in
   `app.py` now, not later.
4. **Upload `catchup_ai_notebook.ipynb` to Kaggle** as a competition notebook.
   Upload `board.jpg`/`notes.jpg` as an attached Kaggle Dataset (or update the
   in-notebook paths to match wherever they're uploaded). Add `GEMMA_API_KEY` via
   Kaggle's Add-ons → Secrets. Run all cells top to bottom to confirm it executes
   cleanly end-to-end, then Save Version as **Public**.
5. **Take 3-4 screenshots** of the working Streamlit app (upload screen, gap report
   with coverage %, a correction example, the clean notes tab) for the Kaggle
   Media Gallery requirement.
6. **Record a 3-5 min demo video** off the working local app: ~40s problem framing,
   ~30s architecture, ~2min live demo, ~20s future work. Upload unlisted to YouTube.
7. **Kaggle Writeup**: create a New Writeup on the competition page covering problem
   statement, solution overview, how Gemma is used, architecture, impact/validation,
   limitations, future work — content should map directly from `README.md`'s pitch
   copy and this file's "how Gemma is used" section in the notebook.
8. **Submit** on Kaggle before the deadline, then keep editing if time remains —
   an early rough submission beats a polished unsubmitted draft.

## Guardrails while working

- Don't refactor `app.py`'s architecture or add new features under time pressure.
- Don't change the JSON schema — the UI, the notebook, and the README all assume it.
- Don't add a database, auth, multi-user support, or a quiz/scoring loop — these are
  explicitly out of scope for the hackathon deadline and are Future Work bullets only.
- If the live Gemma call fails during testing, the priority is fixing prompt/parsing
  robustness (e.g. stripping markdown fences, retry logic) — not building a new
  fallback path, since one already exists in `app.py`.
