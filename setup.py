from setuptools import setup, find_packages


def read_requirements():
    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()
    return [req.strip() for req in requirements if req.strip() and not req.startswith('#')]


setup(
    name='youcreep',
    version='0.1.23',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=read_requirements(),
    url='https://github.com/stevieflyer/youtube_crawler',
    author='Steve Flyer',
    author_email='steveflyer7@gmail.com',
    description='A powerful, asynchronous web crawler designed specifically for YouTube.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
