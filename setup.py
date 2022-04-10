from setuptools import setup

setup(
    name='zombie_dance_disease_tracker',
    version='1.0.0',
    packages=["zombie_dance_disease_tracker"],
    package_dir={'zombie_dance_disease_tracker': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-limiter',
        'flask-restx',
        'tinydb',
        'tinydb-serialization',
    ],
    entry_points={
        "console_scripts": [
            "zombie_dance_disease_tracker = src.__main__:main"
        ]
    },
)