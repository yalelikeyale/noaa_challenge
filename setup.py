from setuptools import setup

setup(
    name="noaa-tap",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["noaa_tap"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    woo-tap=woo_tap:main
    """,
    packages=["noaa_tap"],
    package_data = {
        "schemas": ["noaa_tap/schemas/*.json"]
    },
    include_package_data=True,
)
