from typing import Union

from pandas import DataFrame, read_csv

from core._types import TEST_RESULTS, FILE_PATH
from core.analysis import graphing


class PerfResults:
    def __init__(self, results: Union[DataFrame, TEST_RESULTS]) -> None:
        if type(results) is not DataFrame:
            self.results: DataFrame = DataFrame(results)
        else:
            self.results: DataFrame = results

    @staticmethod
    def from_csv(file_path: FILE_PATH) -> "PerfResults":
        df = read_csv(file_path)

        return PerfResults(df)

    def to_csv(self, file_path: FILE_PATH, **kwargs) -> None:
        self.results.to_csv(file_path, **kwargs)

    def plot(self) -> None:
        graphing.generate_graphs(self.results)
