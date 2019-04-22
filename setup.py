import setuptools

setuptools.setup(
    name="probecard",
    version="0.0.6",
    author="William Wyatt",
    author_email="wwyatt@ucsc.edu",
    description="GUI for probecard measurements.",
    long_description="GUI for probecard measurements.",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/Tsangares/Probecard",
    scripts=['probecard/bin/probecard'],
    install_requires=[
        "cycler==0.10.0",
        "future==0.17.1",
        "iso8601==0.1.12",
        "kiwisolver==1.0.1",
        "matplotlib==3.0.2",
        "numpy==1.15.4",
        "pyparsing==2.3.0",
        "PyQt5==5.11.3",
        "PyQt5-sip==4.19.13",
        "pyserial==3.4",
        "python-dateutil==2.7.5",
        "PyVISA==1.9.1",
        "PyYAML==4.2b4",
        "six==1.11.0",
        "XlsxWriter==1.1.2",
	"contraption>=0.0.2",
        "urllib3>=1.24.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
