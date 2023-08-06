from setuptools import setup

setup(
    name='getFavicon',
    version='0.1',
    packages=['.'],
    author='Tim Afanasiev',
    author_email='timbusinez@gmail.com',
    description='A Python library to fetch favicons from URLs',
    url='https://github.com/talmkg/getFavicon',
    license='MIT',
    install_requires=[
        'fastapi==0.100.1',
        'uvicorn[standard]==0.23.2',
        'aioredis==2.0.1',
        'requests-cache==1.1.0',
        'install==1.3.5',
        'tldextract==3.4.4',
        'pydantic==1.10.2',
        'pillow==10.0.0',
        'aiohttp==3.8.5',
        'asyncio==3.4.3',
        'lxml==4.9.3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.1',
    ],
)
