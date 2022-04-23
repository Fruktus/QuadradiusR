from setuptools import setup

if __name__ == '__main__':
    setup(
        use_scm_version={
            'root': '..',
            'fallback_version': '0.0.0',
        },
        setup_requires=['setuptools_scm'],
    )
