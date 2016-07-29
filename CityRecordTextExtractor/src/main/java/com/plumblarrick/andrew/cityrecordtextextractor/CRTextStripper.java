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
public class CRTextStripper extends PDFTextStripper {


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
        TextPosition ePos = textPositions.get(textPositions.size() - 1);
        //Pattern capNoSpace = Pattern.compile("[a-z]([A-Z])");
        String overRun = "";
        text = text.trim();

       
        int startPoint = Math.round(tPos.getXDirAdj());
        int endPoint = Math.round(ePos.getXDirAdj());
        int splitPoint = 0;

        if (textChunksOnLine == 0) {
            output.write(startPoint + "\t");
        } else {
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
                
        

            

        }//need to add test to catch first-column overrun
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
