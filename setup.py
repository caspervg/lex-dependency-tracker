from distutils.core import setup

setup(
    name='lex-dependency-tracker',
    version='0.0.1',
    packages=[''],
    url='https://github.com/caspervg/lex-dependency-tracker',
    license='MIT',
    author='Casper "caspervg" Van Gheluwe',
    author_email='caspervg@gmail.com',
    description='Python tool that attempts to automatically files to the dependency tracker',
    install_requires=['lex4py>=1.1.0', 'click', 'BeautifulSoup4']
)
