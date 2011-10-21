#!/usr/bin/env python
#
# Copyright (c) 2005-2008  Dustin Sallings <dustin@spy.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# <http://www.opensource.org/licenses/mit-license.php>
"""
Yet another HTTP client abstraction.
"""

import sys
PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.request import Request
    from urllib.request import urlopen
    import base64

    def b64encode(s):
        return str(base64.b64encode(bytes(s, 'utf8')), 'utf8')
else:
    import urllib
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib2 import Request, urlopen

    from base64 import b64encode

def fetch(url, data=None, username=None, password=None, headers={},
          method=None):
    request = Request(url, data=data, headers=headers)
    if method:
        request.get_method = lambda: method
    if username and password:
        request.add_header('Authorization',
                           'Basic ' + b64encode("%s:%s" % (username,
                                                           password)).strip())
    return urlopen(request)
