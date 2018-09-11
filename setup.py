import setuptools


setuptools.setup(

    name = "TelegramSchoolBot",
    version = "3.0",
    url = "https://github.com/paolobarbolini/TelegramSchoolBot",

    license = "MIT",

    author = "Paolo Barbolini",
    author_email = "paolo@paolo565.org",

    description = "A telegram bot to interact with my school website",

    packages = [
        "telegramschoolbot",
    ],

    install_requires = [
        "botogram==0.5.0",
        "click",
        "requests",
        "beautifulsoup4",
        "sqlalchemy",
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
