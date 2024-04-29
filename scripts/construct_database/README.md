# Construct Database  
## Overview  
The scripts and files under this directory are to prepare data used in the later experiments.  

### File 2toMore
The file contains 281 multi-hunk bug ids used in the experiment. This file can be extracted from [parse\_patches](../parse_patches)  

### Check out projects
The script `check_out_projects.py` is to check out all specific projects used in the experiments from defects4j's database.  

### Export the projects metadata
The script `export_metadata.py` can save all properties of the bugs from defects4j's database.  

### Convert the absolute paths
The script `convert_metadata.py` can convert specific absolute paths in the file `database.json` into placeholders to make the file available on other computers and operating systems.  

## Usage
* Usage: `python3 <script> <path_to_bug_ids> <path_to_save_projects> [<path_to_defects4j>]`
* `<script>` is one of scripts in this directory.  
* Arguments:  
1. `<path_to_bug_ids>` is the path to a text file which contains bug ids to check out. Each line in the file is a bug id.  
2. `<path_to_save_projects>` is the destination to save the checked out projects. When the script is successfully executed, folders named as bug ids are created and placed in this path.  
3. `<path_to_defects4j>` is an optional argument which points to the installation path of defects4j. It is used to convert the paths in the properties.  

## Reprocuce the experiments  
The whole process may take 20 min and the expected result is the folder in the compressed file `d4j_export.tar.gz`.  

### One step script
Run `./run.sh` and the script will execute all following steps.  

### Steps
1. In the expriments we need 281 multi-hunk bugs, so we should run `python3 check_out_projects.py ./2toMore /tmp/` and then in the directory `/tmp/` we could find 281 created folders.   
2. To export all properties, we should run `python3 export_metadata.py ./2toMore /tmp/` and the script will create a folder `./d4j_export` which contains the properties and a json file `database.json` in which we can find the properties of the bugs.    
3. The `database.json` is however not the finally version, the properties extracted from defects4j command may contains absolute path, and we can run `python3 convert_metadata.py ./2toMore /tmp/ /root/defects4j` (assuming the defects4j is installed in `/root` as the Dockerfile) to convert the absolute paths into placeholders so that the later experiments can use the properties easily. Notice we assume there is no path conflict (e.g. path to replace appears in the middle of the full path).  
