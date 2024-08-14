from setuptools import setup, find_packages

setup(
    name = 'Cafe Color',
    version = '1.0.0',
    packages = find_packages(),
    install_requires = [
        'numpy',
        'opencv-python',
        'matplotlib',
        'rembg'
    ],
    author = 'Jorge A. Ramírez, Jose D. Ardila, Andrés F. Cerón',
    author_email = 'jorge.ramirez@profesores.uamerica.edu.co',
    description = 'Librería de análisis de imágenes para clasificación de café cereza en Python',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/Andress11/Color_Cafe.git',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.6',
)
