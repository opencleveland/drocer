import os
import time
import pprint
import re
from io import open
from util import RecordFile

DATE_FORMAT = "%Y-%m-%d"
DIR = "/"
INVALID_VALS = ["", "\n", "Not found", {}]
OUTPUT = "out/"


class Record:
    """
    #todo description of the record class
    """

    def __init__(self, filename, rules):
        """Create record class from filename and rules object"""
        self.date = filename[:filename.index('.')]
        self.year = int(self.date[0:4])
        self.f = RecordFile(DIR + self.date[0:4] + '/' + filename)
        self.rules = rules


    @property
    def mayor(self):
        return self.get_prop('mayor')


    @property
    def council_president(self):
        return self.get_prop('council_president')


    @property
    def clerk(self):
        return self.get_prop('clerk')


    @property
    def council_members(self):

        # Grab 80 lines after the line containing "Residence" as a starting pt.
        lines = self.f.get_lines_after("Residence", 80)

        # lines that contain the name and address, look like:
        #    Council Member Name ..................... Address
        main_lines = [line.rstrip() for line in lines if "..." in line]

        # Sometimes the lines don't contain elipses. If that's the case, use
        # an alternative method to get the council members
        if main_lines == []:
            return self.get_council_members()

        # Get the lines containing just the zip code
        zip_code_lines = [line.rstrip()
                          for line in lines if re.search('\d{5}\n', line)]

        # this is in the form of:
        #    {
        #        'Council member 1 name': {
        #            'address': '123 Street Address',
        #            'zipcode': '12345'
        #        },
        #        'Council member 2 name': {...
        #        },...
        #    }
        #
        # Wrong. Should be a list of people objects.
        # Position = Council member
        # Address = Address
        # Zipcode = Zipcode

        council_members = {}

        # keep track of zip codes separately in case an address is missing
        zipcode_ptr = 0

        for i in range(0, len(main_lines)):
            # name is the contents up until "..", remove whitespace with
            # rstrip()
            name = main_lines[i][:main_lines[i].index('..')].rstrip()

            # address is everything after the last index of ".."
            address = main_lines[i][main_lines[i].rfind('..') + 2:]

            # no addres --> no zipcode
            if address == "":
                zipcode = ""
            else: #most lines have zip codes
                zipcode = zip_code_lines[zipcode_ptr]
                zipcode_ptr += 1

            # create the council member
            council_members[name] = {
                'address': address,
                'zipcode': zipcode
            }

        return council_members


    def get_council_members(self):
        """Alternative method of getting the council members.

        This is for the case where there are no elipses between the name and
        address

        """

        lines = self.f.get_lines_after("Name Residence", 25)
        lines = [line.rstrip() for line in lines if line[0].isdigit()]

        council_members = {}

        for line in lines:
            line = line[2:].strip()
            if ("P.O. Box") in line:
                name = line[:line.index("P.O. Box")].rstrip()
            else:
                name = line[:re.search('\d', line).start()].rstrip()

            line = line.replace(name, "")

            zipcode = line[-5:]

            address = line.replace(zipcode, "").strip()

            council_members[name] = {
                'address': address,
                'zipcode': zipcode
            }

        return council_members


    @property
    def cabinet(self):
        lines = self.f.get_lines_between("MAYOR",
                                                   ["OFFICE OF", "DEPT.",
                                                    "Ward\n",
                                                    re.compile("\d{5}")])
        cabinet = {}

        # Some titles don't fit on their line. In this case, combine them with
        # the line above
        i = 0
        for line in lines:
            lines[i] = lines[i].strip()
            if ',' not in lines[i]:
                lines[i-1] = ' '.join(lines[i-1:i+1])
                lines.remove(lines[i])
            i += 1

        for line in lines:
            parts = [part.strip() for part in line.split(",")]

            if (u'\u2013' in parts[0] or '_' in parts[0]):
                parts[0] = "vacant"

            titles_with_commas = ["Director", "Acting Director"]
            contained = [part for part in parts if part in titles_with_commas]
            if contained != []:
                i = parts.index(contained[0])
                parts[i:i + 2] = [', '.join(parts[i:i + 2])]

            cabinet[parts[0]] = parts[1:]

        return cabinet


    @property
    def departments(self):
        # approximately the correct chunk of lines
        lines = self.f.get_lines_between("MAYOR", "MUNICIPAL COURT")

        # clean out lines before first "DEPT" and ward lines that made it into
        # the chunk of lines because of the table layout of the pdf
        lines = self.clean_dept_lines(lines)
        if (self.year == 1996):
            print (lines)

        # split into various bodies (each dept, board, or commission)
        # each body is still a list of strings after this step completes
        bodies = self.split_depts(lines)
        new_bodies = []

        # clean up each body, repeat this loop as many times as there are bodies
        # when the code reaches this line
        for body in bodies:

            # starting point
            new_body = self.create_new_body(body)

            # first line is an unusual case
            first = new_body['lines']
            if (type(first) == list):
                first = new_body["lines"][0]

            # if it starts with a room number, give the department a location
            if first[:4] == "Room":

                # Room# is either separated from the rest of the line by a
                # hyphen or a comma. Ignore if it is a part of a title
                if '-' in first and not any(t in first for t in Person.titles):
                    split_pos = first.index('-')
                else:
                    split_pos = first.index(',')

                # set the location
                new_body["location"] = first[:split_pos]

                # remove this portion of the line because it's now stored
                # elsewhere. To be extra confusing, new_body will be a list if
                # it's a dept otherwise it'll be a string
                if type(new_body) == list:
                    new_body["lines"][0] = first[split_pos + 1:].strip()
                else:
                    new_body["lines"] = first[split_pos + 1:].strip()

            else:
                new_body["location"] = ''

            new_bodies.append(new_body)

        all_bodies = {
            "departments": [],
            "boards": [],
            "commissions": []
        }

        for body in new_bodies:
            if "DEPT" in body["name"]:
                k = "departments"
            elif "BOARD" in body["name"]:
                k = "boards"
            else:
                k = "commissions"
            all_bodies[k].append(body)

        all_bodies['boards'] = self.create_boards(all_bodies["boards"])
        all_bodies['commissions'] = self.create_commissions(all_bodies["commissions"])
        all_bodies['departments'] = self.create_departments(all_bodies['departments'])

        return all_bodies

    def create_new_body(self, body):

        new_body = {
            "name" : '',
            "lines" : []
        }

        # first line looks like "NAME OF DEPT/BOARD/COMMISSION - ..."
        first_line = body[0]

        # subtitles (in parentheses) get hyphens before and after them
        # the following code gets the first hyphen if there is no subtitle and
        # the second hyphen if there is a subtitle
        hyphens = [m.start() for m in re.finditer("-", first_line)]
        split_pos = hyphens[1] if '(' in first_line else hyphens[0]

        # the name is first_line from the beginning -> split_pos
        new_body["name"] = first_line[:split_pos].strip()

        # remove the name from the first element, strip whitespace
        body[0] = first_line[split_pos + 1:].strip()

        # join the lines together for boards or commissions, these are lists of
        # names/positions where the whitespace doesn't matter
        if "DEPT" in new_body["name"]:
            new_body['lines'] = body
        else:
            new_body['lines'] = ' '.join(body)

        return new_body


    def create_departments(self, depts):

        new_depts = []

        '''
        before:
            depts is a list of basic department objects
            these look like:
            {
                name: dept name,
                location: location,
                lines: [all lines between this dept and the next]
            }

        after:
            new_depts is a list of department objects
            a department looks like:
            {
                name: dept name,
                lines: [lines that aren't part of a division],
                location: location,
                divisions: {division}
            }
        '''

        for dept in depts:
            new_dept = {
                'name': dept['name'],
                'location': '',
                'divisions': {},
                'members': []}

            if 'location' in dept:
                new_dept['location'] = dept['location']

            for i in range (0, len(dept['lines'])):
                line = dept['lines'][i]

                if Record.contains_with_spaces('OFFICES', line):
                    offices, members, leftovers = self.create_offices(dept['lines'][i:], dept['name'])
                    new_dept['offices'] = offices
                    divs, members = self.create_divisions(leftovers, dept['name'])
                    new_dept['divisions'] = divs
                    new_dept['members'] += members
                    break

                elif Record.contains_with_spaces('DIVISIONS', line):

                    divs, members = self.create_divisions(dept['lines'][i:], dept['name'])
                    new_dept['divisions'] = divs
                    new_dept['members'] = members
                    break

                else:
                    new_dept['members'].append(Person.get_people(line, department=dept['name']))

            new_depts.append(new_dept)

        return new_depts

    def clean_dept_lines(self, lines):
        # remove whitespace
        lines = [line.strip() for line in lines if line != "\n"]

        # remove lines before first "DEPT"
        i = 0
        while True:
            line = lines[i]
            if not re.search('[A-Z]{4}', line):
                lines.remove(line)
            else:
                break

        # Ward lines, if they exist
        lines = self.remove_ward_lines(lines)

        # Replace abbreviations with the full word for more consistency
        lines = self.replace_abbreviations(lines)

        return lines

    def replace_abbreviations(self, lines):
        for i in range(0, len(lines)):
            line = lines[i]
            line = line.replace("Rm.", "Room")
            line = line.replace("Sec'y.", "Secretary")
            line = line.replace("Exec.", "Executive")
            line = line.replace("Chrm.", "Chairman")
            line = line.replace("Asst.", "Assistant")
            line = line.replace("Ro om", "Room")
            line = line.replace("R oo m", "Room")
            line = line.replace("Act. Mgr.", "Account Manager")
            line = line.replace("DE PT", "DEPT")

            # two passes
            line = line.replace("_ _", "__", 10)
            line = line.replace("_ _", "__", 10)

            line = line.replace("CLEV ELA ND", "CLEVELAND")
            line = line.replace("COMMISS ION", "COMMISSION")
            lines[i] = line
        return lines

    def create_boards(self, boards):
        boards = self.clean_boards(boards)
        for board in boards:
            members = Person.get_people(board['lines'], department=board['name'])
            board['members'] = members
            del board['lines']
        return boards

    def clean_boards(self, boards):
        return boards

    def create_commissions(self, commissions):
        return self.create_boards(commissions)


    def remove_ward_lines(self, lines):

        # skip method if these lines aren't present
        if "Ward\n" not in lines:
            return lines

        i = 0
        found = False
        while True:
            line = lines[i]
            if line == "Ward\n":
                lines.remove(line)
                found = True
            elif found and re.search('\d\n', line):
                lines.remove(line)
            elif found:
                break
            else:
                i += 1
        return lines

    def split_depts(self, lines):

        depts = []
        current_dept = []
        previous = ''

        for line in lines:

            # start of a new thing -
            # "DEPT OF..." or "BOARD OF..." or "SOMETHING COMMISSION"
            # add contents of current_dept to the list of output depts
            if re.search('[A-Z]{4}', line) and current_dept != [] and \
                not Record.contains_with_spaces('DIVISIONS', line) and \
                not Record.contains_with_spaces('OFFICES', line):

                # add current_dept to list and reset current_dept/previous line
                depts.append(current_dept)
                current_dept, previous = [], ''

            # if the current line is
            if self.is_incomplete_line(line, previous):
                if self.year == 1996:
                    print (line)
                # get rid of "|||"s that are being used as spacing
                line.replace('|', '', 10)
                current_dept[-1] = ' '.join([current_dept[-1], line])

            else:
                current_dept.append(line.strip())

            previous = line.strip()

        # add the last department to the output
        depts.append(current_dept)

        return depts


    def is_incomplete_line(self, current, previous):
        """ Return whether a line in a dept/board/commission is incomplete"""

        # lines that contain "DIVISIONS" or "OFFICES" don't count
        if self.contains_with_spaces('DIVISIONS', current) or \
            self.contains_with_spaces('OFFICES', current):
            return False

        # "||||" represents spacing, formatting issue with the conversion from
        # pdf to txt
        tabbed_line = '|' in current

        # the previous line ended with a comma (and is not empty string)
        line_following_comma = previous != '' and previous[-1] == ","

        # too short to be a full line
        not_enough_words = current.count(' ') < 3 and \
                           not self.contains_with_spaces('DIVISION', current)

        # starts with numbers -> starts with an address
        # a complete line doesn't start with an address
        starts_with_digits = re.search('^(\d{3})', current)

        outlier_cases = ['Flr., Court Towers, 1200 Ontario', '',
            'Criminal Branch-Justice Center, 8th']

        return tabbed_line or line_following_comma or not_enough_words or \
            starts_with_digits or (current in outlier_cases)


    def clean_sub_depts(self, lines):

        # a set of divisions/offices looks like:
        # "DIVISIONS -" or "DIVISIONS \" or "DIVISIONS:"
        if '-' in lines[0]:
            split_char = '-'
        elif '\\' in lines[0]:
            split_char = '\\'
        else:
            split_char = ':'

        # remove "DIVISIONS" and whatever punctuation follows it
        lines[0] = lines[0][lines[0].index(split_char) + 1:].strip()

        # for some reason, the rest of the line doesn't matter if there are
        # fewer than 3 spaces. Don't remember why.
        if lines[0].count(' ') < 3:
            lines.remove(lines[0])

        lines = [line for line in lines if line != '']

        return lines


    def create_offices(self, lines, dept_name):
        offices = []
        people = []
        lines = self.clean_sub_depts(lines)

        for i in range(0, len(lines)):
            line = lines[i]

            if "DIVISIONS" in line:
                leftovers = lines[i:]
                break

            if '-' in line:
                parts = line.split('-')

            else:
                if '\\' in line:
                    split_char = '\\'
                else:
                    split_char = ','

                i = line.index(split_char)
                parts = [line[:i], line[i + 1:]]

            division = parts[0].strip()
            person = parts[1].strip()

            offices.append(division)
            people.append(Person.get_people(person, department=dept_name, division=division))

        return offices, people, leftovers

    def create_divisions(self, lines, dept_name):
        divs = []
        people = []

        lines = self.clean_sub_depts(lines)

        for line in lines:
            if '-' in line:
                parts = line.split('-')

            else:
                if '\\' in line:
                    split_char = '\\'
                else:
                    split_char = ','

                i = line.index(split_char)
                parts = [line[:i], line[i + 1:]]

            division = parts[0].strip()
            person = parts[1].strip()

            divs.append(division)
            people.append(Person.get_people(person, department=dept_name, division=division))

        return divs, people

    @staticmethod
    def contains_with_spaces(keyword, line):
        line = line.replace(' ', '')
        return keyword in line

    def get_prop(self, name):

        if len(self.rules[name][self.year]) == 1:
            return eval('self.f.' + self.rules[name][self.year][0])

        else:
            for rule in self.rules[name][self.year]:
                attempt = eval('self.f.' + rule)
                if attempt not in INVALID_VALS:
                    return attempt

        return "Not found"


    def __repr__(self):
        return "<Record, date="+self.date+">"

class Person:

    @staticmethod
    def log_person_constructor(s):
        with open("Person.txt", "a") as f:
            f.write(s + '\n')

    @staticmethod
    def log_get_people(parts, **kwargs):
        with open("GetPeople.txt", "a") as f:

            f.write("PARTS:\n")
            for part in parts:
                s = "(Single)" if Person.is_single_person(part) else "(Multiple)"
                f.write("\t" + s + ' ' + part + '\n')

            f.write('KWARGS:')
            if kwargs == {}:
                f.write('(none)')
            else:
                f.write('\n')

                for kwarg in kwargs:
                    f.write('\t' + kwarg + ': ' + kwargs[kwarg] + '\n')

            f.write('\n\n\n\n')


    suffixes = ["Jr.", "II", "III"]

    titles = ["Chairman", "Executive Director", "Director", "Vice-Chairman",
            "Chairman Ex-Officio", "Secretary", "Executive Secretary",
            "Law Director", "Utilities Director", "President of Council",
            "Councilman", "Director Secretary", "Pres. Finance Director",
            "President", "Vice President", "Member", "Assistant Secretary",
            "Vice Chairman", "Directory Secretary",
            "City Council Representative", "Alternate Member"]

    non_list_titles = ["Chairman", "Executive Director", "Director",
            "Vice-Chairman", "Chairman Ex-Officio", "Law Director",
            "Utilities Director", "President of Council",
            "Pres. Finance Director", "Director Secretary", "President",
            "Vice President", "Member", "Assistant Secretary"]

    list_titles = ["Executive Secretary", "Secretary", "Judge"]

    plural_titles = ["Councilmen"]

    plural_positions = {
        "City Council Representatives" : "City Council Representative",
        "Alternate Members" : "Alternate Member"
    }

    def __init__(self, s, **kwargs):
        Person.log_person_constructor(s)
        # properties: name, position, location

    def create_person(self, s):

        if s and s[-1] == ';':
            s = s[:-1]

        ########################################################################
        # this is for when the person starts with the title instead of the name
        for title in Person.titles:
            if s.startswith(title):
                self.position = title
                s = s.replace(title, '')
                if s.startswith(','):
                    s = s[1:]
                s = s.strip()
        # end block for if the person starts with the title instead of the name
        ########################################################################

        name, s = self.get_name(s)
        self.name = name

        if s == '':
            return

        # one more comma or semi means there is a position and location
        split_char = False
        if ';' in s:
            split_char = ';'
        elif ',' in s:
            split_char = ','

        if split_char:
            self.position = s[:s.index(split_char)].strip()
            self.location = s[s.index(split_char) + 1:].strip()

        else:
            self.position = s

        if self.position and self.position[-1] == '.':
            self.position = self.position[:-1]

    def get_name(self, s):

        split_pos = False
        s = s.strip()

        # input line looks like "Firstname Lastname, Jr., ..."
        if any(suffix in s for suffix in Person.suffixes):
            split_pos = [m.start() for m in re.finditer(r",",s)][-1]

        # input line looks like "Firstname Lastname, ..."
        elif ',' in s:
            split_pos = s.index(',')

        if split_pos:
            name = s[:split_pos]
            s = s[split_pos + 1:].strip()

        # input line line looks like "Firstname Lastname"
        else:
            name = s
            s = ''

        if "_" in name:
            name = "[vacant]"

        if name.endswith('.'):
            name = name[:-1]

        return name, s

    @staticmethod
    def is_single_person(s):
        if ',' not in s:
            return True
        if s.count(',') == 1 and any(t in s for t in Person.titles):
            return True
        if s.count(',') == 2 and any(t in s for t in Person.titles) and \
            any(suffix in s for suffix in Person.suffixes):
            return True
        return False

    @staticmethod
    def get_people(line, **kwargs):

        parts = [part.strip() for part in line.split(';')]

        Person.log_get_people(parts, **kwargs)

    @staticmethod
    def create_from_list(s, position, **kwargs):

        people = []

        # create alternate memebers list separately
        if "Alternate Members" in s:
            parts = s.split("Alternate Members")
            i = re.search(r'\w', parts[1]).start()
            people = Person.create_from_list(parts[1][i:], "Alternate Member", **kwargs)
            s = parts[0]

            if s[-2:] == ', ':
                s = s[:-2]

        # split by comma, remove whitespace
        parts = [part.strip() for part in s.split(',')]

        for part in parts:
            plural = starts_with_any(part, Person.plural_titles)

            # "Secretary" isn't a name, it is a position and often at the end
            # of a string of people indicating the secretary
            if part == "Secretary":
                people[-1].position = "Secretary"

            # handle name suffixes by adding them to the previous person
            elif part in Person.suffixes:
                people[-1].name += ", " + part

            # e.x. "J.S. Sullivan. Executive Secretary G Nina Bombelles"
            elif any(title in part for title in Person.list_titles):
                for title in Person.list_titles:
                    if title in part:
                        people.append(Person(part[:part.index(title) - 1] + ", " + position, **kwargs))
                        people.append(Person(part[part.index(title):], **kwargs))
                        break

            elif plural and 'and' in part:
                sub_parts = part.replace(plural, '').split(' and ')
                people.append(Person(sub_parts[0] + ", " + position, **kwargs))
                people.append(Person(sub_parts[1] + ", " + position, **kwargs))

            # this is an actual person to add to the list, assume their position
            # is "Member". If there's anyting more specific, it will need to be
            # implemented
            else:
                people.append(Person(part + ", " + position, **kwargs))

        return people

    @staticmethod
    def create_person_plural(s, **kwargs):
        people = []
        for title in Person.plural_titles:

            # it's already known that at least one title is present in this
            # string, otherwise we wouldn't be in this method
            if title in s:

                # title isn't important, positon is what we're looking for
                s = s.replace(title, '')

                parts = s.split(',') # 0: names, 1: position

                # this needs to be redone if there can be more than two
                names = [part.strip() for part in parts[0].split('and')]

                # get the individual position associated with the plural
                # position given by the string
                position = Person.plural_positions[parts[1].strip()]

                # create a person for each name in the list
                for name in names:
                    people.append(Person(name + ', ' + position, **kwargs))

        return people


    def to_json(self):
        return self.__dict__


    def __repr__(self):
        ''' Debug repr
        return \
            '\n\tname="' + self.name + '"'\
            '\n\tposition="' + self.position + '"' + \
            '\n\tlocation="' + self.location + '"' + \
            '\n\tdepartment="' + self.department + '"' + \
            '\n\tdivision="' + self.division + '"'
        '''

        return 'Person[name=' + self.name + ']'


class RecordCollection:

    def __init__(self, **kwargs):
        self.rules = Rules.create_rules('rules')

        if ('years' in kwargs):
            self.records = self.create_records_in_range(
                kwargs['years'][0], kwargs['years'][1])

        elif ('variety_pack' in kwargs):
            self.records = self.one_of_each()

        else:
            self.records = self.get_all_records()


    def get_with_success_rate(self, attr):
        vals = []
        for record in self.records:
            vals.append((record.date, getattr(record, attr)))

        total = len(vals)
        invalid = sum(val[1] in INVALID_VALS for val in vals)

        if total == 0:
            return "Did not find any of prop: [" + attr + """] or records was
                    empty"""

        print ("Getting property: " + attr + """\n\trecords searched:
               {0}\n\tattr found in: {1}\n\tsuccess rate: {2:.2%}""".format(
                total, total - invalid, float(total - invalid)/total))

        if invalid > 0:
            print ("\nattr not found in:")

            for val in vals:
                if val[1] in INVALID_VALS:
                    print ("\t" + val[0] + " , result: " + str(val[1]))


    @staticmethod
    def one_at_a_time(attr):
        """ Get the given attribute for each record in a year and print the success
        rate"""

        year = 1996 # start at 1996
        while (year <= 2015):
            print ("Year = " + str(year))
            r = RecordCollection(years=(year, year + 1))
            r.get_with_success_rate(attr)
            input("Press Enter to continue...")
            year += 1


    def one_of_each(self):
        records = []

        for i in range(1996, 2016):
            for f_name in sorted(os.listdir('drocer/' + str(i))):
                records.append(Record(f_name, self.rules))
                break

        return records


    def create_records_in_range(self, start, end):
        records = []

        for i in range(start, end):
            for f_name in sorted(os.listdir('drocer/' + str(i))):
                records.append(Record(f_name, self.rules))

        return records


    def create_records_in_date_range(self, start, end):
        start_date = get_date(start)
        end_date = get_date(end)
        records = []

        # for all i between starting year and ending year
        for i in range(start_date.tm_year, end_date.tm_year + 1):

            # for each file in the list of files in the folder for this year
            for f_name in sorted(os.listdir(DIR + str(i))):

                # the date associated with the current file
                current_date = get_date(f_name[:f_name.index('.')])

                # check if the current date is between the start and end date
                if current_date >= start_date and current_date < end_date:
                    records.append(Record(f_name, self.rules))

        return records


    def get_all_records(self):
        records = []
        return self.create_records_in_range(1996, 2016)



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

        if len(s) == 9:
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


def get_date(s):
    return time.strptime(s, DATE_FORMAT)


def elements_found_in_string(l, s):
    count = 0
    for e in l:
        if e in l:
            count += 1
    return count


def starts_with_any(s, lst):
    for e in lst:
        if s.startswith(e):
            return e

def main():

    # get an attribute (with a success rate) for one year at a time
    # one_at_a_time('cabinet')

    # RecordCollection.one_at_a_time('departments')
    try:
        os.remove('GetPeople.txt')
    except OSError:
        pass

    records = RecordCollection(variety_pack=True).records
    for r in records:
        depts = r.departments

if __name__ == '__main__':
    main()

'''

TODO

- write function to validate where the data is off and give me the name of the
    department (and the file name) where the error is present '''
