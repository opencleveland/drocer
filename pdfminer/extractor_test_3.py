'''
Created on Jul 15, 2016

@author: calarrick
'''

if __name__ == '__main__':
    pass



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
from pdfminer.converter import XMLConverter
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
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

#LAParams is where you can alter the parameters documented for the command line interface
#char-margin, line-margin, word-margin, etc
#but hasn't helped where parser simply seems to be misunderstanding placement of certain characters

fText = open('April272016.xml', 'w')
device = XMLConverter(rsrcmgr, fText, laparams=laparams)

#switched to XMLConverter for converter that recurses deeper, to get indiv. char. info
#could have written own class extending PDFPageAggregator instead but wanted quick test
# device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
# Process each page contained in the document.



page_number = 0
for page in PDFPage.create_pages(document):
    page_number += 1
    #max_x = -sys.maxsize
    #min_x = sys.maxsize
    #max_y = -sys.maxsize
    #min_y = sys.maxsize
    interpreter.process_page(page)
    # layout = device.get_result()
    #print "page_number "+str(page_number)
    #print repr(layout)
    
    
    #print("page bounds: (%d,%d;%d,%d)" % (min_x,min_y,max_x,max_y))
    fText.flush()
fText.close()

