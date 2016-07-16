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
# import jsonpickle

# Open a PDF file.
fp = open('April272016.pdf', 'rb')
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
for page in PDFPage.create_pages(document):
    page_number += 1
    max_x = -sys.maxsize
    min_x = sys.maxsize
    max_y = -sys.maxsize
    min_y = sys.maxsize
    interpreter.process_page(page)
    layout = device.get_result()
    print "page_number "+str(page_number)
    #print repr(layout)
    for obj in layout:
        if isinstance(obj, LTTextBox):
            #print repr(obj)
            #print obj.get_text().encode('utf-8')
            x0 = obj.x0
            y0 = obj.y0
            x1 = obj.x1
            y1 = obj.y1
            if x0 < min_x:
                min_x = x0
            if y0 < min_y:
                min_y = y0;
            if x1 > max_x:
                max_x = x1
            if y1 > max_y:
                max_y = y1
            otext = obj.get_text()
            txt = otext.replace("\n"," ")
            noise = ''
            if y0 < 72 or y1 > 724: #filter headers and footers
                noise = '(noise)'
            print("    text(%d,%d;%d,%d) %d %s %s" % 
                  (
                   x0,
                   y0,
                   x1,
                   y1,
                   len(txt),
                   txt[:24],
                   noise
                  )
            ).encode('utf-8')
        else:
            #print "<non-text object>"
            pass
    print("page bounds: (%d,%d;%d,%d)" % (min_x,min_y,max_x,max_y))

