/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Writer;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

/**
 *
 * @author calarrick
 */
public class IssueExtractorPositional {

    String inFileName = "";
    String outFileName = "";
    PDDocument document = null;
    Writer fileOut;

    public IssueExtractorPositional(String fileName, String outFileName) {

        this.inFileName = fileName;
        this.outFileName = outFileName;

    }
    public IssueExtractorPositional(){
        
    }

    public void extractToFile(String inFileName, String outFileName) throws IOException {

        this.inFileName = inFileName;
        this.outFileName = outFileName;
        try {
            document = PDDocument.load(new File(inFileName));

            PDFTextStripper stripper = new CRTextStripper();
            stripper.setSortByPosition(true);
            stripper.setStartPage(0);
            stripper.setEndPage(document.getNumberOfPages());
            
            
            fileOut = (new BufferedWriter(new PrintWriter(outFileName, "UTF-8")));

            fileOut.write("Source file: " + inFileName + "\n");
            stripper.writeText(document, fileOut);
            
        } finally {
            if (document != null) {
                document.close();
                fileOut.flush();
                fileOut.close();
            }
        }
    }
}
