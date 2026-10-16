"""Interactive dot histogram of engineering salaries by university (Data/NYT_EE.xlsx).

Each sheet in the workbook is one engineering discipline; a dropdown picks which one
is shown. Each university is one dot, stacked in a salary bin. All disciplines share
the same bins and axes, so they can be compared directly.
Hover a dot to see the university and its salary. Writes salary_histogram.html.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).parent
DATA = ROOT / "Data" / "NYT_EE.xlsx"
OUT = ROOT / "salary_histogram.html"

BIN_WIDTH = 5_000  # same salary bins for every discipline, starting at $0
DOT_PX = 6  # dot diameter; each stack level is sized to this so dots nearly touch
GAP_PX = 1  # space between neighboring dots, both within a column and between columns
MARGIN_T, MARGIN_B, MARGIN_L, MARGIN_R = 110, 60, 70, 30
X_MAX = 250_000

HIGHLIGHT = "Portland State University"
HIGHLIGHT_COLOR = "rgb(106,127,16)"

SURFACE = "#fcfcfb"
DOT = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e6e5e0"

# Typos in the workbook's sheet names, corrected for the dropdown label
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
    df["bin_label"] = [f"${b * BIN_WIDTH:,.0f} – ${(b + 1) * BIN_WIDTH:,.0f}" for b in df["bin"]]
    return df


sheets = pd.read_excel(DATA, sheet_name=None)
disciplines = [(discipline_label(name), build(df)) for name, df in sheets.items()]

# Shared axes: x spans to the highest salary in any discipline (to the end of its bin),
# y spans to the tallest column in any discipline
X_END = max(df["bin"].max() + 1 for _, df in disciplines) * BIN_WIDTH
Y_MAX = max(df["level"].max() for _, df in disciplines) + 1

# Size the plot area so one count step on the y axis, and one bin on the x axis,
# each equal one dot plus a small gap: columns sit right next to each other
PLOT_HEIGHT = int(Y_MAX * (DOT_PX + GAP_PX))
PLOT_WIDTH = int(X_END / BIN_WIDTH * (DOT_PX + GAP_PX))

fig = go.Figure()
for i, (label, df) in enumerate(disciplines):
    fig.add_scatter(
        x=df["x"], y=df["level"], mode="markers", visible=(i == 0),
        marker=dict(size=DOT_PX, line=dict(width=0),
                    color=np.where(df["UNIVERSITY"] == HIGHLIGHT, HIGHLIGHT_COLOR, DOT)),
        customdata=df[["UNIVERSITY", "SALARY", "bin_label"]],
        hovertemplate="<b>%{customdata[0]}</b><br>Salary: $%{customdata[1]:,.0f}"
                      "<br>Bin: %{customdata[2]}<extra></extra>",
        name=label,
    )

# Each dropdown choice shows only its own discipline's dots
buttons = [
    dict(label=label, method="restyle",
         args=[{"visible": [j == i for j in range(len(disciplines))]}])
    for i, (label, _) in enumerate(disciplines)
]

fig.update_layout(
    height=PLOT_HEIGHT + MARGIN_T + MARGIN_B,
    width=PLOT_WIDTH + MARGIN_L + MARGIN_R,
    title=dict(text="Engineering salaries<br>by university", x=0.02,
               y=0.98, yref="container", yanchor="top", font=dict(size=15, color=TEXT)),
    plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
    font=dict(color=TEXT_2),
    showlegend=False,
    hoverlabel=dict(bgcolor="white", font_size=12),
    xaxis=dict(
        title="Salary", tickvals=[0, X_MAX], ticktext=["$0", "$250k"],
        showgrid=False, linecolor=TEXT_2, range=[0, X_END],
    ),
    yaxis=dict(title="Number of universities", gridcolor=GRID, zeroline=False,
               range=[0, Y_MAX]),
    margin=dict(l=MARGIN_L, r=MARGIN_R, t=MARGIN_T, b=MARGIN_B),
    updatemenus=[dict(
        buttons=buttons, active=0, direction="down", showactive=True,
        x=0, xanchor="left", y=1, yanchor="bottom", pad=dict(b=10),
        bgcolor="white", bordercolor=GRID, font=dict(size=12, color=TEXT),
    )],
)

fig.write_html(OUT, include_plotlyjs="cdn")
print(f"Saved {OUT}")
print(f"  chart {PLOT_WIDTH + MARGIN_L + MARGIN_R}x{PLOT_HEIGHT + MARGIN_T + MARGIN_B}px, "
      f"x to ${X_END:,}, y to {Y_MAX}")
for label, df in disciplines:
    print(f"  {label}: {len(df)} universities, tallest column {df['level'].max()}")
fig.show()
