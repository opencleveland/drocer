/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.plumblarrick.andrew.cityrecordtextextractor;

import com.plumblarrick.andrew.cityrecordtextextractor.IssueModel.Page;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author calarrick
 */
public class IssueModel {
    
    private List<Page> pages;
    private String issueID;

    
    public IssueModel() {
        
        pages = new ArrayList<>();
        
        
    }
    
    public List<Page> getPages() {
        return pages;
    }

    public Page addPage(int pageNum){
        
        Page page = new Page(pageNum);
        pages.add(page);
           
        
        return page;
    }
    
    public void setPages(List<Page> pages) {
        this.pages = pages;
    }

    public String getIssueID() {
        return issueID;
    }

    public void setIssueID(String issueID) {
        this.issueID = issueID;
    }
    
       
    
    public class Page {
        
        private int pageNum;
        private int countedPageNum;
        private int indexPageNum;

       
        private List<String> rawPageLines;
        private List<String> columns;
        
        public Page(int countedPageNum){
            
            this.countedPageNum = countedPageNum;
            rawPageLines = new ArrayList<>(90);
            
        }
        
        public int addLine(String line){
            
            rawPageLines.add(line);
            return rawPageLines.size();
        }

        
        public int getCountedPageNum() {
            return countedPageNum;
        }

        public void setPageNum(int pageNum) {
            this.pageNum = pageNum;
        }
        
         public void setCountedPageNum(int countedPageNum) {
            this.countedPageNum = countedPageNum;
        }

        public int getIndexPageNum() {
            return indexPageNum;
        }

        public void setIndexPageNum(int indexPageNum) {
            this.indexPageNum = indexPageNum;
        }

        public List<String> getPageContents() {
            return rawPageLines;
        }

        public void setPageLines(List<String> pageLines) {
            rawPageLines = pageLines;
        }

        
    }
    
    
    
    
}
