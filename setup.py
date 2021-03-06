from setuptools import setup

setup(
    name='BicycleParameters',
    version='0.2.0',
    author='Jason Keith Moore',
    author_email='moorepants@gmail.com',
    packages=['bicycleparameters', 'bicycleparameters.test'],
    url='http://pypi.python.org/pypi/BicycleParameters',
    license='LICENSE.txt',
    description='Generates and manipulates the physical parameters of a bicycle.',
    long_description=open('README.rst').read(),
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Operating System :: OS Independent',
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Physics']
)
