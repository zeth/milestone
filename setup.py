"""Setup file for milestone."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

milestone_classifiers = [
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS :: MacOS X",
]

with open("README.rst", "r") as fp:
    milestone_long_description = fp.read()

setup(name="milestone",
      description = 'Split an XML document by milestone element.',
      version=0.2,
      install_requires=['lxml'],
      author="Zeth",
      author_email="theology@gmail.com",
      py_modules=["milestone"],
      long_description=milestone_long_description,
      license="BSD",
      classifiers=milestone_classifiers,
      url = 'https://github.com/zeth/milestone', # use the URL to the github repo
)
