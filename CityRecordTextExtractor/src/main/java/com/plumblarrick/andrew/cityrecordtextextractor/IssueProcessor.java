/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import com.plumblarrick.andrew.cityrecordtextextractor.IssueModel.Page;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;

/**
 *
 * @author calarrick
 */
public class IssueProcessor {

    String startPdfFileName;
    String firstTextFileName;
    String sortedColumnsFileName;

    public String extractIssue(String fileName, String outFileName) {

        startPdfFileName = fileName;
        firstTextFileName = outFileName;
        IssueExtractorPositional ex = new IssueExtractorPositional();

        try {
            ex.extractToFile(startPdfFileName, firstTextFileName);
            return "Extracted " + startPdfFileName + " to " + firstTextFileName;
        } catch (IOException io) {
            return "IO Exception: could not extract " + startPdfFileName;

        }
    }

    public void readLinesToPages(String fileName) throws FileNotFoundException,
            IOException {

        firstTextFileName = fileName;
        readLinesToPages();
    }

    public IssueModel readLinesToPages() throws FileNotFoundException,
            IOException {

        BufferedReader textIn = new BufferedReader(new FileReader(
                firstTextFileName), 100000);
        IssueModel currIssue = new IssueModel();
        String issueName;
        Page page = null;
        int pagesAdded = 0;
        int pageLineCounter = 0;

        String currLine = textIn.readLine();

        if (currLine.substring(0, 12).equals("Source file: ")) {
            issueName = currLine.substring(13);
        } else {
            issueName = currLine;
        }
        currIssue.setIssueID(issueName);

        while ((currLine = textIn.readLine()) != null) {

            //currLine = textIn.readLine();
            if (currLine.equals("") || currLine.equals("\n")) {
                continue;
            }

            if ((currLine.length() >= 12) && currLine.substring(0, 12).equals(
                    "[Start Page ")) {
                pagesAdded++;
                page = currIssue.addPage(pagesAdded);
                pageLineCounter = 0;
                page.setCountedPageNum(pagesAdded);
                System.out.println(pagesAdded);

            } else if (page != null) {
                pageLineCounter = page.addLine(currLine);
                System.out.println(pageLineCounter);

            } else {
                page = currIssue.addPage(pagesAdded + 1);
                page.addLine("Page missing correct starting flag.");
                pageLineCounter = page.addLine(currLine);

            }

        }
        return currIssue;
    }

    public void columnSortIssue(IssueModel issue) {

        List<Page> pages = issue.getPages();
        //replace this w iteration functionality on model

        for (Page page : pages) {
            processPage(page);
        }

    }

    public void processPage(Page page) {

        List<String> lines = page.getPageContents();
        int numColsOnLine = 0;
        //as above
        int lineCounter = 0;
        int xAxisStart = 0;
        String[] measureAndText;
        StringBuilder columnOne = new StringBuilder();
        StringBuilder columnTwo = new StringBuilder();
        StringBuilder columnThree = new StringBuilder();
        StringBuilder strays = new StringBuilder();

        switch (page.getCountedPageNum()) {

            case 0:
                break;
            case 1:
                break;
            case 2:
                break;
            case 3:
                break;
            default:
                //three column body begins
                for (String line : lines) {

                    String[] sections = line.split("\\|");
                    numColsOnLine = sections.length;
                    lineCounter++;

                    int columnOneLine = 74;
                    int columnTwoLine = 230;
                    int columnThreeLine = 380;
                    
                    if (line.equals("") || line.equals("\n")){
                        continue;
                    }

                    if (lineCounter == 1) {

                        if ((sections[0].matches("\t[0-9]{1,3}\t$"))
                                && sections.length == 3) {

                            String pNum = sections[0].substring(5);
                            page.setPageNum(Integer.parseInt(pNum));

                        }
                    }

                    //determine columns
                    for (int i = 0; i < sections.length; i++) {

                        measureAndText = sections[i].split("\t");
                        xAxisStart = Integer.parseInt(measureAndText[0]);

                        if (xAxisStart > columnOneLine * 0.8 && xAxisStart
                                < columnOneLine * 1.3) {
                            columnOne.append(measureAndText[1]);
                        } else if (xAxisStart > columnTwoLine * 0.8
                                && xAxisStart
                                < columnTwoLine * 1.3) {
                            columnTwo.append(measureAndText[1]);
                        } else if (xAxisStart > columnThreeLine * 0.8
                                && xAxisStart
                                < columnThreeLine * 1.3) {
                            columnThree.append(measureAndText[1]);
                        } else {
                            strays.append(measureAndText[0]);
                        }

                    }//end columnar for loop

                    columnOne.append("\n");
                    columnTwo.append("\n");
                    columnThree.append("\n");
                    strays.append("\n");
                    //hmmm... except don't want to append a line break
                    //if a given column got no text that cycle, right?
                    //or just as easy to take extras out later anyway?

                }
                System.out.println(columnOne.toString());
        }

    }

}
