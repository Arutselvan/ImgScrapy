import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="imgscrapy",
    version="0.0.1",
    author="Arut Selvan",
    author_email="arutselvan710@gmail.omc",
    description="A simple imagescraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arutselvan/ImgScrapy",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['imgscrapy=imgscrapy.main:main']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)