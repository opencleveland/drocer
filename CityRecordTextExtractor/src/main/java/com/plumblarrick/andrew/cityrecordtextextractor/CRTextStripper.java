/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.IOException;
import java.util.List;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

/**
 *
 * @author calarrick
 */
public class CRTextStripper extends PDFTextStripper{
    
    
    private int pageCounter = 0;
    private int textChunksOnLine = 0;
    
    public CRTextStripper() throws IOException {
}
    //no call to super b/c PDFTextStripper is invoked with noarg constructor
    
    

    /* 
    In base class startPage doesn't do anything. Here implementation adds
    a harder human-readable page divider
    
    */
    @Override
    protected void startPage(PDPage page)
                  throws IOException {
        
        pageCounter++;
        output.write("\n\n[Start Page " + pageCounter + " ]\n");
        textChunksOnLine = 0;
    }
    
    /*
    Adds tokens within lines of the output file that will enable correct 
    reconstruction of 
    content flow, even when pages switch between single- and multi- column 
    layouts mid-flow.
    
    Overrides 'empty' base-class implementation of the writeString method with
    the List<TextPosition> parameter. Writes the first x-axis position in the list 
    (that of the first character in what PDFBox has already assembled into a 
    line-level String) before calling the basic one-parameter method.
    
    Added counter variable to indicate how many 'columns' appear in the line. This 
    is to assist in downstream calculation of the typical per-page column layout.
    */
    @Override
    protected void writeString(String text, List<TextPosition> textPositions) 
            throws IOException {
        
        TextPosition tPos = textPositions.get(0);
        int startPoint = 0;
        
        if (textChunksOnLine == 0){
            startPoint = Math.round(tPos.getXDirAdj());
            output.write(startPoint + "\t");
        }
        else {
            startPoint = Math.round(tPos.getXDirAdj());
            output.write("|" + startPoint + "\t");
        }
        output.write(text);
        textChunksOnLine++;
        
    }
    
    @Override
    protected void writeLineSeparator() throws IOException
    {
        //output.write("\t[cols=" + textChunksOnLine + "]");
        output.write(getLineSeparator());
        textChunksOnLine = 0;
    }
    
    
    
    
    
    
}
