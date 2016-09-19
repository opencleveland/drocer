/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Writer;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author calarrick
 */
public class OutCleaner {

    String orderedFileName = "";
    String cleanedFileName; 
    String cleanedText;
    

    public OutCleaner(String orderedFileName) {

        this.orderedFileName = orderedFileName;
        cleanedFileName = orderedFileName + "_clnd";

    }

    public OutCleaner() {

    }
    
    

    public void cleanUpFullWidth(String orderedFileName) throws
            FileNotFoundException, IOException {
        
        this.orderedFileName = orderedFileName;
        cleanedFileName = orderedFileName + "_clnd";


        BufferedReader textIn = new BufferedReader(new FileReader(
                orderedFileName), 100000);

        //Boolean seekingWideLines = false;
        Boolean seekingEndCol = false;
        Writer fileOut = (new BufferedWriter(new PrintWriter(cleanedFileName, "UTF-8")));


        //look for Ord starting in col. one w/ mulitple long lines followed by 
        //an 'end column ne' 
        //if found, move it to the very end of the page (as if it were the end of
        //col. three not of col. one
        
        StringBuilder rejiggered = new StringBuilder();
        
        StringBuilder textToMove = new StringBuilder();
        Boolean holdingTextToMove = false;
        String line = textIn.readLine();
        while ((line = textIn.readLine()) != null){

        if (line.startsWith("Ord. No. ")) {

            textIn.mark(2000);
            //seekingWideLines = true;
            seekingEndCol = true;
            int i = 0;
            int longCount = 0;
            int shortCount = 0;

            while (seekingEndCol && i <= 15) {

                String testLine = textIn.readLine();
                if (testLine.startsWith("[End C")){
                    seekingEndCol = false;
                }
                if (testLine.length() > 65) {
                    longCount++;
                } else {
                    shortCount++;
                }
            }
            if (shortCount < longCount){
                
                textIn.reset();
                holdingTextToMove = true;
                
                
                while (!line.startsWith("[End C")){
                    
                    textToMove.append(line);
                    textToMove.append("\n");
                    
                }
                
                
            }
            else {
                textIn.reset();
                rejiggered.append(line);
            }

        }
        
        else if (holdingTextToMove && line.startsWith("[End P")){
            
            rejiggered.append("['Wide' text moved to fix flow across pages/columns] ");
            rejiggered.append(textToMove.toString());
            rejiggered.append(line);
            textToMove.delete(0, textToMove.length());
            holdingTextToMove = false;
            
            
        }
        
        else {
            rejiggered.append(line);
            rejiggered.append("\n");
        }
        line = textIn.readLine();
        }
        
        cleanedText = rejiggered.toString();
        fileOut.append(cleanedText);
        fileOut.flush();
        fileOut.close();
        
        
    }

}
