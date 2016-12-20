#!/usr/bin/python3
"""Milestone - Split an XML document by milestone element.

This is useful for XML files containing multiple hierarchies.

Example
-------

One example is an XML dialect called TEI which might have been created
to represent a book using chapters (div elements) but you want to use
the text by page (pb element).

Imagine an XML file called myfile.xml that contains milestone
elements <pb /> dotted throughout the XML.

The following command will split the input file into separate output
files for each pb element:

    python3 milestone.py -t pb myfile.xml

The above command will name the output files with integers.

Now imagine that the <pb> elements have an attribute called 'n' that
we want to use for the name of each output file.

The following command will split the input file into separate output
files, named according to the 'n' attribute:

python3 milestone.py -t pb -n n myfile.xml

If you want to transform the hierarchy but not split the data into
separate files, you can use the -x flag

python3 milestone.py -x -t pb -n n myfile.xml > outputfile.xml

To use this as a library in your own code, import the
Milestone class.

"""

# Copyright (c) 2016, Zeth
# All rights reserved.
#
# BSD Licence
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import os
import argparse
from collections import OrderedDict
from lxml import etree

__version__ = "0.1"

CLOSING_TAG = "</%s>"
OPENING_TAG = '<%s%s>'
ATTRIBUTE = ' %s="%s"'


def main():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(
        description='Split XML at a given milestone tag.')
    parser.add_argument('-t', '--tag',
                        default='pb',
                        help='milestone tag to split input')
    parser.add_argument('-n', '--name',
                        default=None,
                        help='attribute name to use to name parts')
    parser.add_argument('-o', '--output',
                        default="output",
                        help='output directory')
    parser.add_argument('-x', '--transform',
                        action='store_true',
                        help='transform the file without splitting')
    parser.add_argument('inputfiles', nargs='*', help='Input file or files')
    args = parser.parse_args()
    if args.inputfiles:
        if not os.path.exists(args.output):
            os.mkdir(args.output)

        splitter = Milestone(args.tag,
                             args.inputfiles,
                             args.name,
                             args.output,
                             args.transform)
        result = splitter.split()
        if args.transform:
            print(result)


class Milestone(object):
    """Split files at milestone tag."""
    def __init__(self,
                 milestone,
                 input_filenames,
                 attribute_name=None,
                 output_dir="output",
                 transform_without_split=False):
        self.milestone = milestone
        self.input_filenames = input_filenames
        self.attribute_name = attribute_name
        self.transform_without_split = transform_without_split
        self.output_dir = output_dir
        self.count = 0
        self.parts = OrderedDict()

    def clear_parts(self):
        """Clear the parts dictionary.
        This resets the splitter for the next file."""
        self.parts = OrderedDict()
        self.count = 0

    def split(self):
        """Split all input files."""
        output = ""
        for filename in self.input_filenames:
            result = self.split_file(filename)
            if self.transform_without_split:
                output += result + '\n'

        if self.transform_without_split:
            return output

    @staticmethod
    def get_subdirectory_name(filename):
        """Make subdirectory name of output files."""
        endfilename = os.path.split(filename)[1]
        namepart = os.path.splitext(endfilename)[0]
        return namepart

    def split_file(self, filename):
        """Split single file."""
        self.clear_parts()
        tree = etree.parse(filename)
        milestone_tags = tree.findall('.//%s' % self.milestone)
        for milestone in milestone_tags:
            self.process_milestone(milestone)
        self.split_raw(filename)
        self.create_all_closing_tags()
        self.create_all_opening_tags()
        if self.transform_without_split:
            return self.transform()
        else:
            self.write_files(filename)

    def write_files(self, filename):
        """Write all the output files for the input file."""
        file_dir = os.path.join(self.output_dir,
                                self.get_subdirectory_name(filename))
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        for name in self.parts:
            output_file = os.path.join(file_dir, name) + '.xml'
            self.write_file(name, output_file)

    def combine_part(self, name):
        """Combine the opening, middle text and closing."""
        next_milestone_name = self.get_next_milestone_name(name)
        if next_milestone_name == -1:
            closing = ""
        else:
            closing = self.parts[next_milestone_name]['closing']

        data = self.parts[name]
        if data['text']:
            middle = data['text'] + '\n'
            if data['text'] == '\n':
                middle = '\n'
        else:
            middle = ""
        return data['opening'] + middle + closing

    def write_file(self, name, output_file):
        """Write a single file."""
        text = self.combine_part(name)
        with open(output_file, 'w') as output_fp:
            output_fp.write(text)

    def get_next_milestone_name(self, name):
        """Get next milestone_name"""
        keys = list(self.parts.keys())
        target = keys.index(name) + 1
        try:
            target_name = keys[target]
        except IndexError:
            if target == len(keys):
                return -1
            else:
                raise
        return target_name

    def get_milestone_name(self, milestone):
        """Get milestone name."""
        if not self.attribute_name:
            self.count += 1
            return str(self.count)
        name = milestone.get(self.attribute_name)
        return name

    def get_first_milestone_name(self):
        """Get the first stored milestone name."""
        return next(iter(self.parts.items()))[0]

    @staticmethod
    def get_parents(milestone):
        """Get the parent tags of the milestone."""
        return [(parent.tag, parent.attrib)
                for parent in milestone.iterancestors()]

    def process_milestone(self, milestone):
        """Process the milestone."""
        name = self.get_milestone_name(milestone)
        self.parts[name] = {'parents': self.get_parents(milestone)}

    def split_raw(self, filename):
        """Split the raw text of the file by milestone."""
        with open(filename) as text_fp:
            text = text_fp.read()
        i = 0
        self.count = 0
        milestone_next = self.get_first_milestone_name()
        done = False
        while not done:
            milestone_n = milestone_next
            try:
                index = text.index('<%s' % self.milestone)
            except ValueError:
                done = True
                index = len(text)
                total = len(text)
            else:
                end = text[index:].index('>')
                total = index + end
                element = text[index:total+1]
                milestone_next = self.get_milestone_name(
                    etree.fromstring(element))
            self.parts[milestone_n]['text'] = text[:index]
            text = text[total+1:]
            i += 1

    def create_all_closing_tags(self):
        """Create all the closing tag strings."""
        for milestone_name, data in self.parts.items():
            self.parts[milestone_name]['closing'] = \
                self.create_closing_tags(data['parents'])

    @staticmethod
    def create_closing_tags(parent):
        """Create one closing tag string."""
        closing = ""
        for tag, _ in parent:
            closing += CLOSING_TAG % tag
        return closing

    def create_all_opening_tags(self):
        """Create all the opening tag strings."""
        for milestone_name, data in self.parts.items():
            self.parts[milestone_name]['opening'] = \
                self.create_opening_tags(data['parents'])

    @staticmethod
    def create_opening_tags(parent):
        """Create one opening tag string."""
        opening = ""
        for tag, pairs in reversed(parent):
            attribute_xml = ""
            for keyvalue in pairs.items():
                attribute_xml += ATTRIBUTE % keyvalue
            attribute_xml += ATTRIBUTE % ("continued", "true")
            opening += OPENING_TAG % (tag, attribute_xml)
        return opening

    def transform(self):
        """Combine the parts back to a single XML document."""
        output = ""
        if self.attribute_name:
            attribute_name = self.attribute_name
        else:
            attribute_name = 'id'
        for name in self.parts:
            attribute = ATTRIBUTE % (attribute_name, name)
            output += OPENING_TAG % (self.milestone, attribute) + '\n'
            output += self.combine_part(name)
            output += CLOSING_TAG % self.milestone + '\n'
        return output


if __name__ == '__main__':
    main()
