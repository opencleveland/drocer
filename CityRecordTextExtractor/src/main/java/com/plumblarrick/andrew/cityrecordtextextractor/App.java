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
public class App {
    
    
    public static void main(String[] args) throws IOException {
        
        String fileName = args[0];
        String outFileName = args[1];
        String orderedFileName = "sorted" + outFileName;
        IssueProcessor proc = new IssueProcessor();
        OutStringCleaner clean = new OutStringCleaner(orderedFileName);
        
        
        String status = proc.extractIssue(fileName, outFileName);
        System.out.println(status);
        
        
        IssueModel issue = proc.readLinesToPages();
        proc.printIssue(issue, orderedFileName);
        clean.removeProcessingTags(orderedFileName);
        
        
        
    }
    
}
