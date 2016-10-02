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
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 *
 * @author calarrick
 */
public final class OutStringCleaner {

    String orderedFileName;
    String[] orderedFileNameSplit;

    String cleanedFileName;
    BufferedReader textIn;

    private final Pattern sortingArtifact = Pattern.compile(
            "\\[[a-z'A-Z0-9\\-\\s]+\\]");
    //above pattern will match almost any of my bracketed notes... use carefully
    private final Matcher artifactMatcher = sortingArtifact.matcher("");
    
    private final Pattern pageNumPattern = Pattern.compile("\\[Page ([0-9]+)\\]");
    private final Matcher pageMatcher = pageNumPattern.matcher("");
    

    /**
     *
     * @param fileName
     */
    public OutStringCleaner(String fileName) {

        setCleanedFileName(fileName);

    }

    public OutStringCleaner() {

    }

    private String setCleanedFileName(String fileName) {

        orderedFileNameSplit = fileName.split(".txt");
        String shortenedFileName = orderedFileNameSplit[0];
        cleanedFileName = shortenedFileName + "_clnd.txt";

        return cleanedFileName;
    }


    public void removeProcessingTags(String fileName) {

        orderedFileName = fileName;
        cleanedFileName = setCleanedFileName(fileName);
        removeProcessingTags();
    }

    public void removeProcessingTags() {

        StringBuilder cleaner = new StringBuilder();

        try {
            textIn = new BufferedReader(new FileReader(
                    orderedFileName), 98 * 1024);
        } catch (FileNotFoundException ex) {
            Logger.getLogger(OutStringCleaner.class.getName())
                    .log(Level.SEVERE, null, ex);
        }

        List<String> lines = textIn.lines().collect(Collectors.toList());
        //List<String> newLines = new ArrayList<>();

        for (String line : lines) {

            artifactMatcher.reset(line);
            pageMatcher.reset(line);
            line = line.trim();
            

            if (artifactMatcher.matches()) {
                
                if (pageMatcher.matches()){
                    
                    String pageNum = pageMatcher.group(1);
                    cleaner.append(" <");
                    cleaner.append(pageNum);
                    cleaner.append("> ");
                                        
                }
                
            } else {
                
                if ((line.endsWith(".") || line.endsWith(":"))){
                    
                    cleaner.append(line);
                    cleaner.append("\n");
                }
                
                else if (line.endsWith("-")){
                    
                    line = processHyphenation(line);
                    cleaner.append(line);
                }
                
                else if (line.contains("|")){
                    cleaner.append(line);
                    cleaner.append("\n");
                    
                }
                else {
                    line = line.concat(" ");
                    cleaner.append(line);
                }
                
            }

        }


        String cleaned = cleaner.toString();
        writeCleaned(cleaned);


    }
    
    public String processHyphenation(String line){
        
        return line;
    }

    public void writeCleaned(String cleaned) {
        try (Writer fileOut = (new BufferedWriter(
                new PrintWriter(cleanedFileName, "UTF-8")))) {

            fileOut.write(cleaned);


        } catch (IOException ex) {

        }


    }
}
