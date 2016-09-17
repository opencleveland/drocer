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
public class CRTStripper extends PDFTextStripper {


    public CRTStripper() throws IOException {
    }

    private int pageCounter = 0;
    private int textChunksOnLine = 0;



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
        if (pageCounter == 2){
            super.setSortByPosition(false);
        }
        if (pageCounter > 2){
            super.setSortByPosition(true);
        }
    


    }

    /*
    Adds tokens within lines of the output file that will enable correct 
    reconstruction of 
    content flow, even when pages switch between single- and multi- column 
    layouts mid-flow.
    
    Overrides base-class implementation of the writeString method variant that
    uses a TextPositions param. 
    
       */
    @Override
    protected void writeString(String text, List<TextPosition> textPositions)
            throws IOException {

        if (pageCounter != 2){
        TextPosition tPos = textPositions.get(0);
        TextPosition ePos = textPositions.get(textPositions.size() - 1);
        //Pattern capNoSpace = Pattern.compile("[a-z]([A-Z])");
        String overRun = "";
        text = text.trim();
        int startPoint = Math.round(tPos.getXDirAdj());
        int endPoint = Math.round(ePos.getXDirAdj());

        int splitPoint = 0;

        double prevX = 0;


        if (textChunksOnLine > 0) {
            output.write("|");
        }

        adjustXPosOrder(textPositions, text);


        textChunksOnLine++;
        }
        else {
            output.write(text);
        }
        

    }

    @Override
    protected void writeLineSeparator() throws IOException {
        //output.write("\t[cols=" + textChunksOnLine + "]");
        output.write(getLineSeparator());
        textChunksOnLine = 0;
    }

    private void adjustXPosOrder(List<TextPosition> textPositions, String text) throws
            IOException {


        TextPosition stPos = textPositions.get(0);
        boolean inOrder = true;

        double prevX = 0;
        double prevXPos = 0;
        String overRun = "";

        int startPoint = Math.round(stPos.getXDirAdj());
        long splitPoint;
        int splitIndex = 0;

        output.write(String.valueOf(startPoint));
        output.write("\t");
        for (int i = 0; i < text.length(); i++) {

            double currXPos = textPositions.get(i).getXDirAdj();

            if (i + 1 == text.length()) {
                output.write(text);
            }


            if (currXPos < prevXPos || (prevXPos > 0 && currXPos > prevXPos + 9)) {
                //'backwards' x-axis movement (in this set of docs)
                //is assumed to indicate an 'overrun' or erroneous
                //concat
                //long x-coord gaps may also indicate erroneous concat
                //and if this over-matches 'gaps' within columns
                //that should come back out in page processing
                splitIndex = i;
                splitPoint = Math.round(currXPos);
                overRun = text.substring(splitIndex);
                text = text.substring(0, splitIndex);

                output.write(text);
                writeLineSeparator();
                inOrder = false;

                adjustXPosOrder(textPositions.subList(i, textPositions.size()),
                        overRun);

            }

            prevXPos = currXPos;

        }

    }


}
