This directory contains scripts and code to run PubTator 3 normalization for Chemicals.

Chemical normalization is based on the normalization for the NLMChem tagger. 

There are two scripts, one for each file format combination.

The parameters for each script are the same:
	1. Input directory. All files within this directory will be processed, regardless of contents or file extension.
	2. Abbreviation directory. All files within this directory will be loaded as abbreviation TSV files
	3. Output directory. The is where the file output will be placed. Files with the same name as a file in the input directory will always be overwritten. All other files will be ignored.

Specifically:
	./run_Chemical_BioCXML.sh input abbr output
	./run_Chemical_PubTator.sh input abbr output

Internally the scripts use several variables:
	1. A BASE_DIR variable to reference the full path of the installation. This will need to be updated if moved or copied.
	2. A BASE_TEMP_DIR variable which specifies the full path of a directory where processes can create temporary folders. The user starting the scripts must have write access to this directory. In addition, if a process errors or is cancelled the temp folder for that process will need to be deleted manually.

Installation:
This code is tested with Python 3.9.18
The requirements.txt includes the Python packages needed

Prome integration branch
========================
The main branch preserves the original third-party mirror. Its 45 source,
configuration and documentation files were verified byte-identical to the
NLMChemTaggerNormalizer archive in https://zenodo.org/records/10839631
(archive MD5 e687bfc27848cbd1d650da85ef226897).

The prome branch keeps integration fixes and contract tests here. Dictionary
resources are installed separately at CHEM_NORM/data (a directory or symlink);
the prome branch does not track or fetch them through Git LFS.

For PubTator, run_Chemical_PubTator.sh also accepts the installation directory
as its fourth argument. Input, abbreviations and output remain the first
three arguments. TSV abbreviations are explicit and scoped to document IDs.

Run contract tests in an environment with the listed requirements:
  python -m unittest discover -s tests -v
