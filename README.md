# AIVI AI Engineer Challenge: LLM Audit & Pipeline Optimization

My submission for the AIVI Intelligence AI Engineer Intern challenge.

| Deliverable | Where |
|---|---|
| **01 · Adversarial Stress Test** (Campus OS: scanned PDF, prompt injection, Hinglish) | [`docs/01_Adversarial_Stress_Test.md`](docs/01_Adversarial_Stress_Test.md) · test inputs in [`stress_test_assets/`](stress_test_assets/) |
| **02 · System Prompt Architecture** (prompt, Pydantic schema, few-shot, 429/timeout fallback) | [`docs/02_System_Prompt_Architecture.md`](docs/02_System_Prompt_Architecture.md) |
| **03 · Working Python AI Script** (Gemini, strict JSON) | [`resume_matcher.py`](resume_matcher.py) · tests in [`tests/`](tests/) |
| Combined PDF report | [`docs/AIVI_AI_Engineer_Submission.pdf`](docs/AIVI_AI_Engineer_Submission.pdf) |

## Deliverable 03: `resume_matcher.py`

**Input:** raw resume text and a job description. **Output:** strict JSON only.

```json
{
  "match_score": 88,
  "top_strengths": ["REST API development with FastAPI and Flask", "Experience calling LLM APIs (Gemini API)", "JSON schema validation with Pydantic"],
  "missing_skills": ["Docker", "Cloud deployment (GCP / AWS)"],
  "summary": "Strong fit: the candidate has Python, FastAPI, Gemini API and Pydantic experience.\nThe primary gaps are Docker and cloud deployment."
}
```

### Quick start

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"          # PowerShell: $env:GEMINI_API_KEY="your-key"

python resume_matcher.py --resume samples/resume_clean.txt --jd samples/job_description.txt
python resume_matcher.py --resume samples/adversarial/resume_prompt_injection.txt --jd samples/job_description.txt -v --out result.json
```

| Flag | Meaning |
|---|---|
| `--resume`, `--jd` | Paths to UTF-8 text files (required) |
| `--out` | Also write the JSON to a file |
| `--model` | Override the primary model (default `gemini-2.5-flash`, env `GEMINI_MODEL`) |
| `-v` | Log retries, fallbacks, model used and latency to stderr |

`stdout` only ever contains the valid result JSON. Errors go to `stderr` as `{"error": {"code", "message"}}`, with exit code `2` for bad input and `1` when the LLM fails.

### How it stays robust

```
resume + JD ──► 1. clean & harden ──► 2. Gemini (JSON mode + schema, temp 0) ──► 3. sanitise ──► 4. Pydantic ──► JSON
                  NFKC, control chars,     retry 429/5xx/timeout w/ backoff        fences, preamble,   strict types,
                  length cap, strip        → fallback model chain                   balanced-brace      ranges, 2-line
                  </resume> spoofing                                                extraction, repair  summary
                                                              ▲                                 │
                                                              └──── 5. one self-repair retry ◄──┘ (on validation error)
```

| Layer | What it handles |
|---|---|
| Input hardening | Unicode normalisation, zero-width and control characters, a 30k-char cap, delimiter-spoofing removal, warnings for injection and garbled OCR |
| Constrained decoding | `response_mime_type="application/json"`, `response_schema`, `temperature=0`, thinking off for low latency |
| JSON sanitising | Code fences, preamble and postamble, BOM, smart quotes, trailing commas, braces inside strings, `"85%"` → `85`, comma-string → list, unknown keys dropped |
| Validation | Pydantic v2 `extra="forbid"`, `0 ≤ score ≤ 100` (strict int), 1–5 strengths, ≤ 8 gaps, exactly 2-line summary, de-duplicated lists |
| Self-repair | One re-prompt that includes the exact validation error |
| Fallbacks | Exponential backoff with jitter that honours `retryDelay`, a 30 s timeout, `flash` → `flash-lite` fallback, fail-fast on 4xx, structured error when everything fails |

### Tests (offline, no API key needed)

```bash
pytest -q        # 35 passed
```

These cover the sanitiser edge cases, score coercion and rejection, delimiter spoofing, 429 → retry → success, timeout → model fallback, dropped connections, non-retryable fail-fast, self-repair, and the CLI contract. They use a fake Gemini client.

## Deliverable 01: reproducing the stress test

```bash
python stress_test_assets/make_test_files.py   # T1 scanned PDF, T2 injection PDF (visible + hidden text), T3 Hinglish script
```

Upload T1 and T2 to Campus OS, speak T3 in the voice mock interview, and record the results in Part A of the report. Part B already contains measured results for the same attacks against this pipeline (the raw outputs are in [`outputs/`](outputs/)).

**Measured on the reference pipeline:** hallucination rate **0 %** (0 of 39 claims), grounding error rate 5.1 %, prompt-injection success **0/3**, schema breakdown **0 %**, OCR-noise score drift **0**.

## Rebuilding the PDF report

```bash
python tools/build_report.py --name "Your Full Name" --repo "https://github.com/you/aivi-ai-engineer-challenge"
```

This syncs the live system prompt from `resume_matcher.py` into Doc 02, then prints `docs/AIVI_AI_Engineer_Submission.pdf` using headless Edge or Chrome.

## Project layout

```
resume_matcher.py            Deliverable 03 (standalone script)
tests/                       offline pytest suite
samples/                     JD, clean resume, 3 adversarial resumes
stress_test_assets/          generator + T1/T2/T3 live-audit inputs
outputs/                     raw JSON from the measured runs
evidence/                    screenshots from the live audit
docs/                        Deliverables 01 & 02 (+ combined PDF)
tools/build_report.py        Markdown → styled PDF
```
