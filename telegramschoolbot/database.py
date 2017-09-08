"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import threading

# Temporary logging
"""
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
"""


threadLocal = threading.local()

class Database:
    def __init__(self, config):
        self.config = config


    def Session(self):
        engine = getattr(threadLocal, "engine", None)
        if engine is None:
            threadLocal.engine = create_engine(self.config["database_url"])

        session = getattr(threadLocal, "session", None)
        if session is None:
            session_factory = sessionmaker(bind=threadLocal.engine)
            threadLocal.session = scoped_session(session_factory)

        return threadLocal.session()
