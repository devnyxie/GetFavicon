from setuptools import setup

# Read the content of Markdown file
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='getFavicon',
    version='0.6.1',
    author='Tim Afanasiev',
    author_email='timbusinez@gmail.com',
    description='A Python library to fetch favicons from URLs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/talmkg/getFavicon',
    license='MIT',
    install_requires=[
        'tldextract==3.4.4',
        'pydantic==1.10.2',
        'pillow==10.0.0',
        'aiohttp==3.8.6',
        'asyncio==3.4.3',
        'lxml==4.9.3',
        'timeout-decorator==0.5.0',
        'lxml==4.9.3',
        'timeout-decorator==0.5.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.1',
    ],
)
