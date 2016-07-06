'''
Created on Apr 21, 2016

@author: Andrew
'''
# import re

def process_issue(iss_file_name):
    issue_string = getissue(iss_file_name)
    issue_sectioner(issue_string)
    

def getissue(iss_file_name):
    f = open(iss_file_name, encoding="utf8")
    return f.read()
 
    

# this is hard-coded to the patterns of the ord/res sections. This type of line-by-line routine could 
# also probably be parameterized to work for other sections/elements of the Record

def issue_sectioner(issue_string):
    line_list = issue_string.splitlines()
    
    # have regex that can locate page numbering (both kinds) but needs to work across lines (not split)
    # am pondering way to tag lines with pagination information before split, then 
    # pull page no info out of existing line-by-line loop below
    council_readings_section = ""
    council_readings_section_flag = False
    enacted_ords_res_flag = False
    enacted_ords_section = ""
    # header_line = re.compile("^([A-Z\s]+)") was too easy for this regex to grab non-headers
    # so will need other way to find end of last ord
    # section_start_index = 0
    
    
    
    for index, line in enumerate(line_list):
        
        #target_header = False
        #header_line_match = header_line.fullmatch(line)
        
        if line.startswith(("FIRST READING", "SECOND READING", "THIRD READING")) and index < len(line_list)-1:
            council_readings_section_flag = True
            # header_line_match = False
            section_header = line + " " + line_list[index+1]
            if not line_list[index+2].startswith(("Ord. No.", "Res. No.")):
                section_header = section_header + " " + line_list[index+2]
                #these headers can be two or three lines long
            continue 
            
        if line.startswith("THE CALENDAR"):
            council_readings_section_flag = False
        
        if council_readings_section_flag:
            if line.startswith(("Ord. No.", "Res. No.")):
                council_readings_section = (council_readings_section + "\nSection: " + section_header + "\nCitation: " 
                + line + "\nText: " + line + " ")
            else:
                council_readings_section = council_readings_section + " " + line
                     
        if line.startswith(("ADOPTED RESOLUTIONS", "ADOPTED ORDINANCES")) and index < len(line_list)-1:
            enacted_ords_res_flag = True
            #target_header = True
            section_header = line + " " + line_list[index+1]
            #section_start_index = index
            index +=1
            continue
        
        if enacted_ords_res_flag:
            if line.startswith(("Ord. No.", "Res. No.")):
                enacted_ords_section = (enacted_ords_section + "\nSection: " + section_header + "\nCitation: " 
                + line + "\nText: " + line + " ")
            else:
                enacted_ords_section = enacted_ords_section + " " + line     
            
            if line.startswith(("Effective ", "Awaiting ")) and line_list[index-1].startswith("Passed"):
                # finds end of last ordinance/res in section by "brute force" look forward
                # sufficient lines to feel confident that we are out of range for another 'ord. no.' section
                # to start
                is_next = False
                # enacted_ords_section = enacted_ords_section + " " + line_list[index+1]
                for i in range (1,9):
                    if line_list[index+i].startswith(("Ord. No.", "Res. No.")):
                        is_next = True
                if is_next == False:
                    enacted_ords_res_flag = False 
        
        
        
        
        
    # using print to standard output as place-holder. need determine how we want these (output a tokenized file of JSON
    # objects for each Res/Ord appearance? Write to XML? Need semi-working idea of schema to move forward with either)    
        
    print (council_readings_section)
    print (enacted_ords_section)



if __name__ == '__main__':
    import sys
    process_issue(sys.argv[1])
    

