/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.IOException;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

/**
 *
 * @author calarrick
 */

//OLD VERSION -- replace with CRTStripper class

public class CRTextStripper extends PDFTextStripper {


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
        sumFirstColStarts = 0;
        sumFirstColEnds = 0;
        sumSecondColStarts = 0;
        sumSecondColEnds = 0;
        avgFirstColStarts = 0;
        avgFirstColEnds = 0;
        avgSecondColStarts = 0;
        avgSecondColEnds = 0;


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


        if (textChunksOnLine == 0) {
            output.write(startPoint + "\t");

            if (avgFirstColStarts == 0) {
                temp_sumFirstColStarts = startPoint;
                temp_sumFirstColEnds = endPoint;
            } else {
                temp_sumFirstColStarts = sumFirstColStarts + startPoint;
                temp_sumFirstColEnds = sumFirstColEnds + endPoint;
            }


        } else {

            if (textChunksOnLine == 1) {

                columnLineCounter++;

                if (avgSecondColStarts == 0) {
                    avgSecondColStarts = startPoint;
                    sumSecondColStarts = startPoint;
                    avgSecondColEnds = endPoint;
                    sumSecondColEnds = endPoint;
                    sumFirstColStarts = temp_sumFirstColStarts;
                    avgFirstColStarts = temp_sumFirstColStarts;

                } else {
                    sumSecondColStarts = sumSecondColStarts + startPoint;
                    sumSecondColEnds = sumSecondColEnds + endPoint;
                    sumFirstColStarts = temp_sumFirstColStarts;
                    sumFirstColEnds = temp_sumFirstColEnds;
                    avgFirstColStarts = sumFirstColStarts / columnLineCounter;
                    avgFirstColEnds = sumFirstColEnds / columnLineCounter;
                }

                temp_sumFirstColStarts = 0;
                temp_sumFirstColEnds = 0;

            }

            output.write("|" + startPoint + "\t");
        }

        if (startPoint > endPoint) {
            //catches overrun issues in columns other than the first

            //check for beginning of overrun
            float prevXPos = 0;
            float currXPos;
            int splitIndex = 0;
            for (int i = 0; i < text.length(); i++) {

                currXPos = textPositions.get(i).getXDirAdj();
                if (currXPos < prevXPos) {
                    splitIndex = i;
                    splitPoint = Math.round(currXPos);
                    overRun = text.substring(splitIndex);
                    text = text.substring(0, splitIndex);
                    //output.write("|" + startPoint + "\t");
                    output.write(text);
                    output.write("\n" + splitPoint + "\t" + overRun);
                    writeLineSeparator();

                    break;
                }

                prevXPos = currXPos;

            }

        } 
//        else if (columnLineCounter > 1 && textChunksOnLine == 0 && endPoint
//                > avgFirstColEnds
//                && endPoint > avgSecondColEnds * .9 && endPoint
//                < avgSecondColEnds * 1.1) {
//
//            int checkPos = avgSecondColStarts + (avgSecondColEnds
//                    - avgSecondColStarts) / 3;
//            int checkIndex = -1;
//            int i = text.length()-1;
//
//            while (checkPos > avgSecondColStarts && i > 0) {
//
//                TextPosition iPos = textPositions.get(i);
//                checkIndex = i;
//                checkPos = Math.round(iPos.getXDirAdj());
//                i--;
//            }
//            if (text.charAt(checkIndex - 1) == ' ') {
//
//                overRun = text.substring(checkIndex);
//                text = text.substring(0, checkIndex - 1);
//                output.write(text);
//                output.write("\n" + checkPos + "\t" + overRun);
//                writeLineSeparator();
//
//
//            }
//
//
//        } //need to add test to catch first-column overrun
        //can't just throw out long lines or we are back
        //to problem with 'full-width' items
        //ideas might be to spot long lines that aren't near
        //any other long lines
        //and or long lines that end near where a second
        //column line should end
        //IF can target the right lines they should be 
        //unlikely to have wide, intentional, spaces
        //so might be an additoinal heuristic there for placing the actual break
        else {
            output.write(text);
        }

        // output.write("\t" + ePos.getXDirAdj());
//        if (!overRun.equals("")) {
//            //output.write(String.valueOf(splitPoint));
//            output.write("\n" + splitPoint + "\t" + overRun);
//            writeLineSeparator();
//        }
        textChunksOnLine++;

    }

    @Override
    protected void writeLineSeparator() throws IOException {
        //output.write("\t[cols=" + textChunksOnLine + "]");
        output.write(getLineSeparator());
        textChunksOnLine = 0;
    }


}
