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
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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
        String pNum = "";

        String[] measureAndText;
        String text = "";
        int xAxisStart = 0;

        StringBuilder columnOne = new StringBuilder();
        StringBuilder columnTwo = new StringBuilder();
        StringBuilder columnThree = new StringBuilder();
        StringBuilder strays = new StringBuilder();
        strays.append("Couldn't place these: \n");

        Pattern firstLineIssuePagination = Pattern.compile(
                "[0-9]{1,3}\\t([0-9]{1,3})\\s*");
        Matcher pageMatcher = firstLineIssuePagination.matcher("");

        Pattern colBreak = Pattern.compile("\\|");

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

                    String[] sections = colBreak.split(line);
                    numColsOnLine = sections.length;
                    lineCounter++;
                    //remember this means lineCounter variable is one greater than 
                    //the list index through all following logic

                    int columnOneLine = 74;
                    int columnTwoLine = 230;
                    int columnThreeLine = 380;

                    if (line.equals("") || line.equals("\n") || line.equals(
                            " ")) {
                        continue;
                    }

                    if (lineCounter == 1) {

                        pageMatcher.reset(sections[0]);

                        if (sections.length == 3 && pageMatcher.matches()) {

                            pNum = pageMatcher.group(1);
                            page.setPageNum(Integer.parseInt(pNum));

                        } else if (sections.length == 3) {

                            pageMatcher.reset(sections[2]);
                            if (pageMatcher.matches()) {
                                pNum = pageMatcher.group(1);
                            }
                            page.setPageNum(Integer.parseInt(pNum));

                        }

                        page.setHeader(line);

                    } else if (lineCounter == lines.size()) {

                        pageMatcher.reset(sections[0]);

                        if (sections.length == 1 && pageMatcher.matches()) {

                            pNum = pageMatcher.group(1);
                            page.setIndexPageNum(Integer.parseInt(pNum));


                        }
                        page.setFooter(line);
                    }


                    boolean columnOnePresent = false;
                    boolean columnTwoPresent = false;
                    boolean columnThreePresent = false;
                    boolean straysPresent = false;
                    //determine columns
                    for (int i = 0; i < sections.length; i++) {

                        measureAndText = sections[i].split("\t");
                        if (measureAndText.length == 2) {
                            try {
                                xAxisStart = Integer.parseInt(measureAndText[0]);
                                text = measureAndText[1];
                            } catch (NumberFormatException e) {
                                strays.append(measureAndText[1]);
                            }
                        }


                        if (xAxisStart < columnOneLine * 2) {
                            //use this or fixed addition for expected col w?
                            //do need factor to left too to pickup mal-aligned
                            //units (probably)
                            columnOne.append(text);
                            columnOnePresent = true;
                        } else if (xAxisStart > columnTwoLine * 0.8
                                && xAxisStart
                                < columnTwoLine * 1.3) {
                            columnTwo.append(text);
                            columnTwoPresent = true;
                        } else if (xAxisStart > columnThreeLine * 0.8
                                && xAxisStart
                                < columnThreeLine * 1.3) {
                            columnThree.append(text);
                            columnThreePresent = true;
                        } else {
                            strays.append(text);
                        }


                    }//end columnar for loop

                    if (columnOnePresent) {
                        columnOne.append("\n");
                    }
                    if (columnTwoPresent) {
                        columnTwo.append("\n");
                    }
                    if (columnThreePresent) {
                        columnThree.append("\n");
                    }
                    if (straysPresent) {
                        strays.append("\n");
                    }


                }//end line iteration

                List<String> columns = new ArrayList<>();
                columns.add(columnOne.toString());
                columns.add(columnTwo.toString());
                columns.add(columnThree.toString());

                page.setColumns(columns);

                //System.out.println(columnOne.toString());
                for (String column : columns) {
                    System.out.println(column);
                }

        }
    }
}
