from itertools import chain

import matplotlib.pyplot as plt  # type ignore
import pandas as pd


def generate_graphs(
    results: pd.DataFrame
):
    df = results
    routes: pd.DataFrame = df['path_name'].unique()

    if len(routes) % 2:
        rows = len(routes) + 1
    else:
        rows = len(routes)
    rows = int(rows / 2)

    fig, axes = plt.subplots(rows, 2, figsize=(10, 8))
    axes = list(chain(*axes))  # flatten axis array

    for i, route in enumerate(routes):
        ax = axes[i]

        df[(df.path_name == route)].boxplot(by=["type", "status_code"], column="time", rot=30, ax=ax)
        ax.title.set_text(f"Route: {route}")
        ax.ylabel = "Response Time (s)"

    fig.suptitle('OpenAPI Performance Analysis', fontsize=20)
    plt.tight_layout()
    plt.show()

