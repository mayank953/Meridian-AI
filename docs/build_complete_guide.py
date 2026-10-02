"""Joins the numbered learner documents into one file: docs/MERIDIAN_AI_COMPLETE_GUIDE.md

Run from the project root:   python docs/build_complete_guide.py
"""
import glob
import os
import re

folder = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(folder, "[0-9][0-9]-*.md")))

parts = ["# Meridian AI — Complete Learner Guide\n\nAll learner documents in one file. Section numbers match the individual files in the `docs/` folder.\n"]
toc = ["## Contents\n"]
body = []
for path in files:
    text = open(path, encoding="utf-8").read().strip()
    title = text.splitlines()[0].lstrip("# ").strip()
    anchor = re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")
    toc.append(f"- [{title}](#{anchor})")
    # demote headings by one level so each document is a chapter
    text = re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", text, flags=re.M)
    # links between the numbered documents become in-file links
    text = re.sub(r"\]\((\d\d-[a-z0-9-]+)\.md\)", lambda m: "](#chapter-" + m.group(1)[:2] + ")", text)
    body.append(f'<a id="chapter-{os.path.basename(path)[:2]}"></a>\n\n{text}\n')

out = "\n".join(parts) + "\n" + "\n".join(toc) + "\n\n---\n\n" + "\n\n---\n\n".join(body)
dest = os.path.join(folder, "MERIDIAN_AI_COMPLETE_GUIDE.md")
open(dest, "w", encoding="utf-8").write(out)
print(f"wrote {dest} ({len(out):,} characters from {len(files)} documents)")
