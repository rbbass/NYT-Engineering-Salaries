"""Static dot histograms of salaries by university (Data/NYT_EE.xlsx) -> salary_histogram.png.

The PNG counterpart of the interactive chart: each sheet in the workbook is one
discipline, drawn as its own panel side by side (in place of the dropdown). Each
university is one dot, stacked in a salary bin. All panels share the same bins and
axes, so they can be compared directly. Portland State is highlighted and labeled
(in place of hover), and each panel carries the same summary as the web page.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "Data" / "NYT_EE.xlsx"
OUT = ROOT / "salary_histogram.png"

BIN_WIDTH = 5_000  # same salary bins for every discipline, starting at $0
X_MAX = 250_000
PITCH_IN = 0.06  # one bin wide and one university tall, in inches: columns sit right next to each other
DOT_FRACTION = 6 / 7  # dot diameter as a share of the pitch, leaving a small gap between dots
DPI = 150

# Figure layout, in inches
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 0.85, 0.3, 1.75, 1.15
PANEL_GAP = 0.45

HIGHLIGHT = "Portland State University"
HIGHLIGHT_COLOR = (106 / 255, 127 / 255, 16 / 255)

SURFACE = "#fcfcfb"
DOT = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e6e5e0"

FOOTNOTE = ("Earnings represent the median income reported on IRS tax records for students who "
            "graduated from a particular program in 2017–18 or 2018–19. A program is listed if "
            "there were more than 15 graduates who had received federal aid.")

# Typos in the workbook's sheet names, corrected for the panel titles
LABEL_FIXES = {"Mechancial": "Mechanical"}


def discipline_label(sheet):
    for wrong, right in LABEL_FIXES.items():
        sheet = sheet.replace(wrong, right)
    return sheet.strip()


def build(df):
    """Bin one discipline's salaries into the shared BIN_WIDTH bins; return the dot positions."""
    df = df.dropna(subset=["UNIVERSITY", "SALARY"]).sort_values("SALARY").reset_index(drop=True)

    # Bin index for each university; stack dots 1..n within each bin (lowest salary at bottom)
    df["bin"] = (df["SALARY"] // BIN_WIDTH).astype(int)
    df["level"] = df.groupby("bin").cumcount() + 1
    df["x"] = df["bin"] * BIN_WIDTH + BIN_WIDTH / 2
    return df


def summary(df):
    """The web page's summary line: count, median, range, and Portland State's salary and rank."""
    sal = df["SALARY"]
    lines = [f"{len(df)} universities · median ${sal.median():,.0f}",
             f"Range ${sal.min():,.0f} – ${sal.max():,.0f}"]
    psu = df.index[df["UNIVERSITY"] == HIGHLIGHT]
    if len(psu):
        i = psu[0]
        lines.append(f"Portland State ${sal[i]:,.0f} · #{len(df) - i} of {len(df)}")
    return "\n".join(lines)


sheets = pd.read_excel(DATA, sheet_name=None)
disciplines = [(discipline_label(name), build(df)) for name, df in sheets.items()]

# Shared axes: x spans to the highest salary in any discipline (to the end of its bin),
# y spans to the tallest column in any discipline
X_END = max(df["bin"].max() + 1 for _, df in disciplines) * BIN_WIDTH
Y_MAX = max(df["level"].max() for _, df in disciplines) + 1

panel_w = X_END / BIN_WIDTH * PITCH_IN
panel_h = Y_MAX * PITCH_IN
fig_w = MARGIN_L + MARGIN_R + len(disciplines) * panel_w + (len(disciplines) - 1) * PANEL_GAP
fig_h = MARGIN_T + MARGIN_B + panel_h
dot_area = (PITCH_IN * DOT_FRACTION * 72) ** 2  # scatter size is the marker area in points²

fig = plt.figure(figsize=(fig_w, fig_h), facecolor=SURFACE)

for i, (label, df) in enumerate(disciplines):
    left = MARGIN_L + i * (panel_w + PANEL_GAP)
    ax = fig.add_axes([left / fig_w, MARGIN_B / fig_h, panel_w / fig_w, panel_h / fig_h])
    ax.set_facecolor(SURFACE)

    is_psu = df["UNIVERSITY"] == HIGHLIGHT
    ax.scatter(df["x"], df["level"], s=dot_area, linewidths=0, zorder=3,
               c=[HIGHLIGHT_COLOR if h else DOT for h in is_psu])

    # Label Portland State's dot directly, since a PNG has no hover
    for _, row in df[is_psu].iterrows():
        ax.annotate("Portland State", xy=(row["x"], row["level"]),
                    xytext=(row["x"] + 14 * BIN_WIDTH, row["level"] + 12),
                    fontsize=8.5, color=TEXT, ha="left", va="center", zorder=4,
                    bbox=dict(boxstyle="round,pad=0.25", fc=SURFACE, ec="none"),
                    arrowprops=dict(arrowstyle="-", color=TEXT_2, lw=0.8,
                                    shrinkA=0, shrinkB=3))

    ax.set_xlim(0, X_END)
    ax.set_ylim(0, Y_MAX)
    ax.set_xticks([0, X_MAX], ["$0", "$250k"])
    ax.tick_params(axis="x", colors=TEXT_2, labelsize=9)
    ax.tick_params(axis="y", colors=TEXT_2, labelsize=9, labelleft=(i == 0), length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(TEXT_2)
    ax.set_xlabel("Salary", color=TEXT_2, fontsize=9.5)
    if i == 0:
        ax.set_ylabel("Number of universities", color=TEXT_2, fontsize=9.5)

    ax.text(0, 1, summary(df), transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8.5, color=TEXT_2, linespacing=1.5, parse_math=False)
    ax.text(0, 1, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=11.5,
            color=TEXT, fontweight="bold").set_position((0, 1 + 0.62 / panel_h))

fig.text(MARGIN_L / fig_w, 1 - 0.18 / fig_h, "Engineering salaries by university",
         ha="left", va="top", fontsize=16, color=TEXT)
fig.text(MARGIN_L / fig_w, 0.12 / fig_h, FOOTNOTE, ha="left", va="bottom",
         fontsize=7.5, color=TEXT_2, wrap=True)

fig.savefig(OUT, dpi=DPI, facecolor=SURFACE)
print(f"Saved {OUT} ({fig_w * DPI:.0f}x{fig_h * DPI:.0f}px)")
plt.show()
