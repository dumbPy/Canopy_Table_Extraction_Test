# Table Extraction for Canopy

## Literature
* Since PDF doesn't contain heirarchial data like table rows or columns, extracting table from the positional information if a non-trivial task.
* That said, [Anssi Nurminen Master's thesis](https://pdfs.semanticscholar.org/a9b1/67a86fb189bfcd366c3839f33f0404db9c10.pdf) gives the most extensively used table detection algorithms.
* There are two modes of detection.
1. **Lattice** in which the cells are detected using the 2D lines drawn
2. **Stream** in which the positional alignment of the words is used to associate a word/line with a perticular column and cell

* There are two popular libraries that implement these methods for python.
1. [**camelot**](https://camelot-py.readthedocs.io/) that uses [pdfminer](https://pdfminersix.readthedocs.io/en/latest/) for extracting the positional information and lines
2. [**tabula**](https://tabula-py.readthedocs.io/en/latest/) a python wrapper to tabula a java library that implements the the above algorithms

## This Solution

* This solution is driven by the example file provided and hence might not work for every possible pdf table.
* This comes down to the selection of the algo used (*Stream* since columns are space separated instead of lines) and the assumption 

### Assumptions
* The the cells are top aligned. i.e., if a cell spans 3 lines but the text is a single line, it is in the first line instead of in middle of last line. If the first like has not value, the cell is empty
* All the columns have headers (used for cleaning the extra top rows)

### Dependencies
* pandas for DataFrame
* camelot for table detection algorithm
* click for the cli interface
* dateutil for parsing dates

Install the dependencies with
```
pip install -r requirements.txt
```

### Usage
```
$ python Extract_Tables.py ./data/canopy_technical_test_input.pdf ./data
```


