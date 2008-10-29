import xml.sax, re, sys
import importer
from gourmet.gdebug import *
from gourmet.gglobals import *

class RecHandler (xml.sax.ContentHandler, importer.importer):
    def __init__ (self, recData, total=None, prog=None, conv=None):
        self.elbuf = ""
        xml.sax.ContentHandler.__init__(self)
        importer.importer.__init__(self,rd=recData,total=total,prog=prog,threaded=True,
                                   do_markup=False, conv=conv)

    def characters (self, ch):
        self.elbuf += ch

class converter:
    def __init__ (self, filename, rd, recHandler, recMarker=None, threaded=False, progress=None,
                  conv=None):

        """Initialize an XML converter which will use recHandler to parse data.
        
        filename - our file to parse (or the name of the file).

        rd - our recdata object.

        recHandler - our recHandler class.

        recMarker - a string that identifies a recipe, so we can
        quickly count total recipes and update users as to progress)
        and our recHandler class.

        We expect subclasses effectively to call as as we are with
        their own recHandlers.
        """

        self.rd = rd
        self.recMarker=recMarker
        self.fn = filename
        self.threaded = threaded
        self.progress = progress
        self.rh = recHandler(recData=self.rd,prog=self.progress,conv=conv)
        self.added_ings = self.rh.added_ings
        self.added_recs = self.rh.added_recs
        self.terminate = self.rh.terminate
        self.suspend = self.rh.suspend
        self.resume = self.rh.resume
        if not self.threaded: self.run()

    def run (self):
        # count the recipes in the file        
        t = TimeAction("rxml_to_metakit.run counting lines",0)
        if type(self.fn)==str:
            f=file(self.fn,'rb')
        else:
            f=self.fn
        recs = 0
        for l in f.readlines():
            if l.find(self.recMarker) >= 0: recs += 1
        f.close()
        t.end()
        self.rh.total=recs
        self.parse = xml.sax.parse(self.fn, self.rh)
        importer.importer._run_cleanup_(self.rh)
        