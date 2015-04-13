import os
from setuptools import find_packages, setup
import sys


PYTHON3 = sys.version_info > (3, )
HERE = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(HERE, 'README.md')) as f:
        return f.read()


def get_version():
    with open(os.path.join(HERE, "pyzab/__init__.py"), "r") as f:
        content = "".join(f.readlines())
    env = {}
    if PYTHON3:
        exec(content, env, env)
    else:
        compiled = compile(content, "get_version", "single")
        eval(compiled, env, env)
    return env["__version__"]


setup(name='pyzab',
      version=get_version(),
      description='A Python implementation of ZooKeeper\'s ZAB',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking",
      ],
      keywords='ZooKeeper ZAB',
      url='https://github.com/rgs1/pyzab',
      author='Raul Gutierrez Segales',
      author_email='rgs@itevenworks.net',
      license='Apache',
      packages=find_packages(),
      test_suite="pyzab.tests",
      scripts=['bin/demo'],
      install_requires=[],
      tests_require=['nose'],
      extras_require={
          'test': ['nose'],
      },
      include_package_data=True,
      zip_safe=False)
