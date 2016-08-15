
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

__version__ = None
exec(open('wikiscraper/version.py').read())

setup(name='wikiscraper',
      version=__version__,
      description=__doc__,
      author='Louis Dijkstra',
      author_email='louisdijkstra@gmail.com',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'bs4',
          'requests',
          'urllib3', 
          'docopt'
        ],
      entry_points = {
        'console_scripts': [
            'wikiscrape = wikiscraper.main:scrape',
            'wikiscrape_user = wikiscraper.main:scrape_user',
            'wikiscrape_article = wikiscraper.main:scrape_article',
            'wikistats = wikiscraper.main:get_number_users'
        ]
      },
      classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
      ],
      )
