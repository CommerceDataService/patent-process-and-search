# uspto_ptab
This is a set of scripts to download Patent Trials and Appeals Board data, munge, and load into a Solr instance.

# Setting up and running Tika service
Follow the installation instructions for the 18F document processing toolkit: (https://github.com/18F/doc_processing_toolkit) 

Once all of the installation instructions have been followed you can start the Tika service by running the following:
    java -jar tika-server-1.7.jar --port 9998

#Downloading and Processing files
In order to download zip files from the USPTO bulk data site (https://bulkdata.uspto.gov/data2/patent/trial/appeal/board/)
run the retrieval script:
    ./retrieval_files.sh
This script will download the zip files into the /files directory, unzip them, and send each pdf file to the Tika server to parse.
  The output of this script can be found in the /logs directory.

The second script for processing reads through the resulting txt files from the previous step and combines the raw data with the XML metadata file for each
downloaded zip file into a JSON file.  In order to run this script, execute the
following:
    ./parsexml.py

#Loading data into Solr
