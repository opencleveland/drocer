/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import java.io.IOException;

/**
 *
 * @author calarrick
 */
public class extractOne {
    
    
    
    public static void main(String[] args) {
        
        String fileName = args[0];
        IssueExtractorPositional ex = new IssueExtractorPositional();
        try{
        ex.extractToFile(fileName);
        }
        catch (IOException io){
            System.out.println("IO Exception");
            
        }
        
        
    }
    
    
    
    
}
