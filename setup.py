from setuptools import setup, find_packages

VERSION = "0.0.5"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="openapi-perf",
    version=VERSION,
    author="Adam Watkins, Ethan Haid",
    author_email="cadamrun@gmail.com",
    packages=find_packages(exclude=("tests.*", "tests")),
    url="https://github.com/awtkns/openapi-perf",
    license="MIT",
    description="An Automatic REST Endpoint Performance Test Generation Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=required,
    python_requires=">=3.6",
    keywords=["OpenAPI", "REST", "Performance Testing"],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Typing :: Typed",
    ],
)
