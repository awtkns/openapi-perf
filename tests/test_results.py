from pytest import mark

from openapi_perf import PerfResults, RegressionResults


@mark.noautofixt
def test_results_plot():
    new = PerfResults.from_csv("sample_results/new.csv")
    new.plot()


@mark.noautofixt
def test_regression_plot():
    new = PerfResults.from_csv("sample_results/new.csv")
    old = PerfResults.from_csv("sample_results/old.csv")
    RegressionResults(new, old).plot()
