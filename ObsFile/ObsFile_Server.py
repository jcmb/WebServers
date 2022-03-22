#! /usr/bin/env python3

# Really Simple Web server to support processing a file delivered via a post
#
# Done as an experiment to see if this was simpler than installing a web server and doing CGI
# It wasn't. All of the complexity was working out how to get the filename of the file
# cgi FieldStorage does this simply

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from pprint import pprint
import sys
import argparse
import cgi

hostName = ""
serverPort = 8080


def output_index_page(file):

    file.write(bytes(
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<link rel="stylesheet" type="text/css" href="https:///css/tcui-styles.css">
<title>Decode Observations Information for a GNSS file</title>
 </head>
<body class="page">
<div class="container clearfix">
  <div style="padding: 10px 10px 10px 0 ;"> <a href="http://construction.trimble.com/">
        <img src="https://trimbletools.com/images/trimble-logo.jpg" alt="Trimble Logo" id="logo"> </a>
      </div>
  <!-- end #logo-area -->
</div>
<div id="top-header-trim"></div><div id="content-area"><div id="content"><div id="main-content" class="clearfix">
<form target="_blank" action="/cgi-bin/T02_2_Obs" method="post" enctype="multipart/form-data" >

<table border="1" width="100%">
<caption>GNSS File Source</caption>
<col width="25%"><col width="75%"><tr><td>GNSS File:</td><td><input type="file" name="file" size="80"/></td></tr>
</table>
<br/>

<table border="1" width="100%">
<caption>Processing options</caption>
<col width="25%">
<col width="75%">
<tr><td>Output Type:</td><td>
<select name="Type">
   <option value="TXT">Text(TXT)</option>
   <option value="DAT">Dat</option>
   <option value="TMT">TMT</option>
   <option value="APPLANIX">Applanix</option>
   <option value="INFO">Info</option>
   <option value="NAVSOLN">NavSoln</option>
   <option value="KML">KML</option>
</select></td></tr>
</table>
<p/>

<input type="submit" value="Submit" />
</form></div></div></div>
</body>
</html>
""", "utf-8"))

class MyServer(BaseHTTPRequestHandler):

    def _set_response(self,responce):
        self.send_response(responce)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == "/" : # Send the Upload page as root
            self._set_response(200)        
            output_index_page(self.wfile)
        else:
            self.send_response(404) # Everything else is an error.
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Unknown Page</title></head></html>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<H1>Error</H1>", "utf-8"))
            self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
#        pprint(self.headers['content-type'])
#        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data

        if self.path != "/cgi-bin/T02_2_Obs" : #Only accept on the expected URL.
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Unknown Page</title></head></html>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<H1>Error</H1>", "utf-8"))
            self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
            return()
        
        fields = cgi.FieldStorage(
            fp = self.rfile,
            headers = self.headers,
            environ = {'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE': self.headers['content-type'],
                     }
            )        

#TODO This saves the file in the working directory. Need to move it. 
#TODO Should also get a temp name, and the filename be an attribute passed.
        out = open(fields["file"].filename, 'wb')
        out.write(fields["file"].value)
        out.close()        
        
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\n",
                str(self.path), str(self.headers))

        self._set_response(200)
        self.wfile.write("POST request for {} accepted\n".format(self.path).encode('utf-8'))


def process_args():

   parser = argparse.ArgumentParser(
               description='Simple Webserver Process Radio Data',
               fromfile_prefix_chars='@',
               epilog="(c) JCMBsoft 2022",
               formatter_class=argparse.ArgumentDefaultsHelpFormatter)

   parser.add_argument("-V", "--Verbose", action="count", help="Verbose reporting level")
   parser.add_argument("-P",'--Port', type=int,default=8080,help="Port to listen for HTTP connections on")
   parser.add_argument("-H",'--Host', type=str,default="",help="IP address to bind to")

   args=parser.parse_args()
   if args.Verbose==None:
      args.Verbose=0

   if args.Verbose>=2:
      logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")
   elif args.Verbose>=1:
      logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
   else:
      logging.basicConfig(level=logging.WARNING,format="%(asctime)s - %(levelname)s - %(message)s")
      
   return (vars(args))

def main():
    args=process_args()
    pprint(args)

    webServer = HTTPServer((args["Host"], args["Port"]), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


if __name__ == "__main__":        
   main()
