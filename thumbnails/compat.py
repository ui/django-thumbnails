import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY2:
    string_types = (str, unicode)
    text_type = unicode
    _iteritems = "iteritems"

    def as_text(v):
        return v

else:
    string_types = (str,)
    text_type = str
    _iteritems = "items"

    def as_text(v):
        if v is None:
            return None
        elif isinstance(v, bytes):
            return v.decode('utf-8')
        elif isinstance(v, str):
            return v
        else:
            raise ValueError('Unknown type %r' % type(v))


def iteritems(d, **kw):
    """Return an iterator over the (key, value) pairs of a dictionary."""
    """Taken from six"""
    return iter(getattr(d, _iteritems)(**kw))
