import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBox
#from pdfminer.utils import bbox2str
import json
import jsonpickle
import timeit

# define structure of output document
class DrocerSerializable(object):
    def serial(self):
        return self.__dict__
    @staticmethod
    def serialize(obj):
        if hasattr(obj, 'serial'):
            return obj.serial()
class DrocerDocument(DrocerSerializable):
    title = ''
    source_document_path = ''
    pages = []
    text = ''
    def __init__(self, title, source_document_path):
        self.title = title
        self.source_document_path = source_document_path
    def serial(self):
        d = self.__dict__.copy()
        d.update({'pages' : self.pages})
        return d
class DrocerPage(DrocerSerializable):
    number = 0
    boxes = []
    text = ''
    def __init__(self, number):
        self.number = number
    def serial(self):
        d = self.__dict__.copy()
        d.update({'boxes' : self.boxes})
        return d
class DrocerBox(DrocerSerializable):
    number = 0
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    text = ''
    page_location = ''
    def __init__(self, number, x0, y0, x1, y1, text, page_location=''):
        self.number = number
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text
        self.page_location = page_location
output_document = DrocerDocument(
    'Cleveland City Record, April 27, 2016 ',
    'April272016.pdf'
)
# Open a PDF file.
fp = open(output_document.source_document_path, 'rb')
# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
# Supply the password for initialization.
password = ''
document = PDFDocument(parser, password)
# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed
# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()
# Create a PDF device object.
#device = PDFDevice(rsrcmgr) # from example 1
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
# Process each page contained in the document.
page_number = 0
start_time = timeit.default_timer()
for page in PDFPage.create_pages(document):
    page_number += 1
    output_page = DrocerPage(page_number)
    interpreter.process_page(page)
    layout = device.get_result()
    elapsed = timeit.default_timer() - start_time
    print "[%s] processing page number %s" % (elapsed, page_number)
    #print repr(layout)
    box_number = 0
    for obj in layout:
        if isinstance(obj, LTTextBox):
            box_number += 1
            output_box = DrocerBox(
                box_number,
                obj.x0,
                obj.x1,
                obj.y0,
                obj.y1,
                obj.get_text().encode('utf8'), 
                'body'
            )
            if obj.y0 < 72 :
                output_box.page_location = 'footer'
            if obj.y1 > 724:
                output_boxpage_location = 'header'
            output_page.boxes.append(output_box)
        else:
            #print "<non-text object>"
            pass
    output_document.pages.append(output_page)

print json.dumps(output_document, default=DrocerSerializable.serialize)

# matching examples
import re

# match parcel numbers
for page in output_document.pages:
    for box in page.boxes:
        matcher = re.compile('([0-9]{3})-?([0-9]{2})-?([0-9]{3}[a-zA-Z]?)')
        result = matcher.search(box.text)
        if result:
            print "page: %s, box %s: %s in %s" % (page.number, box.number, result.group(0), box.text)

# match ord-res numbers
for page in output_document.pages:
    for box in page.boxes:
        matcher = re.compile('[0-9]{3}-[0-9]{2}')
        result = matcher.search(box.text)
        if result:
            print "page: %s, box %s: %s in %s" % (page.number, box.number, result.group(0), box.text)
