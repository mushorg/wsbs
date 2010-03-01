# Thanks to http://blog.doughellmann.com/2009/07/pymotw-urllib2-library-for-opening-urls.html

import itertools
import mimetools
import mimetypes
import urllib2
import sys
import base64
import time


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        fileHandle.close()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)

def to_sandbox(php_file = ""):
    
    url = 'https://blog.honeynet.org.my/pKaji'
    username = 'glastopf'
    password = '4ku4nakm3s14'
    scheme = "Basic"
    realm = "Application"
    xml_output = True
    
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    # Connect to the sandbox to get the cookie and authenticity token
    try:
        handle = urllib2.urlopen(req)
    except IOError, e:
        print "Error while connecting to the sandbox: %s" % e
        return
    
    # Extract the cookie
    cookie = str(handle.info()).partition("Set-Cookie: ")[2].partition("; path")[0]
    if cookie == "":
        print "No cookie found."
    # Get the authenticity token
    for line in handle.readlines():
        if "authenticity_token" in line:
            token = line.partition("value=\"")[2].partition("\"")[0]
    if not token:
        print "no token found!"
        return
    # Generate the form
    form = MultiPartForm()
    form.add_field('authenticity_token', token)
    if xml_output == True:
        form.add_field('displayFormat[]', 'xml')
    form.add_file('mohon[bin_data]', str("file/" + php_file), fileHandle=open("file/" + php_file, 'r'))
    body = str(form)
    # Form the request
    request = urllib2.Request('https://blog.honeynet.org.my/pKaji/mohon/uploadFile')
    request.add_header('User-agent', 'Glastopf Web Honeypot Sensor')
    request.add_header('Content-type', form.get_content_type())
    request.add_header('Content-length', len(body))
    request.add_header("Cookie", cookie)
    request.add_header("Authorization", authheader)
    request.add_data(body)
    
    #print
    #print 'OUTGOING DATA:'
    #print request.get_data()
    #print "Request to sandbox formed!"

    #print 'SERVER RESPONSE:'
    try:
        start_time = time.time()
        out = urllib2.urlopen(request)
        #print "Parsed file %s returned from sandbox!" % php_file
        
        time_difference = time.time() - start_time
        #print "Sandbox runtime = %d seconds" % int(time_difference)
        return out
    
    except urllib2.HTTPError, e:
        #print e.read()
        print "Sandbox response error: %s" % e
        return


