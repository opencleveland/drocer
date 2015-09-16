import re
from io import open

def reset_file_pointer(func):
    """Decorator to reset the file position before/after a method"""

    def inner(self, *args, **kwargs):
        self.f.seek(0)
        ret = func(self, *args, **kwargs)
        self.f.seek(0)
        return ret
    return inner

class RecordFile:

    """Wraps the file object and provides utility functions for the record
       class"""

    def __init__(self, path):
        self.path = path
        self.f = open(path, encoding="utf-8")


    def get_nth_line_contents(self, n):
        """Return the line contents at a given index

        Args:
                n (int): The index to get the line at

        Returns:
                str: the contents of the file at line n

        """

        return linecache.getline(self.f, n + 1)[:-1]


    @reset_file_pointer
    def get_index_of_line(self, keywords, start=0):
        """Get the index of the first line after line n containing a keyword or
           element from a list of keywords

        Args:
                keyword: A keyword or list of keywords to search for
                start: the index of the line to start searching at, default 0

        Returns:
                int: The index of the line containing the keyword or element
                     from a list of keywords
        """

        # redirect to the function that searches for multiple keywords
        if not isinstance(keywords, list):
            keywords = [keywords]

        for i, line in enumerate(self.f):
            if i > start:
                for keyword in keywords:
                    if re.search(keyword, line):
                        return i


    @reset_file_pointer
    def get_line_after(self, keyword, offset=0):
        """Get the line after the line containing a keyword

        Args:
                keyword: the term to search for
                offset: number of lines after the keyword to return the line at

        Returns:
                string: the line after the keyword at the offset indicated by
                        offset

        """

        keyword_found = False
        for i, line in enumerate(self.f, start=0):
            if keyword_found:
                if offset > 0:
                    offset -= 1
                else:
                    return line.rstrip()
            if re.search(keyword, line):
                keyword_found = True


    @reset_file_pointer
    def get_lines_after(self, keyword, n):
        """Get n lines after the line containing a keyword

        Args:
                keyword: the term to return the lines after
                n: number of lines to return

        Returns:
                list[str]: A list of length n containing the lines immediately
                           after the keyword

        """

        keyword_found = False
        result = []
        for i, line in enumerate(self.f, start=0):
            if len(result) == n:
                return result
            if keyword_found:
                result.append(line)
            if re.search(keyword, line):
                keyword_found = True


    @reset_file_pointer
    def get_line_before(self, keyword, offset=0, max_line_expected=50):
        """Get the line before the line containing keyword

        Args:
                keyword: the line to get the line before
                offset: to get the line n lines before the keyword
                max_line_expected: the max expected index of the line. In place
                                   to make sure the whole file doesn't get
                                   searched in the case that the line containing
                                   keyword doesn't exist

        Returns:
                str: the line before the line containing keyword at the given
                     offset

        """

        for i, line in enumerate(self.f, start=0):
            if re.search(keyword, line):
                return self.get_nth_line_contents(i - 1 - offset)
            if i > max_line_expected:
                return "Out of range"


    @reset_file_pointer
    def get_lines_between(self, start_keyword, end_keyword):
        """ Get the lines between the lines with the given keywords

        Args:
            start_keyword: keyword present in the line before the lines desired
            end_keyword: keyword present in the line after the lines desired

        Returns:
            list[str]: All the lines between the lines containing the keywords

        """

        start_index = self.get_index_of_line(start_keyword)
        end_index = self.get_index_of_line(end_keyword, start=start_index)
        lines = []

        for i, line in enumerate(self.f):
            if i > start_index and line != "\n":
                lines.append(line.replace(u'\u2013', '-').replace(u'\u2019', "'"))
            if i == end_index - 1:
                return lines

        return lines


class Rules:
    """A class to keep track of the Rules for getting properties of a file.

    Consider restructuring because it looks like few properties will be simple
    enough to get in the constraints of a csv

    """

    @staticmethod
    def create_rules(f):
        return Rules().get_rule_obj(open(f, encoding="utf-8").read()
            .splitlines())


    @staticmethod
    def get_rule_obj(arr):
        '''
            {
                attr1: {
                    1996: [rule1],
                    1997: [rule1, rule2],
                    1998: [rule1],
                    ...
                },
                attr2: {
                    1996: [rule1],
                    1997: [rule1, rule2],
                    1998: [rule1],
                    ...
                }

            }

        '''
        rules = {}
        for e in arr:
            a = e.split(', ')

            attr = a[0]
            years = Rules().get_years(a[1])
            r = a[2]

            if attr not in rules:
                rule = {}
                for year in range(1996, 2016):
                    rule[year] = []
                rules[attr] = rule

            for year in years:
                rules[attr][year].append(r)

        return rules


    @staticmethod
    def get_years(s):
        if Rules.is_year(s):
            return [int(s)]

        years = []

        if "<=" in s:
            start = 1996
            end = int(s[2:]) + 1

        elif "<" in s:
            start = 1996
            end = int(s[1:])

        if ">=" in s:
            start = int(s[2:])
            end = 2016

        elif ">" in s:
            start = int(s[1:]) + 1
            end = 2016

        elif len(s) == 9:
            start = int(s[:4])
            end = int(s[5:]) + 1

        for year in range(start, end):
            years.append(year)

        return years


    @staticmethod
    def is_year(s):
        try:
            s = int(s)
            if s < 2100 and s > 1900:
                return True
            return False
        except:
            return False
