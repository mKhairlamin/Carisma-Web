from setuptools import setup, find_packages

setup(
    name="Carisma",
    version="1.0.0",
    description="A car recommendation system using cosine similarity and affordability analysis",
    author="Khairul Amin",
    author_email="mkhairlamin@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "pandas",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
