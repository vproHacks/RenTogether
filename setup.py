import setuptools

with open('README.md', 'r') as readme:
    # Wow atleast the computer read it
    long_description = readme.read()

setuptools.setup(
    name="RenTogether-vproHacks",
    version='0.0.1',
    author='Vraj Prajapati',
    author_email='vrajip@gmail.com',
    description='A Utility that Allows everyone to play VNs Together!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vproHacks/RenTogether',
    packages=['src'],
    install_requires=['pygetwindow', 'flask', 'keyboard'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points = {
        'console_scripts': [
            'rentogether=src.__main__:main',
        ],
    },
    python_requires='>=3.6'
)
