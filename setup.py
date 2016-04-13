from setuptools import setup

data_perf_scripts = [
    'share/perf_python_scripts/export-to-csv.py',
    'share/perf_python_scripts/export-to-csv.py',
    ]

setup(name='linux-perf-stats',
      version='0.0.1',
      description='Tools to get statistics from perf.data records',
      url='xxx',
      author='Alexis Berlemont',
      author_email='alexis.berlemont@gmail.com',
      license='GPL',
#      classifiers=[
#          TODO,
#      ],
      packages=['linux_perf_stats'],
      install_requires=['pandas'],
      package_data={
          'perf_python_scripts': data_perf_scripts,
      },
)
