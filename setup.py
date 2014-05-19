from setuptools import setup

setup(
    name='python-package-requirements',
    version='1.0',
    long_description=__doc__,
    packages=['py_pkg_req'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
	'Flask',
        'requests',
    ],
    entry_points = {
        'console_scripts': [
            'flask-ctl = py_pkg_req.script:run',
        ]
    },
)
