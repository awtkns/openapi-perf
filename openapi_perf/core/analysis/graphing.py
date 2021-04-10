from typing import Union
from os import PathLike

import matplotlib.pyplot as plt  # type ignore
import pandas as pd

FILE_PATH = Union[str, PathLike]


def load_results(file_path: FILE_PATH) -> pd.DataFrame:
    return pd.read_csv(file_path)


def extract_params(row: pd.Series) -> pd.Series:
    # todo: this is a naive implementation
    split = row["path"].split("?")
    row["params"] = split[1] if len(split) == 2 else None
    row["path"] = split[0]

    return row


if __name__ == "__main__":
    df = load_results("results.csv")
    df = df.apply(extract_params, axis=1)

    correct = df[df.time < 0.01]
    errors = df[df.time > 0.01]
    plot = correct.boxplot(by=["type", "status_code"], column="time", rot=30)

    plot.ylabel = "Response Time (s)"
    plt.show()

    print(errors)
