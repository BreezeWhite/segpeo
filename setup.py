import setuptools


with open('README.md') as red:
    ldest = red.read()

with open('requirements.txt') as req_f:
    reqs = req_f.read().split()

setuptools.setup(
    name='segpeo',
    version='0.1.0',
    author='SeanChan',
    author_email='cxgincsu@163.com',
    maintainer='BreezeWhite',
    maintainer_email='miyasihta2010@tuta.io',
    description='Robust Human Matting via Semantic Guidance',
    long_description=ldest,
    long_description_content_type='text/markdown',
    license='License :: OSI Approved :: MIT License',
    license_files=('LICENSE',),
    url='https://github.com/BreezeWhite/segpeo',
    packages=setuptools.find_packages(),
    install_requires=reqs,
    entry_points={'console_scripts': ['segpeo = segpeo.main:main']},
    keywords=['human-segmentation', 'semantic-segmentation', 'AI', 'machine-learning', 'image-processing'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control :: Git'
    ]
)
