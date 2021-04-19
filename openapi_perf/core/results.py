from typing import Union, Any

from pandas import DataFrame, read_csv
from matplotlib.figure import Figure

from ._types import TEST_RESULTS, FILE_PATH
from .analysis import graphing


class PerfResults:
    def __init__(self, results: Union[DataFrame, TEST_RESULTS]) -> None:
        if type(results) is not DataFrame:
            self.results = DataFrame(results)
        else:
            self.results = results

    @staticmethod
    def from_csv(file_path: FILE_PATH) -> "PerfResults":
        df = read_csv(file_path, index_col=None)

        return PerfResults(df)

    def to_csv(self, file_path: FILE_PATH, **kwargs: Any) -> None:
        self.results.to_csv(file_path, index=False, **kwargs)

    def plot(self, show: bool = True) -> Figure:
        return graphing.generate_graphs(self.results, show)


class RegressionResults:
    def __init__(self, new: PerfResults, old: PerfResults) -> None:
        self.new = new
        self.old = old

    def plot(self, show: bool = True) -> Figure:
        return graphing.plot_regression(self.new.results, self.old.results, show)
