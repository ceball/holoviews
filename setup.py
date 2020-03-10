#!/usr/bin/env python

import json
import os
import sys
import shutil

from setuptools import setup, find_packages

import pyct.build

setup_args = {}
install_requires = ['param>=1.8.0,<2.0', 'numpy>=1.0', 'pyviz_comms>=0.7.2', 'panel>=0.7.0']

extras_require = {}


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']

setup_args.update(dict(
    name='holoviews',
    version=get_setup_version("holoviews"),
    python_requires=">=2.7",
    install_requires=install_requires,
    extras_require=extras_require,
    description='Stop plotting your data - annotate your data and let it visualize itself.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jean-Luc Stevens and Philipp Rudiger",
    author_email="holoviews@gmail.com",
    maintainer="PyViz Developers",
    maintainer_email="developers@pyviz.org",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='https://www.holoviews.org',
    entry_points={
        'console_scripts': [
            'holoviews = holoviews.util.command:main'
        ]},
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Framework :: Matplotlib",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"]
))


if __name__ == "__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'holoviews/examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    if 'install' in sys.argv:
        header = "HOLOVIEWS INSTALLATION INFORMATION"
        bars = "="*len(header)

        extras = '\n'.join('holoviews[%s]' % e for e in setup_args['extras_require'])

        print("%s\n%s\n%s" % (bars, header, bars))

        print("\nHoloViews supports the following installation types:\n")
        print("%s\n" % extras)
        print("Users should consider using one of these options.\n")
        print("By default only a core installation is performed and ")
        print("only the minimal set of dependencies are fetched.\n\n")
        print("For more information please visit http://holoviews.org/install.html\n")
        print(bars+'\n')

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
