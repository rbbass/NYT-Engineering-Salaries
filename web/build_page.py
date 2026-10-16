"""Build the shareable web page (web/salary-dots.html) from Data/NYT_EE.xlsx.

Each sheet in the workbook becomes one discipline in the page's dropdown. The data is
embedded in the page, so re-run this after changing the workbook, then republish
salary-dots.html.

Usage: python web/build_page.py [data.xlsx] [template.html] [output.html]
"""
import json
import sys
from pathlib import Path

import pandas as pd

WEB = Path(__file__).parent
DEFAULTS = [WEB.parent / "Data" / "NYT_EE.xlsx", WEB / "template.html", WEB / "salary-dots.html"]

# Typos in the workbook's sheet names, corrected for the dropdown label
LABEL_FIXES = {"Mechancial": "Mechanical"}

data_path, template_path, out_path = [Path(a) for a in sys.argv[1:4]] + DEFAULTS[len(sys.argv) - 1:]

data = {}
for name, df in pd.read_excel(data_path, sheet_name=None).items():
    for wrong, right in LABEL_FIXES.items():
        name = name.replace(wrong, right)
    df = df.dropna(subset=["UNIVERSITY", "SALARY"])
    data[name.strip()] = [[str(u), int(s)] for u, s in zip(df["UNIVERSITY"], df["SALARY"])]

html = template_path.read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, separators=(",", ":")))
out_path.write_text(html, encoding="utf-8")
print(f"Saved {out_path}")
for name, rows in data.items():
    print(f"  {name}: {len(rows)} universities")
