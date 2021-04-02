As an open source package, OpenApi-Perf accepts contributions from **all members** of the community. If you are interested in the
contributing, reading the development guidelines below may help you in the process. 😊

## Github

### Issues
Please create an issue to report a bug, request a feature or to simply ask a question.


### Pull Requests
Unless the pull request is a simple bugfix, please try to create an issue before starting on the implementation of your pull request.
This ensures that the potential feature is in alignment with CRUDRouter's goals moving forward. This also allows for feedback
on the feature and potential help on where to start implementation wise.

## Development

### Installing the Dev Requirements
OpenApi-Perf requires as set of development requirements that can installed with `pip` be found in `tests/dev.requirements.txt`

<div class="termy">

```console
$ pip install -r tests/dev.requirements.txt
---> 100%
```

</div>

### Testing
OpenApi-Perf utilizes the [pytest](https://docs.pytest.org/en/latest/) framework for all of its unittests. Tests can be run 
as shown below. When adding additional features, please try to add additional tests that prove that your implementation
works and is bug free.

<div class="termy">

```console
$ pytest
---> 100%
```

</div>

### Linting, Formatting and Typing

With `dev.requirements.txt` installed above you also install tools to lint, format and static type check the project.

To format the project run: 

```
black openapi_perf tests
```

To check styles, imports, annotations, pep8 etc. run:

```
flake8 openapi_perf
```

To check static types annotations run: 

```
mypy openapi_perf
```

### Documentation
OpenApi-Perfs's documentation was built using [mkdocs-material](https://squidfunk.github.io/mkdocs-material/). To start the development
documentation server, please first install mkdocs-material and then run the server as shown below.

<div class="termy">

```console
$ pip install mkdocs-material
---> 100%
$ cd docs/en
$ mkdocs serve
```

</div>


### Implementation Details
More to come



