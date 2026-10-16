"""Dot histogram of engineering salaries by university (Data/NYT_EE.xlsx).

Each university is one dot, stacked inside one of 20 salary bins.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).parent
DATA = ROOT / "Data" / "NYT_EE.xlsx"
OUT = ROOT / "salary_histogram.png"

N_BINS = 20
LABEL_TOP = 3  # direct-label the highest-salary universities

SURFACE = "#fcfcfb"
BAR = "#dbe7f6"
DOT = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e6e5e0"

df = pd.read_excel(DATA).sort_values("SALARY").reset_index(drop=True)
counts, edges = np.histogram(df["SALARY"], bins=N_BINS)
width = edges[1] - edges[0]

# Bin index for each university; stack dots 1..n within each bin (lowest salary at bottom)
df["bin"] = np.clip(np.digitize(df["SALARY"], edges) - 1, 0, N_BINS - 1)
df["level"] = df.groupby("bin").cumcount() + 1
df["x"] = edges[df["bin"]] + width / 2

fig, ax = plt.subplots(figsize=(13, 8), facecolor=SURFACE)
ax.set_facecolor(SURFACE)

ax.bar(edges[:-1], counts, width=width * 0.94, align="edge",
       color=BAR, edgecolor="none", zorder=1)
ax.scatter(df["x"], df["level"], s=22, color=DOT, edgecolor=SURFACE,
           linewidth=0.6, zorder=3)

for _, row in df.nlargest(LABEL_TOP, "SALARY").iterrows():
    ax.annotate(f"{row['UNIVERSITY']}\n${row['SALARY']:,.0f}",
                xy=(row["x"], row["level"]), xytext=(0, 12),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=9, color=TEXT_2)

ax.set_xticks(edges)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v / 1000:,.0f}k"))
ax.tick_params(axis="x", rotation=45, colors=TEXT_2, labelsize=9)
ax.tick_params(axis="y", colors=TEXT_2, labelsize=9)
ax.set_xlim(edges[0] - width * 0.3, edges[-1] + width * 0.3)
ax.set_ylim(0, counts.max() + 6)

ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(TEXT_2)

ax.set_xlabel("Salary (bin edges)", color=TEXT_2, fontsize=10)
ax.set_ylabel("Number of universities", color=TEXT_2, fontsize=10)
ax.set_title(f"Engineering salaries by university — {len(df)} universities, {N_BINS} bins",
             loc="left", color=TEXT, fontsize=14, pad=14)

fig.tight_layout()
fig.savefig(OUT, dpi=150, facecolor=SURFACE)
print(f"Saved {OUT}")
plt.show()
