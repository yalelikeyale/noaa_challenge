from setuptools import setup

setup(
    name="noaa_challenge",
    version="0.1.0",
    description="Singer.io tap for extracting data from the NOAA Weather API",
    author="yalelikeyale",
    url="https://github.com/yalelikeyale/noaa_challenge",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["noaa_tap"],
    install_requires=[
        'attrs==16.3.0',
        'singer-python==5.0.15',
        'requests==2.31.0'
    ],
    entry_points="""
    [console_scripts]
    noaa-challenge=noaa_tap:main
    """,
    packages=["noaa_tap"],
    package_data = {
        "schemas": ["noaa_tap/schemas/*.json"]
    },
    include_package_data=True,
)
