from setuptools import setup

setup(
    name='PySimplexTree',
    version='0.0.1',
    license='MIT',
    author='Ryan Rose',
    author_email='ryanthrose@gmail.com',
    description='Simplex Tree',
    packages=['pysimplextree'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
		'matplotlib',
		'numpy',
		'numpy-stl'
    ]
)
