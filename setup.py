from setuptools import setup, find_packages

# Read requirements.txt, ignore comments
try:
    with open("requirements.txt", "r") as f:
        REQUIRES = [line.split("#", 1)[0].strip() for line in f if line.strip()]
except:
    print("'requirements.txt' not found!")
    REQUIRES = list()

setup(
    name="aurelius",
    version="1.0.0",
    include_package_data=True,
    author="Vivek",
    author_email="",
    url="https://github.com/vivek1240/aurelius",
    license="MIT",
    packages=find_packages(),
    install_requires=REQUIRES,
    description="AURELIUS: AI-Powered Wealth Intelligence Platform",
    long_description="""AURELIUS - Wisdom Meets Wealth""",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="Financial Analysis, AI Agents, Wealth Intelligence, Stock Analysis",
    platforms=["any"],
    python_requires=">=3.10, <3.12",
)
