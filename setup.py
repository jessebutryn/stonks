from setuptools import setup, find_packages

setup(
    name='stonks',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'yfinance==0.2.33',
		'pandas==2.0.3',
		'tabulate==0.9.0',
    ],
	entry_points={
        'console_scripts': [
            'stonks = stonks.__main__:main',
    	],
	},
)
