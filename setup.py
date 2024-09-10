#!/usr/bin/env python3
import os

from setuptools import setup

# parse the repo name from the git repository

URL = "https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel"
PLUGIN_CLAZZ = "NevermindPlugin"

AUTHOR, REPO = URL.split(".com/")[-1].split("/")
ADDITIONAL_AUTHORS = ["jarbasai"]
AUTHORS = ADDITIONAL_AUTHORS + [AUTHOR]
PKG = "ovos_utterance_plugin_cancel"

BASEDIR = os.path.abspath(os.path.dirname(__file__))
PKGDIR = os.path.join(BASEDIR, PKG)
UTTERANCE_ENTRY_POINT = f'{REPO.lower()}={PKG}:{PLUGIN_CLAZZ}'


def get_version():
    """ Find the version of the package"""
    version_file = f'{BASEDIR}/ovos_utterance_plugin_cancel/version.py'
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def find_resource_files():
    resource_base_dirs = ("locale", "res",)  # Removed "ui"
    package_data = list()
    for res in resource_base_dirs:
        if os.path.isdir(os.path.join(PKGDIR, res)):
            for directory, _, files in os.walk(os.path.join(PKGDIR, res)):
                for f in files:
                    path = os.path.relpath(os.path.join(directory, f), PKGDIR)
                    package_data.append(path)
    return package_data


with open(os.path.join(BASEDIR, "README.md"), "r") as f:
    long_description = f.read()


setup(
    name=REPO,
    description='OpenVoiceOS Utterance Cancel Plugin',
    long_description=long_description,
    version=get_version(),
    author=AUTHOR,
    author_email='jarbasai@mailfence.com',
    url=URL,
    license='apache-2.0',
    packages=[PKG],
    package_data={PKG: find_resource_files()},
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'neon.plugin.text': UTTERANCE_ENTRY_POINT
    }
)
