import hashlib
import random
import string

from app.models import UrlModel


def shorten_url(long):
    while True:
        suffix = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        short = hashlib.md5(bytes(long + suffix, encoding="utf-8"))
        short = short.hexdigest()[:7]
        if len(UrlModel.objects(short=short)) == 0:
            break
    return short
