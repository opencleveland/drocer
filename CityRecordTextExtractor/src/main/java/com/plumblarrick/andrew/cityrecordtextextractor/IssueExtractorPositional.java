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

    String fileName = "";

    public IssueExtractorPositional(String fileName) {

        this.fileName = fileName;

    }
    public IssueExtractorPositional(){
        
    }

    PDDocument document = null;

    public void extractToFile(String fileName) throws IOException {

        this.fileName = fileName;
        try {
            document = PDDocument.load(new File(fileName));

            PDFTextStripper stripper = new CRTextStripper();
            stripper.setSortByPosition(true);
            stripper.setStartPage(0);
            stripper.setEndPage(document.getNumberOfPages());
            
            Writer fileOut = new PrintWriter(new BufferedWriter(new PrintWriter("test.txt", "UTF-8")));

            fileOut.write("Source file: " + fileName + "\n");
            stripper.writeText(document, fileOut);
            
        } finally {
            if (document != null) {
                document.close();
            }
        }
    }
}
