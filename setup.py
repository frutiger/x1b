from setuptools import setup

setup(name='x1b',
      version='0.1',
      description='A macOS escape route for IP network packets',
      url='https://github.com/frutiger/x1b',
      author='Masud Rahman',
      license='MIT',
      packages=[
          'x1b.client',
          'x1b.gateway',
      ])

