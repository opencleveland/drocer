/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.Reader;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author calarrick
 */
public class OutStringCleaner {
    
    String orderedFileName;
    String cleanedFileName;
    Reader textIn;
    
    public OutStringCleaner(String fileName){
    
    this.orderedFileName = fileName;
        cleanedFileName = orderedFileName + "_clnd";


    }
    
    public OutStringCleaner(){
        
    }
    
    public void fixWideOrds(String fileName){
        
        this.orderedFileName = fileName;
        cleanedFileName = orderedFileName + "_clnd";
        
        
        
        try {
            textIn = new BufferedReader(new FileReader(
                    orderedFileName), 100000);
        } catch (FileNotFoundException ex) {
            Logger.getLogger(OutStringCleaner.class.getName())
                    .log(Level.SEVERE, null, ex);
        }
        
        
        
        
    
        
        
    }
    
    
    
}
