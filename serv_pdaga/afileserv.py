from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes,os,socket,sys
from functools import partial

class FileListServerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, fileWhiteList=None, directory=None, **kwargs):
        self.fileWhiteList = fileWhiteList
        if directory is None:
            directory = os.getcwd()
        self.directory = os.fspath(directory)        
        super().__init__(*args, **kwargs)
    def do_GET(self):
        fn_ok=False
        fn=os.path.basename(self.path)
        if self.fileWhiteList is not None:
            for file_n in self.fileWhiteList:
                if file_n==fn:
                    fn_ok=True
            if not fn_ok:
                self.send_response(403)
                self.end_headers()
                return
        realfn=os.path.join(self.directory,fn)
        if not os.path.isfile(realfn):
            self.send_response(404)
            self.end_headers()
            return
        elif not os.access(realfn, os.R_OK):
            self.send_response(403)
            self.end_headers()
            return            
        _, self.fext = os.path.splitext(fn)
        try:
            self.content_type=mimetypes.types_map[self.fext]
        except:
            self.content_type="application/octet-stream"
        print(self.content_type)                
        self.send_response(200)
        self.send_header('Content-type', self.content_type)
        if self.content_type=="application/octet-stream":
            self.send_header('Content-Disposition', 'attachment; filename="'+fn+'"')
        self.end_headers()
        # Open the file
        with open(realfn, 'rb') as file: 
            self.wfile.write(file.read()) # Read the file and send the contents 
def _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr

def runhttp(HandlerClass=BaseHTTPRequestHandler,
         ServerClass=ThreadingHTTPServer,
         protocol="HTTP/1.0", port=8080, bind=None):
    """Test the HTTP request handler class.
    This runs an HTTP server on port 8000 (or the port argument).
    """
    ServerClass.address_family, addr = _get_best_family(bind, port)
    HandlerClass.protocol_version = protocol
    with ServerClass(addr, HandlerClass) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        print(
            f"Serving HTTP on {host} port {port} "
            f"(http://{url_host}:{port}/) ..."
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

class aFileServer():
    def __init__(self,fileList,dir=None,bind="0.0.0.0"):
        self.fileList=fileList
        self.dir=dir
        self.bind=bind
    def setDir(self,dir):
        self.dir=dir
    def run(self):
        handler_class = partial(FileListServerHandler,
            fileWhiteList=self.fileList,directory=self.dir)
        runhttp(
            HandlerClass=handler_class,
            bind=self.bind
        )

if __name__ == "__main__":
    fwl=["icon.png","L106.hdf5"]
    afs=aFileServer(fwl)
    afs.setDir(r"D:\temp")
    afs.run()