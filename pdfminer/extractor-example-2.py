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

# define structure of output document
output_document = {
    'title': 'Cleveland City Record, April 27, 2016 ',
    'source_document_path': 'April272016.pdf',
    'pages': [],
    'text':''
}
# Open a PDF file.
fp = open(output_document['source_document_path'], 'rb')
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
    output_page = {
        'number': page_number,
        'boxes': [],
        'text': ''
    }
    interpreter.process_page(page)
    layout = device.get_result()
    print "page_number "+str(page_number)
    #print repr(layout)
    for obj in layout:
        if isinstance(obj, LTTextBox):
            output_box = {
                'x0': obj.x0,
                'y0': obj.x1,
                'x1': obj.y0,
                'y1': obj.y1,
                'text': obj.get_text().encode('utf8'), 
                'page_location': 'body'
            }
            if obj.y0 < 72 :
                output_box['page_location'] = 'footer'
            if obj.y1 > 724:
                output_box['page_location'] = 'header'
            output_page['boxes'].append(output_box)
        else:
            #print "<non-text object>"
            pass
    output_document['pages'].append(output_page)

print repr(output_document)
