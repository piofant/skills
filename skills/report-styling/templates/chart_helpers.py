"""Reusable matplotlib helpers for report-styling skill.

Import:
    from chart_helpers import PALETTE, setup_style, save_chart, annotate_winner

Templates inline at the bottom for quick copy-paste:
    - horizontal_bar()
    - scatter_pareto()
    - histogram_with_zones()
    - heatmap()
    - donut()
    - timeline_with_p95()
    - cost_breakdown_stacked()  (slide-style cost comparison)
"""

from __future__ import annotations

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


PALETTE: dict[str, str] = {
    'win':       '#2ca02c',
    'baseline':  '#1f77b4',
    'warn':      '#ff7f0e',
    'fail':      '#d62728',
    'muted':     '#7f7f7f',
    'highlight': '#ffd700',
    'bg':        '#f7f7f7',
}


def setup_style(*, slide: bool = False) -> None:
    """Apply canonical matplotlib rcParams. Call once at script start.

    slide=True: bigger fonts, thicker lines, suitable for presentation/slide-style charts.
    """
    base = {
        'font.size': 14 if slide else 11,
        'axes.titleweight': 'bold',
        'axes.titlesize': 18 if slide else 14,
        'axes.labelsize': 14 if slide else 12,
        'xtick.labelsize': 12 if slide else 10,
        'ytick.labelsize': 12 if slide else 10,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.facecolor': 'white',
        'lines.linewidth': 2.5 if slide else 1.5,
    }
    plt.rcParams.update(base)


def save_chart(fig, path: str, dpi: int = 120) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


def annotate_winner(ax, xy, text, *, xytext=None, color='green'):
    if xytext is None:
        xytext = (xy[0] + 0.2, xy[1] + 0.3)
    ax.annotate(
        text, xy=xy, xytext=xytext,
        arrowprops=dict(arrowstyle='->', color=color, lw=2),
        fontsize=12, color=f'dark{color}', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor=color),
    )


def color_by_threshold(value, *, win=4.5, warn=3.5):
    if value >= win: return PALETTE['win']
    if value >= warn: return PALETTE['warn']
    return PALETTE['fail']


def horizontal_bar_template():
    setup_style()
    names = ['Model A', 'Model B', 'Model C']
    values = [4.62, 4.53, 4.46]
    colors = [color_by_threshold(v) for v in values]
    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.barh(names, values, color=colors, edgecolor='black', alpha=0.85)
    for bar, v in zip(bars, values):
        ax.text(v + 0.05, bar.get_y() + bar.get_height()/2, f'{v:.2f}',
                va='center', fontsize=10, fontweight='bold')
    ax.axvline(4.0, color='red', linestyle='--', alpha=0.5, label='Threshold')
    ax.set_xlim(0, 5.5); ax.invert_yaxis()
    ax.set_xlabel('Mean overall score'); ax.legend(loc='lower right')
    ax.set_title('<ACTIVE HEADLINE>')
    save_chart(fig, '/tmp/horizontal_bar_demo.png')


def scatter_pareto_template():
    setup_style()
    points = [
        ('A', 0.10, 4.62, True), ('B', 0.10, 4.53, False),
        ('C', 0.80, 4.46, False), ('D', 0.30, 4.19, False),
    ]
    fig, ax = plt.subplots(figsize=(13, 8))
    for name, x, y, win in points:
        c = PALETTE['win'] if win else PALETTE['baseline']
        ax.scatter(x, y, s=200, c=c, alpha=0.7, edgecolors='black')
        ax.annotate(name, (x, y), xytext=(8, 4),
                    textcoords='offset points', fontsize=10)
    ax.set_xscale('log'); ax.axhline(4.0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Cost ($/1M, log)'); ax.set_ylabel('Quality')
    ax.set_title('<HEADLINE>')
    annotate_winner(ax, (0.10, 4.62), 'Лидер')
    save_chart(fig, '/tmp/scatter_pareto_demo.png')


def histogram_with_zones_template():
    setup_style()
    values = np.random.normal(4.3, 0.8, 130).clip(0, 5)
    threshold = 4.0
    fig, ax = plt.subplots(figsize=(12, 6))
    bins = np.arange(0, 5.5, 0.25)
    counts, edges, patches = ax.hist(values, bins=bins,
                                      color=PALETTE['baseline'],
                                      edgecolor='black', alpha=0.8)
    for i, p in enumerate(patches):
        if edges[i] < threshold: p.set_facecolor(PALETTE['fail'])
        elif edges[i] >= threshold + 0.5: p.set_facecolor(PALETTE['win'])
    ax.axvline(threshold, color='red', linestyle='--', linewidth=2)
    ax.axvline(np.mean(values), color='black', linestyle=':', linewidth=2,
               label=f'Mean={np.mean(values):.2f}')
    ax.set_xlabel('Score'); ax.set_ylabel('Count')
    ax.set_title(f'<HEADLINE — {sum(v>=threshold for v in values)}/{len(values)} pass>')
    ax.legend()
    save_chart(fig, '/tmp/histogram_demo.png')


def heatmap_template():
    setup_style()
    models = [f'M{i}' for i in range(8)]
    dims = [f'D{i}' for i in range(6)]
    data = np.random.uniform(0, 5, (len(models), len(dims)))
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(data, cmap='RdYlGn', vmin=0, vmax=5, aspect='auto')
    ax.set_xticks(range(len(dims))); ax.set_xticklabels(dims, rotation=20)
    ax.set_yticks(range(len(models))); ax.set_yticklabels(models)
    for i in range(len(models)):
        for j in range(len(dims)):
            v = data[i, j]
            color = 'black' if v > 2.5 else 'white'
            ax.text(j, i, f'{v:.1f}', ha='center', va='center',
                    color=color, fontsize=10, fontweight='bold')
    ax.set_title('<HEADLINE>')
    plt.colorbar(im, ax=ax, label='Score')
    save_chart(fig, '/tmp/heatmap_demo.png')


def cost_breakdown_stacked_template():
    """Slide-style stacked bar: total cost = input cost + output cost per model.

    Use case: compare $/run for N models, decompose into (in, out) so reader sees
    where the cost comes from. Annotate winner.
    """
    setup_style(slide=True)
    models = ['Lite-preview ★', 'Lite-stable', 'Flash', 'Claude Haiku',
              'GPT-4o mini', 'GPT-5 mini']
    in_cost = [0.041, 0.014, 0.293, 0.976, 0.146, 0.244]
    out_cost = [0.061, 0.010, 0.061, 0.122, 0.015, 0.146]

    fig, ax = plt.subplots(figsize=(14, 7))
    y = np.arange(len(models))
    bars1 = ax.barh(y, in_cost, color=PALETTE['baseline'],
                     label='Input', edgecolor='black', alpha=0.85)
    bars2 = ax.barh(y, out_cost, left=in_cost, color=PALETTE['warn'],
                     label='Output', edgecolor='black', alpha=0.85)
    for i, (ic, oc) in enumerate(zip(in_cost, out_cost)):
        total = ic + oc
        ax.text(total + 0.02, i, f'${total:.2f}',
                va='center', fontsize=12, fontweight='bold')
    ax.set_yticks(y); ax.set_yticklabels(models)
    ax.invert_yaxis()
    ax.set_xlabel('Cost per benchmark run ($)')
    ax.set_title('<ACTIVE HEADLINE — e.g. preview-Lite at lowest cost wins>',
                 pad=15)
    ax.legend(loc='lower right')
    save_chart(fig, '/tmp/cost_stacked_demo.png')


if __name__ == '__main__':
    horizontal_bar_template()
    scatter_pareto_template()
    histogram_with_zones_template()
    heatmap_template()
    cost_breakdown_stacked_template()
    print("All templates rendered to /tmp/*_demo.png")
