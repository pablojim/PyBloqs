#!/bin/env python
from distutils.file_util import copy_file
import glob
import logging
import os
import sys


from setuptools import setup, find_packages, Command
from setuptools.command.install import install


# Convert Markdown to RST for PyPI
# http://stackoverflow.com/a/26737672
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    changelog = pypandoc.convert('CHANGES.md', 'rst')
except (IOError, ImportError, OSError):
    long_description = open('README.md').read()
    changelog = open('CHANGES.md').read()


def _copy_hc_files(source_paths, dest_path):
    """Copies all .js files (excluding .src.js) from source_path into dest_path."""
    if source_paths is None:
        logging.warn("***** Option --highcharts not specified. Highcharts blocks will not work! ******")
        return

    hc_files = []
    for source_path in source_paths:
        hc_files += set([i for i in glob.glob(os.path.join(source_path, '*.js')) if not i.endswith('.src.js')])
    if len(hc_files) > 0:
        for f in hc_files:
            copy_file(f, dest_path)
    else:
        logging.error(" No *.js files (excluding *.src.js) found in highcharts-paths: {}"
                      .format(source_paths))
        sys.exit(1)
        
def _copy_wkhtmltopdf(src_path):
    files = ['wkhtmltopdf' , 'wkhtmltoimage']
    for f in files:
        source = os.path.join(src_path, f)
        dest = os.path.join(sys.exec_prefix, 'bin', f)
        copy_file(source, dest)


class LoadHighcharts(Command):
    user_options = [
        ("highcharts=", None, "List of paths with highcharts, e.g. ~/highcharts/js/,~/highcharts-heatmap/js/"),
    ]

    def initialize_options(self):
        self.highcharts = None

    def finalize_options(self):
        assert self.highcharts is not None, "Please provide --highcharts parameter"
        self.ensure_string_list("highcharts")
        self.highcharts = [os.path.abspath(os.path.expanduser(p)) for p in self.highcharts]

    def copy_hc_files(self):
        dest_path = os.path.join("pybloqs", "static")
        _copy_hc_files(self.highcharts, dest_path)

    def run(self):
        self.copy_hc_files()

class LoadWkhtmltopdf(Command):
    user_options = [
        ("wkhtmltopdf=", None, "Path for wkhtmltopdf and wkhtmltoimage."),
    ]

    def initialize_options(self):
        self.wkhtmltopdf = None

    def finalize_options(self):
        assert self.wkhtmltopdf is not None, "Please provide --wkhtmltopdf parameter"
        self.ensure_string("wkhtmltopdf")
        self.wkhtmltopdf = os.path.abspath(os.path.expanduser(self.wkhtmltopdf))

    def run(self):
        _copy_wkhtmltopdf(self.wkhtmltopdf)


class PyBloqsInstall(install):
    # Options tuples: long name, short name and help string
    user_options = install.user_options + [
        ("highcharts=", None, "List of paths with highcharts, e.g. ~/highcharts/js/,~/highcharts-heatmap/js/"),
        ("wkhtmltopdf=", None, "Path for wkhtmltopdf and wkhtmltoimage."),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.highcharts = None

    def finalize_options(self):
        install.finalize_options(self)
        self.ensure_string_list("highcharts")
        if self.highcharts is not None:
            self.highcharts = [os.path.abspath(os.path.expanduser(p)) for p in self.highcharts]

    def copy_hc_files(self):
        dest_path = os.path.join("build", "lib", "pybloqs", "static")
        _copy_hc_files(self.highcharts, dest_path)

    def minimise_js_files(self):
        """Find all .js files (including sub-directories) and minimise them with jsmin."""
        from jsmin import jsmin  # Lazy load to give setup machinery a chance to download dependency
        for dir_name, _, files in os.walk(os.path.join("build", "lib", "pybloqs", "static")):
            for f in files:
                if f.lower().endswith(".js"):
                    file_name = os.path.join(dir_name, f)
                    logging.info("Minimizing file: {}".format(file_name))
                    with open(file_name, 'r') as f_js:
                        content = f_js.read()
                    with open(file_name, 'w') as f_js:
                        f_js.write(jsmin(content))

    def run(self):
        install.run(self)
        logging.getLogger().setLevel(logging.INFO)
        self.copy_hc_files()
        if self.wkhtmltopdf is not None:
            _copy_wkhtmltopdf(self.wkhtmltopdf)
        self.minimise_js_files()


setup(
    name="pybloqs",
    version="1.0.0",
    author="Man AHL Technology",
    author_email="ManAHLTech@ahl.com",
    description="Data Visualization and Report Building",
    long_description='\n'.join((long_description, changelog)),
    keywords=["ahl", "pdf", "html", "visualization", "report"],
    url="https://github.com/manahl/pybloqs",
    setup_requires=["jsmin"],
    install_requires=[
        "beautifulsoup4",
        "matplotlib",
        "markdown",
        "html5lib",
        "pandas",
        "docutils",
        "lxml",
        "pyyaml",
        "jinja2"
    ],
    tests_require=[
        "mock",
        "pytest",
        "pytest-cov"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    cmdclass={
        "install": PyBloqsInstall,
        "load_highcharts": LoadHighcharts,
        "load_wkhtmltopdf": LoadWkhtmltopdf
    },
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"pybloqs.static": ["block-core.js",
                                  "jsinflate.js",
                                  "css/pybloqs_default/main.css"],
                  "pybloqs.htmlconv": ["wkhtmltoimage",
                                    "wkhtmltopdf"]}
)