# uspto_ptab
This is a set of scripts to download Patent data, munge, and load into a Solr instance.

##Processing PTAB (Patent Trial and Appeal Board Files)

###Setting up and running Tika service
1. Follow the installation instructions for the 18F document processing toolkit: (https://github.com/18F/doc_processing_toolkit) 

Once all of the installation instructions have been followed you can start the Tika service by running the following command:
```
java -jar tika-server-1.7.jar --port 9998
```

###Downloading and Processing files
In order to download zip files from the USPTO bulk data site (https://bulkdata.uspto.gov/data2/patent/trial/appeal/board/)
run the retrieval script:
```
./retrieve_ptab_files.sh
```

This script will download the zip files into the /files directory, unzip them, and send each pdf file to the Tika server to parse.  The output of this script can be found in the /logs directory.

The second script for processing reads through the resulting txt files from the previous step and combines the raw data with the XML metadata file for each
downloaded zip file into a JSON file.  In order to run this script, execute the
following:
```
python parse_xml.py
```

###Loading data into Solr
The `parse_xml.py` script referred to above will also load the resulting JSON files into Solr (unless skipping Solr processing is specified).

##Processing Office Actions
The `retrieve_oa_files.py` and `retrieve_oa_staging_files.py` files contain processes to copy, parse, combine Office Action files with PAIR data, and store the resulting JSON files in AWS S3.  These scripts are specific to two directories of Office Action files that were used for processing.

##Exctracting Public Application ID's from PAIR Bulk Data Files
The `extractpairappids.py` file is a process that uses the PAIR bulk download files from:
https://pairbulkdata.uspto.gov
This process goes through each file in the set and copies the application ID's to one file.  These application ID's are for public patent applications only.
