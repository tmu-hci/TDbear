import setuptools
import os

package_name: str = "tdbear"
package_version: str = "1.0.8"

root_dir: str = os.path.abspath(os.path.dirname(__file__))
long_description: str = ""
install_requires: list[str] = []

with open(os.path.join(root_dir, "requirements.txt"), "r", encoding="UTF-8") as f:
    install_requires = [*map(str.strip, f.readlines())]

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setuptools.setup(
    python_requires=">=3.11.0",
    name=package_name,
    version=package_version,
    description=("A module assisting with experiments " "and analysis of TDS methods."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.comp.sd.tmu.ac.jp/hci/TDbear/",
    project_urls={
        "Documentation": "https://www.comp.sd.tmu.ac.jp/hci/TDbear/",
        "Source": "https://github.com/tmu-hci/TDbear",
    },
    author="TMU HCI lab.",
    license="MIT",
    keywords="TDS TDbear",
    packages=setuptools.find_packages(),
    package_data={"tdbear": ["analyzer/dataset/*.yml"]},
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
    ],
)
