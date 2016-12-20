Milestone
=========

This is useful for XML files containing multiple hierarchies.

Example
-------

One example is an XML dialect called TEI which might have been created
to represent a book using chapters (div elements) but you want to use
the text by page (pb element).

Imagine an XML file called myfile.xml that contains milestone
elements <pb/> dotted throughout the XML.

The following command will split the input file into separate output
files for each pb element::

    python3 milestone.py -t pb myfile.xml

Or if you have installed the module through pip, you can use::

    python3 -m milestone -b pb myfile.xml

The above commands will name the output files with integers.

Now imagine that the <pb> elements have an attribute called 'n' that
we want to use for the name of each output file.

The following command will split the input file into separate output
files, named according to the 'n' attribute::

    python3 milestone.py -t pb -n n myfile.xml

If you want to transform the hierarchy but not split the data into
separate files, you can use the -x flag::

    python3 milestone.py -x -t pb -n n myfile.xml > outputfile.xml

To use this as a library in your own code, import the
Milestone class::

    from milestone import Milestone

To share ideas or improvements, please visit the github project at:

    https://github.com/zeth/milestone
