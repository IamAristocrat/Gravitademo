"""Check public Gravita Pages files for links, media, and sensitive source content."""
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys
root = Path("docs")
files = list(root.rglob("*.html"))
failures = []
assert (root / "index.html").is_file(), "Homepage missing"
assert (root / "assets" / "gravita-logo-official.webp").is_file(), "Official logo missing"
assert not (root / "assets" / "gravita-company-profile.pdf").exists(), "Internal PDF must not be public"
assert not list((root / "assets").glob("profile-*.webp")), "Full profile scans must not be public"
for file in files:
    page = file.read_text(encoding="utf-8")
    if re.search(r"₹|\\b(?:crores?|lakhs?)\\b", page, re.I):
        failures.append(f"{file}: financial value text")
    if "gravita-ground-engineering.aristoverse.chatgpt.site" in page:
        failures.append(f"{file}: stale canonical URL")
    for match in re.finditer(r'''\\b(?:href|src|poster|action)=["']([^"']+)["']''', page):
        url = match.group(1)
        if not url.startswith("/"): continue
        if not url.startswith("/Gravitademo/"):
            failures.append(f"{file}: wrong root path {url}")
            continue
        local = urlsplit(url).path[len("/Gravitademo/"):]
        dest = root / local
        if local.endswith("/"): dest = dest / "index.html"
        if not dest.exists():
            failures.append(f"{file}: missing {url}")
if len(files) < 60: failures.append(f"Expected full 67-page site; only {len(files)} HTML files")
if failures:
    print("\\n".join(failures[:35]), file=sys.stderr)
    sys.exit(1)
print(f"Verified {len(files)} public HTML pages, local links, logo, and excluded internal PDF/profile images.")
