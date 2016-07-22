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
        IssueProcessor proc = new IssueProcessor();
        String status = proc.extractIssue(fileName, outFileName);
        System.out.println(status);
        proc.readLinesToPages();
        
    }
    
}
