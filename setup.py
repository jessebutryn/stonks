from setuptools import setup, find_packages

setup(
    name='stonks',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
      'yfinance',
      'pandas',
      'tabulate',
      'currency_converter',
    ],
	entry_points={
        'console_scripts': [
            'stonks = stonks.__main__:main',
    	],
	},
)
