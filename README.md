# 📓 CatchUp AI

**Because borrowing notes shouldn't mean borrowing someone else's learning gaps.**

Built for **Build With Gemma @ Bangladesh** — Multimodal Track.

---

## The Problem

Every day in Bangladesh, thousands of university students miss a lecture. Not because they don't care — but because of Dhaka's traffic, long commutes, monsoon rains, illness, or part-time work.

What happens next is something almost every student has experienced. A message appears in the class group:

> *"Vai, ajker notebook ar board ta ektu den."*

A friend sends a few photos. The student studies them... but never knows what is missing.

**That's where CatchUp AI comes in.**

## What It Does

CatchUp AI is an AI-powered lecture recovery assistant that compares the classroom whiteboard with a student's notes and tells them exactly what they missed, what they copied incorrectly, and what they should study first.

Not another note generator. Not another chatbot.

**It verifies learning instead of generating content.**

Upload two photos — the board, and your (borrowed) notes — and see:

```
📊 Coverage: 68%

🔴 Critical Missing
★★★★★ Boundary Condition

🟡 Correction
Your note:  O(n²)
Board:      O(n log n)

🟢 Verified Notes
Clean lecture notes generated directly from the classroom board.
```

Instead of spending hours comparing notebooks line by line, students know exactly where to focus.

## Why Is This Different?

Today's AI study tools answer: *"What notes can I generate?"*

CatchUp AI answers a different question: **"What did I miss?"**

That single difference changes the entire experience. Rather than producing another summary, CatchUp AI identifies the student's actual learning gaps using the classroom board as the source of truth.

## Why Gemma?

This isn't OCR. This isn't image matching.

Gemma Vision understands the *meaning* of both the whiteboard and the notebook, compares them semantically, identifies missing and incorrect concepts, prioritizes them by importance, and generates a grounded recovery report. Without multimodal reasoning, this comparison simply isn't possible.

## Why Bangladesh?

CatchUp AI wasn't invented around AI. It was invented around a habit that already exists in Bangladesh.

Students already share board photos. Students already borrow notebooks. Students already ask *"What did I miss?"*

We're simply giving them the answer.

---

## How It Works

```
Board photo  ─┐
              ├──▶  Gemma Vision  ──▶  Structured JSON  ──▶  Triaged gap report
Notes photo  ─┘        (semantic comparison)
```

Gemma receives both images in a single call and returns:

- **`coverage_percent`** — how much of the board the notes capture
- **`missing_from_notes`** — content absent from the notes, rated 1–5 on exam-relevance criteria (deadlines/definitions/boundary conditions score highest; asides score lowest)
- **`corrections`** — places where the notes and board conflict
- **`partially_covered`** — related-but-incomplete content, so near-matches aren't mislabelled as full gaps
- **`clean_notes`** — Markdown notes grounded strictly in the board image

## Setup & Run

```bash
git clone <this-repo-url>
cd catchup-ai
pip install streamlit google-genai pillow

cp .env.example .env
# Edit .env and set GEMMA_API_KEY
# optional, defaults to gemma-4-31b-it
# GEMMA_MODEL=gemma-4-31b-it

streamlit run app.py
```

Then open the local URL Streamlit prints, upload a board photo and a notes photo, and click **Generate Gap Report**.

No API key handy? Check **"Use sample output (offline demo)"** to see the full experience with a cached example response.

## Tech Stack

- **Gemma** (vision + reasoning) — core comparison engine
- **Streamlit** — UI
- **Pillow** — image preprocessing

## Limitations & Future Work

- Currently single-student, single-session — no persistence across lectures yet
- Handwriting quality affects extraction accuracy; very messy notes may lower confidence
- **Future direction:** the same comparison run across an entire class's notebooks could produce teacher-facing completeness analytics — e.g. "85% of students missed the boundary condition" — surfacing common misconceptions without adding a second app

---

*Missing a lecture shouldn't mean falling behind for weeks. CatchUp AI transforms two ordinary photos into a personalized recovery plan — helping students recover learning, not just notes.*
