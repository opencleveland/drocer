import os
import time
import re
from io import open
from util import RecordFile, Rules

DATE_FORMAT = "%Y-%m-%d"
INVALID_VALS = ["", "\n", "Not found", {}]


class Record:

    def __init__(self, filename, **kwargs):
        self.date = filename[:filename.index('.')]
        self.year = int(self.date[0:4])
        self.f = RecordFile(self.date[0:4] + '/' + filename)

        if 'rules' in kwargs:
            self.rules = kwargs['rules']

        else:
            self.rules = Rules.create_rules('rules.txt')


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
        lines = self.f.get_lines_after("Residence", 80)

        # lines that contain the name and address, look like:
        #    Council Member Name ..................... Address
        main_lines = [line.rstrip() for line in lines if "..." in line]

        # In the case that the lines aren't in the form containing the elipses,
        # use alternative method
        if main_lines == []:
            return self.get_council_members()

        # Get the lines containing just the zip code
        # regex for five digit number followed by newline char
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

        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(cabinet)

        return cabinet


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


class RecordCollection:

    def __init__(self, **kwargs):
        self.rules = Rules.create_rules('rules.txt')

        if ('years' in kwargs):
            self.records = self.create_records_in_range(
                kwargs['years'][0], kwargs['years'][1])

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
            raw_input("Press Enter to continue...")
            year += 1


    def create_records_in_range(self, start, end):
        records = []

        for i in range(start, end):
            for f_name in sorted(os.listdir(str(i))):
                records.append(Record(f_name, rules=self.rules))

        return records


    def create_records_in_date_range(self, start, end):
        start_date = get_date(start)
        end_date = get_date(end)
        records = []

        # for all i between starting year and ending year
        for i in range(start_date.tm_year, end_date.tm_year + 1):

            # for each file in the list of files in the folder for this year
            for f_name in sorted(os.listdir(str(i))):

                # the date associated with the current file
                current_date = get_date(f_name[:f_name.index('.')])

                # check if the current date is between the start and end date
                if current_date >= start_date and current_date < end_date:
                    records.append(Record(f_name, self.rules))

        return records


    def get_all_records(self):
        records = []
        return self.create_records_in_range(1996, 2016)


def get_date(s):
    return time.strptime(s, DATE_FORMAT)


def main():

    # print an attribute (with a success rate) from each file one year at a time
    # RecordCollection.one_at_a_time('cabinet')

    # get one attribute from one file
    r = Record('1996-01-03.txt')
    mayor = r.mayor

    # TODO: Output format?

if __name__ == '__main__':
    main()
