"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from delorean import Delorean
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from . import utils


class PageModel(Model):
    """A page"""

    class Meta:
        table_name = "telegramschoolbot-pages"
        region = "eu-west-1"

    type = UnicodeAttribute(hash_key=True) # class/teacher/classroom
    name = UnicodeAttribute(range_key=True)
    display_name = UnicodeAttribute()
    url = UnicodeAttribute()
    last_file_id = UnicodeAttribute(default=None, null=True)
    last_hash = UnicodeAttribute(default=None, null=True)
    last_check = UTCDateTimeAttribute(default=None, null=True)

    def cached(self):
        return self.last_file_id is not None and self.last_hash is not None and self.last_check is not None


class PostModel(Model):
    """A post"""

    class Meta:
        table_name = "telegramschoolbot-posts"
        region = "eu-west-1"

    url = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    time = UTCDateTimeAttribute(default=lambda: Delorean().datetime)
    # Remove rows older than 4 months, pynamodb doesn't support enabling the ttl row in dynamodb
    # so you have to enable it manually from the aws console to make it work
    expire = NumberAttribute(default=lambda: Delorean().next_month(4).datetime.timestamp())


class SubscriberModel(Model):
    """A telegram subscriber"""

    class Meta:
        table_name = "telegramschoolbot-subscribers"
        region = "eu-west-1"

    chat_id = NumberAttribute(hash_key=True)
