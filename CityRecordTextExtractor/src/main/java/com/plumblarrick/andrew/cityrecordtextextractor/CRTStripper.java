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

    int sumFirstColStarts = 0;
    int sumFirstColEnds = 0;
    int sumSecondColStarts = 0;
    int sumSecondColEnds = 0;
    int avgFirstColStarts = 0;
    int avgFirstColEnds = 0;
    int avgSecondColStarts = 0;
    int avgSecondColEnds = 0;
    int columnLineCounter = 0; //counts lines with at least two columns


    int temp_sumFirstColStarts = 0;
    int temp_sumFirstColEnds = 0;


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
        
        checkXPosOrder(textPositions, text);
        
        //output.write("["+ endPoint +"]");
        
        
//        output.write(startPoint + "\t" + text);


        textChunksOnLine++;

    }

    @Override
    protected void writeLineSeparator() throws IOException {
        //output.write("\t[cols=" + textChunksOnLine + "]");
        output.write(getLineSeparator());
        textChunksOnLine = 0;
    }

    private void checkXPosOrder(List<TextPosition> textPositions, String text) throws
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
            if (prevXPos  > 0 && currXPos > prevXPos + 10){
                
                splitIndex = i;
                splitPoint = Math.round(currXPos);
                overRun = text.substring(splitIndex);
                text = text.substring(0,splitIndex);
                output.write(text);
                //writeLineSeparator();
                output.write("|"+ splitPoint +"\t"+ overRun);
                inOrder = false;

                
                
                
            }
            
            if (currXPos < prevXPos) {
                splitIndex = i;
                splitPoint = Math.round(currXPos);
                overRun = text.substring(splitIndex);
                text = text.substring(0, splitIndex);

                output.write(text);
                //output.write("\n" + splitPoint + "\t" + overRun);
                writeLineSeparator();
                inOrder = false;

                checkXPosOrder(textPositions.subList(i, textPositions.size()),
                        overRun);

                //return overRun;
            }

            prevXPos = currXPos;

        }

    }


}
