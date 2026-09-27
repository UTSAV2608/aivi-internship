"""
Builds the submission PDF from the two Markdown deliverables.

    python tools/build_report.py [--name "Full Name"] [--repo https://github.com/you/repo]

1. Syncs the live SYSTEM_PROMPT from resume_matcher.py into docs/02 (single source of truth).
2. Renders docs/01 + docs/02 into docs/AIVI_AI_Engineer_Submission.html (print-styled).
3. Prints it to docs/AIVI_AI_Engineer_Submission.pdf via headless Edge/Chrome, if found.
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))
from resume_matcher import SYSTEM_PROMPT  # noqa: E402

START, END = "<!-- SYSTEM_PROMPT:start -->", "<!-- SYSTEM_PROMPT:end -->"

CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
:root { --ink:#0f172a; --muted:#64748b; --line:#e2e8f0; --accent:#6d28d9; --accent2:#2563eb; --soft:#f5f3ff; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Inter, Arial, sans-serif; color: var(--ink); font-size: 10.5pt; line-height: 1.5; margin: 0; background:#fff; }
.cover { height: 262mm; display:flex; flex-direction:column; justify-content:center; padding: 0 8mm;
         background: linear-gradient(135deg,#1e1b4b 0%,#4c1d95 55%,#1d4ed8 100%); color:#fff; border-radius: 6px; page-break-after: always; }
.cover .tag { letter-spacing:.2em; font-size:9pt; opacity:.8; text-transform:uppercase; }
.cover h1 { font-size: 30pt; line-height:1.15; margin: 10px 0 8px; border:0; color:#fff; }
.cover .sub { font-size: 13pt; opacity:.9; margin-bottom: 36px; }
.cover table { border-collapse:collapse; width:auto; font-size:10.5pt; background:transparent; }
.cover td { border:0; padding:5px 18px 5px 0; color:#fff; background:transparent !important; }
.cover td:first-child { opacity:.7; }
.cover .chips span { display:inline-block; border:1px solid rgba(255,255,255,.4); border-radius:99px; padding:3px 12px; margin:0 6px 6px 0; font-size:9pt; }
.toc { page-break-after: always; }
.toc li { margin: 6px 0; }
h1 { font-size: 19pt; color: var(--accent); border-bottom: 3px solid var(--accent); padding-bottom: 6px; margin-top: 0; }
section.doc + section.doc h1 { page-break-before: always; }
h2 { font-size: 13.5pt; color: var(--ink); margin: 22px 0 8px; padding-left: 10px; border-left: 4px solid var(--accent2); page-break-after: avoid; }
h3 { font-size: 11.5pt; color: var(--accent); margin: 16px 0 6px; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 14px; font-size: 9pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: var(--accent); color: #fff; text-align: left; padding: 6px 7px; font-weight: 600; }
td { border-bottom: 1px solid var(--line); padding: 5px 7px; vertical-align: top; }
tr:nth-child(even) td { background: #fafafa; }
code { font-family: Consolas, "Cascadia Code", monospace; font-size: 8.6pt; background: #f1f5f9; padding: 1px 4px; border-radius: 3px; }
pre { background: #0f172a; color: #e2e8f0; padding: 11px 13px; border-radius: 6px; font-size: 8pt; line-height: 1.45;
      white-space: pre-wrap; word-break: break-word; page-break-inside: auto; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
blockquote { margin: 10px 0; padding: 9px 13px; background: var(--soft); border-left: 4px solid var(--accent); border-radius: 0 6px 6px 0; }
blockquote p { margin: 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 18px 0; }
.fill { background: #fef9c3; color: #854d0e; border-radius: 3px; padding: 0 3px; font-weight: 600; }
strong { color: #1e1b4b; }
"""


def sync_prompt() -> Path:
    path = DOCS / "02_System_Prompt_Architecture.md"
    text = path.read_text(encoding="utf-8")
    block = f"{START}\n```text\n{SYSTEM_PROMPT.rstrip()}\n```\n{END}"
    if "<!-- SYSTEM_PROMPT -->" in text:
        text = text.replace("<!-- SYSTEM_PROMPT -->", block)
    else:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    path.write_text(text, encoding="utf-8")
    return path


def render(md_text: str) -> str:
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    return re.sub(r"⟨([^⟩]*)⟩", lambda m: f'<span class="fill">⟨{m.group(1)}⟩</span>', body)


def find_browser() -> str | None:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("msedge")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="⟨Your Full Name⟩")
    ap.add_argument("--repo", default="⟨GitHub repo URL⟩")
    args = ap.parse_args()

    sync_prompt()
    docs = [DOCS / "01_Adversarial_Stress_Test.md", DOCS / "02_System_Prompt_Architecture.md"]
    sections = "\n".join(f'<section class="doc">{render(p.read_text(encoding="utf-8"))}</section>' for p in docs)

    cover = f"""
<div class="cover">
  <div class="tag">AIVI Intelligence · AI Engineer Intern Challenge</div>
  <h1>LLM Audit &amp;<br>Pipeline Optimization</h1>
  <div class="sub">Adversarial stress test · System prompt architecture · Gemini resume matcher</div>
  <table>
    <tr><td>Candidate</td><td>{render(html.escape(args.name))[3:-4]}</td></tr>
    <tr><td>Submitted</td><td>{date.today():%d %B %Y}</td></tr>
    <tr><td>Code (Deliverable 03)</td><td>{render(html.escape(args.repo))[3:-4]}</td></tr>
    <tr><td>Targets</td><td>AIVI Campus OS · Hack My Website</td></tr>
  </table>
  <div class="chips" style="margin-top:28px">
    <span>0% hallucination (39 claims)</span><span>0/3 injection success</span>
    <span>0% schema breakdown</span><span>35 offline tests</span>
  </div>
</div>
<div class="toc">
  <h1>Contents</h1>
  <ol>
    <li><strong>Deliverable 01: Adversarial Stress Test</strong>: method, live Campus OS audit (T1 scanned PDF, T2 prompt injection, T3 Hinglish), measured reference-pipeline results, Hack My Website observations, root causes.</li>
    <li><strong>Deliverable 02: System Prompt Architecture</strong>: production prompt, three-layer schema enforcement, few-shot edge cases, 429 / timeout fallback strategy.</li>
    <li><strong>Deliverable 03: Working Python Script</strong>: <code>resume_matcher.py</code> in the linked repository (README has setup, usage and test instructions).</li>
  </ol>
</div>"""

    out_html = DOCS / "AIVI_AI_Engineer_Submission.html"
    out_html.write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AIVI AI Engineer Submission</title>'
        f"<style>{CSS}</style></head><body>{cover}{sections}</body></html>",
        encoding="utf-8",
    )
    print("wrote", out_html.relative_to(ROOT))

    browser = find_browser()
    if not browser:
        print("No Edge/Chrome found - open the HTML and use Print -> Save as PDF.")
        return
    out_pdf = DOCS / "AIVI_AI_Engineer_Submission.pdf"
    out_pdf.unlink(missing_ok=True)
    profile = Path(tempfile.gettempdir()) / "aivi_pdf_profile"  # isolated from any open browser
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={profile}", f"--print-to-pdf={out_pdf}", out_html.as_uri()],
                   check=False, capture_output=True, timeout=120)
    for _ in range(60):  # the launcher can return before the print job finishes
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            break
        time.sleep(1)
    print("wrote", out_pdf.relative_to(ROOT) if out_pdf.exists() else "PDF FAILED")


if __name__ == "__main__":
    main()
