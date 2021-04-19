import pytest
from matplotlib.figure import Figure

from openapi_perf import PerfResults, RegressionResults


@pytest.mark.skip
def test_save_load():
    pr = PerfResults.from_csv("sample_results/new.csv")
    pr.to_csv("sample_results/new2.csv")

    pr2 = PerfResults.from_csv("sample_results/new2.csv")

    assert pr2.results.equals(pr)


def test_results_plot():
    new = PerfResults.from_csv("sample_results/new.csv")

    fig = new.plot(show=False)
    assert type(fig) is Figure


def test_regression_plot():
    new = PerfResults.from_csv("sample_results/new.csv")
    old = PerfResults.from_csv("sample_results/old.csv")

    fig = RegressionResults(new, old).plot(show=False)
    assert type(fig) is Figure

