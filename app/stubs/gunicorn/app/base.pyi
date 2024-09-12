# Basic implementation of the type for gunicorn used in wsgi.py
# Since this is the only place used and very likely not subject to change,
# this stubbing is intentionally very minimal to just satisfy the type checking
class BaseApplication:

    def run(self):
        ...
