"""joblib-hadoop package installation module."""

from os.path import join as pjoin
from setuptools import setup, find_packages

if __name__ == '__main__':

    setup(name='joblibhadoop',
          version='0.1.0',
          description=('Provides Hadoop parallel and store backends for '
                       'joblib.'),
          url='https://github.com/joblib/joblib-hadoop',
          author='Alexandre Abadie',
          author_email='alexandre.abadie@inria.fr',
          license='BSD',
          platforms='any',
          packages=find_packages(),
          scripts=[pjoin('bin', 'joblib-yarn-worker')],
          install_requires=[
              'joblib>=0.10',
              'knit>=0.2'
          ],
          zip_safe=False,
         )
