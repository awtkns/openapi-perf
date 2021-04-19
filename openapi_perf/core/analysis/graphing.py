from math import ceil
from typing import Tuple, Any, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import numpy as np
import pandas as pd
from cycler import cycler  # type: ignore
from scipy.stats import gaussian_kde  # type: ignore

custom_cycler = cycler(color=["#30a2da", "#fc4f30"])
plt.style.use("seaborn-whitegrid")

# TODO Define this properly, use a style sheet?
BOXPLOT_STYLE = dict(
    boxprops=dict(linewidth=1.5, color="#30a2da"),
    flierprops=dict(marker=".", markeredgecolor="#fc4f30", markersize=3),
    medianprops=dict(linewidth=1.5, color="#fc4f30"),
    whiskerprops=dict(linewidth=1.5, color="#30a2da"),
    capprops=dict(linewidth=1.5, color="#fc4f30"),
)


def get_dims(n_plots: int, cols: int = 2) -> Tuple[int, int]:
    """
    Gets the number of rows and columns for matplotlib layout
    :param n_plots: number of plots that will be plotted
    :param cols: number of columns
    :return: (row, col), (fig_size_h, fig_size_w)
    """
    return ceil(n_plots / cols), cols


def generate_graphs(results: pd.DataFrame, show: bool = True) -> Figure:
    df = _drop_percentiles(results).copy()
    df["time"] = df["time"] * 1000

    routes: pd.DataFrame = df["path_name"].unique()

    rows, cols = get_dims(len(routes))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 5))
    axes = axes.flatten()

    for i, route in enumerate(routes):
        ax = axes[i]
        ax.set_prop_cycle(custom_cycler)

        df[(df.path_name == route)].boxplot(
            by=["type", "status_code"], column="time", rot=30, ax=ax, **BOXPLOT_STYLE
        )

        ax.title.set_text(f"Route: {route}")
        ax.ylabel = "Response Time (s)"

    fig.suptitle("OpenAPI Performance Analysis", fontsize=20)
    fig.text(
        0.01,
        0.5,
        "Response Time (ms)",
        va="center",
        rotation="vertical",
        fontweight="bold",
    )

    fig.tight_layout()

    if show:
        fig.show()

    return fig


def _add_kde(
    ax: Any,
    data: pd.DataFrame,
    xlim: Tuple[float, float],
    samples: int = 1000,
    label: Optional[str] = None,
) -> None:
    kde = gaussian_kde(data)
    xx: np.ndarray = np.linspace(*xlim, samples)
    ax.plot(xx, kde.pdf(xx), label=label, linewidth=3)


def _get_xlim(data1: pd.Series, data2: pd.Series) -> Tuple[float, float]:
    x1 = min(data1.min(), data2.min())
    x2 = max(data1.max(), data2.max())

    return x1, x2


def _drop_percentiles(
    data: pd.DataFrame, column: str = "time", percentile: float = 0.995
) -> pd.DataFrame:
    high = data[column].quantile(percentile)
    low = data[column].quantile(1 - percentile)

    return data[(data[column] < high) & (data[column] > low)]


def plot_regression(new: pd.DataFrame, old: pd.DataFrame, show: bool = True) -> Figure:
    new = _drop_percentiles(new).copy()
    old = _drop_percentiles(old).copy()
    new["time"] = new["time"] * 1000
    old["time"] = old["time"] * 1000

    new_routes = new.drop_duplicates(["path_name", "type"])[["path_name", "type"]]
    old_routes = old.drop_duplicates(["path_name", "type"])[["path_name", "type"]]
    shared_routes = pd.merge(
        new_routes, old_routes, how="inner", on=["path_name", "type"]
    )

    rows, cols = get_dims(len(shared_routes))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4 / 3), sharex="all")
    axes = list(axes.flatten())

    n = 0
    for i, (_, row) in enumerate(shared_routes.iterrows()):
        ax = axes[i]
        ax.set_prop_cycle(custom_cycler)
        ax_kde = ax.twinx()
        ax_kde.set_prop_cycle(custom_cycler)
        axes.append(ax_kde)

        new_time = new[(new["path_name"] == row.path_name) & (new["type"] == row.type)][
            "time"
        ]
        old_time = old[(old["path_name"] == row.path_name) & (old["type"] == row.type)][
            "time"
        ]

        # TODO: might want to change later
        new_n = int((len(new_time) + len(old_time)) / 2)
        if new_n > n:
            n = new_n

        # TODO: Potential edge case if the min / max arent in the shared set of routes
        xlim = _get_xlim(new["time"], old["time"])

        # Plotting
        ax.hist(new_time, alpha=0.5, bins=20, label="New")
        ax.hist(old_time, alpha=0.5, bins=20, label="Old")
        _add_kde(ax_kde, new_time, xlim=xlim, label="New PDF")
        _add_kde(ax_kde, old_time, xlim=xlim, label="Old PDF")

        ax_kde.yaxis.set_visible(False)
        ax.title.set_text(f"Route: {row.path_name}, Method: {row.type}")
        ax.set_xlim(*xlim)
        ax.ylabel = "Response Time (s)"

    fig.suptitle("OpenAPI Regression Analysis", fontsize=20)
    lines_labels = [ax.get_legend_handles_labels() for ax in axes]
    lines, labels = [  # type: ignore
        sum(lol, []) for lol in zip(*lines_labels[11:13])
    ]  # TODO: THIS IS A HACK, does not generalize
    fig.legend(lines, labels, ncol=2)
    fig.autofmt_xdate(rotation=30)

    fig.text(0.5, 0.01, "Response Time (ms)", ha="center", fontweight="bold")
    fig.text(
        0.01, 0.5, f"Count (n={n})", va="center", rotation="vertical", fontweight="bold"
    )
    fig.text(
        0.98,
        0.5,
        "Probability Density",
        va="center",
        rotation="vertical",
        fontweight="bold",
    )

    fig.tight_layout(rect=(0.010, 0.025, 0.990, 0.995))

    if show:
        fig.show()

    return fig
