from itertools import chain

from typing import Tuple
import pathlib

import matplotlib.pyplot as plt  # type ignore
from cycler import cycler

import numpy as np
import pandas as pd

from scipy.stats import gaussian_kde

custom_cycler = (cycler(color=["#30a2da", "#fc4f30"]))
plt.style.use("seaborn-whitegrid")

def get_dims(n_plots: int) -> Tuple[int, int]:
    """
    Gets the number of rows and columns for matplotlib layout
    :param n_plots: number of plots that will be plotted
    :return: (row, col)
    """

    if n_plots % 2:
        n_plots =+ 1

    return int(n_plots / 2), 2


def generate_graphs(results: pd.DataFrame) -> None:
    df = results
    df = df[df['time'] < 0.05]

    routes: pd.DataFrame = df["path_name"].unique()

    fig, axes = plt.subplots(*get_dims(len(routes)), figsize=(10, 8))
    axes = list(chain(*axes))  # flatten axis array

    for i, route in enumerate(routes):
        ax = axes[i]
        ax.set_prop_cycle(custom_cycler)

        df[(df.path_name == route)].boxplot(
            by=["type", "status_code"], column="time", rot=30, ax=ax
        )
        ax.title.set_text(f"Route: {route}")
        ax.ylabel = "Response Time (s)"

    fig.suptitle("OpenAPI Performance Analysis", fontsize=20)
    plt.tight_layout()
    plt.show()


def _add_kde(ax, data, xlim: Tuple[float, float] = None, samples: int = 1000, label: str = None):
    kde = gaussian_kde(data)
    xx = np.linspace(*xlim, samples)
    ax.plot(xx, kde.pdf(xx), label=label, linewidth=3)


def _get_xlim(data1: pd.Series, data2: pd.Series) -> Tuple[float, float]:
    x1 = min(data1.min(), data2.min())
    x2 = max(data1.max(), data2.max())

    return x1, x2


# def _drop_percentiles(data: pd.DataFrame, column: str = "time", percentile: float = 0.99) -> pd.DataFrame:
#     desc = data[[column]].describe(percentiles=[0.99])
#     print(desc.iloc)


def plot_regression(new: pd.DataFrame, old: pd.DataFrame):
    # _drop_percentiles(new)
    new = new[new['time'] < 0.05] # TODO: REMOVE
    old = old[old['time'] < 0.05]

    new_routes = new.drop_duplicates(["path_name", "type"])[["path_name", "type"]]
    old_routes = old.drop_duplicates(["path_name", "type"])[["path_name", "type"]]
    shared_routes = pd.merge(new_routes, old_routes, how='inner', on=['path_name', 'type'])

    fig, axes = plt.subplots(*get_dims(len(shared_routes)), figsize=(10, 8), sharex=True)
    axes = list(chain(*axes))  # flatten axis array

    for i, (_, row) in enumerate(shared_routes.iterrows()):
        ax = axes[i]
        ax.set_prop_cycle(custom_cycler)
        ax_kde = ax.twinx()
        ax_kde.set_prop_cycle(custom_cycler)
        axes.append(ax_kde)

        new_time = new[(new['path_name'] == row.path_name) & (new['type'] == row.type)]['time'] * 1000
        old_time = old[(old['path_name'] == row.path_name) & (old['type'] == row.type)]['time'] * 1000
        xlim = _get_xlim(new_time, old_time) # TODO: Potential edge case if the min / max arent in the shared set of routes

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
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels[11:13])]  # TODO: THIS IS A HACK, does not generalize
    fig.legend(lines, labels, ncol=2)
    fig.autofmt_xdate(rotation=30)

    fig.text(0.5, 0.01, 'Response Time (ms)', ha='center', fontweight='bold')
    fig.text(0.01, 0.5, 'Count', va='center', rotation='vertical', fontweight='bold')
    fig.text(0.98, 0.5, 'Probability Density', va='center', rotation='vertical', fontweight='bold')

    plt.tight_layout(rect=(.010, .025, .990, .995))
    plt.show()
