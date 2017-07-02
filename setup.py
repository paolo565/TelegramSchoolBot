import setuptools


setuptools.setup(

    name = "TelegramSchoolBot",
    version = "2.0",
    url = "https://github.com/paolobarbolini/TelegramSchoolBot",

    license = "MIT",

    author = "Paolo Barbolini",
    author_email = "paolo@paolo565.org",

    description = "A telegram bot to interact with my school website",

    packages = [
        "telegramschoolbot",
    ],

    install_requires = [
        "botogram==0.4.dev0",
        "click",
        "requests",
        "beautifulsoup4",
        "sqlalchemy",
    ],

    dependency_links = [
        "https://github.com/paolobarbolini/botogram/archive/compile-language-files.zip#egg=botogram-0.4.dev0"
    ],

    entry_points = {
        "console_scripts": [
            "telegramschoolbot = telegramschoolbot.__main__:cli",
        ],
    },

    include_package_data = True,
    zip_safe = False,

    classifiers = [
        "Not on PyPI"
    ],

)
