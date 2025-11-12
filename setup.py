from setuptools import find_packages, setup

setup(
    name="fxharry",
    version="0.1.0",
    packages=find_packages(exclude=("tests", "frontend", "ml_pipeline", "genai_agent")),
    install_requires=[],
    description="Institutional AI trading platform scaffold",
)
