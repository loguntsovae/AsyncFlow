from setuptools import setup, find_packages

setup(
    name="order_service",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "."},
    python_requires=">=3.11",
)