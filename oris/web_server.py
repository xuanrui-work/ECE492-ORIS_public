from http import server
from typing import Type, List

from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
import cgi, os, time

from matplotlib import container

from band_detection import BandDetectionResult
from record import *
from resistor import *

from threading import Thread

IMG_SIZE = (200,200)

class MyRequestHandler(BaseHTTPRequestHandler):
    '''
        (Class) Http Server Reuqest Handler
    '''
    num_result = 10
    _abs_direct = os.path.join(os.getcwd(), RECORD_SAVE_PATH[2:-1])
    _img_path = os.path.join(_abs_direct,'temp')
    _search_date = ''
    _pickle_list = []

    def pickle_handler(self,path: str) -> List[BandDetectionResult]:
        '''
        unpack the pickle and store the object in the pickle list

        parameter:
            path(directory for scan result)
        '''
        os.makedirs(path, exist_ok=True)
        files = os.listdir(path)
        
        self._pickle_list = []
        for file in files:
            if os.path.isfile(os.path.join(path, file)):
                img_path = os.path.join(path, file)
                temp = read_from_file(img_path)
                
                temp_path = os.path.join(path, 'temp')
                os.makedirs(temp_path, exist_ok=True)
                
                image = temp.image.copy()
                temp.detection_result.draw_on_img(image)
                
                Image.fromarray(image).save(os.path.join(temp_path, file[:-7] + '.png'), 'PNG')
                self._pickle_list.append(temp)

    def table_gen(self, path: str, date_limit: str) -> str:
        '''
        generate the html table for the result display

        parameter:
            (str)path(directory for image of scan result)
            (str)date_limit(the date delimitor for the result display)
        '''
        my_table = '<table border="1"><tr><th>Picture</th><th>Scan Result</th><th>Detection Result</th><th>Date</th></tr>'

        for element in self._pickle_list:
            if element is None:
                continue
            my_resistor = Resistor(element.detection_result)
            my_time = element.time
            if my_time.strftime('%Y-%m-%d_%H-%M-%S').find(date_limit) != -1:
                    my_table += '<tr><td><img src="' + element.time.strftime('%Y-%m-%d_%H-%M-%S')+ '.png' + '" width="' + str(IMG_SIZE[0]) + '" height ="' + str(IMG_SIZE[1]) + '"></td>'
                    my_table += '<td><table>'
                    #################################
                    # display scan result here
                    for b in element.detection_result.detected_bands:
                        if b is not None:
                            my_table += '<tr><td>'
                            my_table += b.label
                            my_table += '</td><td>'
                            myscore = '{:d}'.format(round(b.score*100))
                            my_table += myscore
                            my_table += '%</td></tr>'
                    my_table += '</table></td>'
                    # display detection result here
                    my_table += '<td>'
                    my_table += '<table><tr><td>Resistance: </td></tr>'
                    my_table += '<tr><td>' + f'{my_resistor.get_resistance():,}' + ' Ohm</td></tr>'
                    my_table += '<tr><td>Tolenrance: </td></tr>'
                    my_table += '<tr><td>' + f'{my_resistor.get_tolerance()}' + '% </td></tr>'
                    my_table += '</table></td>'
                    ##################################
                    my_table += '<td>' + my_time.strftime('%Y-%m-%d_%H-%M-%S') + '</td></tr>'
        my_table += '</table>'
        return my_table

    def do_GET(self):
        '''
        Handle the 'GET' request to the server
        '''
        try:
            if self.path.endswith('/'):
                self.pickle_handler(self._abs_direct)

                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ''
                output += '<html><body>'
                output += '<h1>Previous Scan Result </h1>'
                output += '<h3><a href = "/search">Search</a></h3>'
                output += self.table_gen(self._abs_direct,self._search_date)
                output += '</body></html>'
                self.wfile.write(output.encode())

            elif self.path.endswith('.png'):
                self.send_response(200)
                self.send_header('content-type', 'image/jpeg')
                self.end_headers()
                content = open(os.path.join(self._img_path, self.path[1:]), 'rb')
                self.wfile.write(content.read())
                content.close()
        
            elif self.path.endswith('/search'):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ''
                output += '<html><body>'
                output += '<h1>Enter the date</h1>'
                output += '<form method = "POST" enctype="multipart/form-data" action="/search">'
                output += '<input name="search_date" type ="text" placeholder ="YYYY-MM-DD_hh-mm-ss">'
                output += '<input type="submit" value = "Search">'
                output += '</form>'
                output += '</body></html>'
                self.wfile.write(output.encode())
        except IOError:
            self.send_error(404)
    
    def do_POST(self):
        '''
        Handle the 'POST' request to the server
        '''
        if self.path.endswith('/search'):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if 'boundary' in pdict:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            content_len = int(self.headers.get('Content-length'))
            pdict['CONTENT-LENGTH'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                key = fields.get('search_date')
                self.__class__._search_date = key[0]

            self.send_response(301)
            self.send_header('content-type', 'text/html')
            self.send_header('Location',  '/')
            self.end_headers()

server_instance = None
server_thread = None

def my_serve_forever(http_server: HTTPServer):
    try:
        http_server.serve_forever()
    except Exception as error:
        print(error)

def start_http_server(port: int = 8080):
    global server_instance, server_thread
    if server_instance is None and server_thread is None:
        server_instance = HTTPServer(('0.0.0.0', port), MyRequestHandler)
        server_thread = Thread(target=my_serve_forever, args=(server_instance,))
        server_thread.start()

def close_http_server():
    global server_instance, server_thread
    if server_instance is not None and server_thread is not None:
        server_instance.shutdown()
        server_instance.server_close()
        server_thread.join()
        server_instance = server_thread = None

if __name__ == '__main__':
    try:
        start_http_server()
    except Exception:
        close_http_server()
