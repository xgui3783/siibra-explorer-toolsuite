from setuptools import setup, find_packages

setup(
    name="siibra-explorer-toolsuite",
    version="0.0.1a",
    author="Xiao Gui",
    author_email="xgui3783@gmail.com",
    packages=find_packages(include=["siibra_explorer_toolsuite"]),
    python_requires=">=3.6",
    install_requires=[
        "siibra>=0.3a6,<0.4"
    ]
)
