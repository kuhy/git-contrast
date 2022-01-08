from setuptools import find_packages, setup


def readme():
    with open('README.org') as f:
        return f.read()


setup(
    name='git-contrast',
    version='0.1',
    description='CLI tool that reveals change in code quality between commits',
    long_description=readme(),
    keywords='git linter diff',
    url='http://github.com/kuhy/git-contrast',
    author='Ondřej Kuhejda',
    packages=find_packages(),
    install_requires=[
        'click',
        'git',
    ],
    entry_points={
        'console_scripts': ['git-contrast=git_contrast.main:cli'],
    },
    include_package_data=True,
    zip_safe=False
)
