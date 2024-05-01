# Parse Defects4J Patches
## Overview
The scripts convert patches (reversed diff patch) from d4j's database into a json file containing information of each hunk from the original patch.  

## Usage  
### Validate patch files
Script [validate.py](./validate.py) checks if the patch file is in `git diff` format and whether the encoding of the it is correct.  
`python3 validate.py [<path_to_defects4j>]`  

The expected output is as below:  
```
root@container_id:~/CatenaD4J/scripts/parse_patches# python3 validate.py /root/defects4j
Chart_7
Decode error, utf-8, /root/defects4j/framework/projects/Lang/patches/25.src.patch
```

### Parser of the patches
Script [parser\_defects4j.py](./parser_defects4j.py) is used to parse the patch files from defects4j. It finds every continuous diff block and converts the diff block into a file edit object which is called hunk in the experiments.  

Usage can be found at the end of the script.  
```
path_to_the_patch = '/root/defects4j/framework/projects/Chart/patches/1.src.patch'
parser = Parser(path_to_the_patch)
parser.parse()
print(parser.dump_d4j_patch())
```

### Parse patches from defectsj v2.0
Script [parse\_defects4j\_v2\_0.py](./parse_defects4j_v2_0.py) is used to generate hunks information for defects4j bug projects.  
`python3 parse_defects4j_v2_0.py [<path_to_defects4j>] [<project_name>]`  

The output is a directory `./pacthes` which contains the generated hunks information.  

Furthermore, the script will analyze the process and generate a file `./analysis` which contains a summary of the generated hunks information.  

### Generate hunks information without comments and blank lines
If the patch is as the following block:  
```
+ for(int a = (int)(-100 + Math.random() * 200);;) {
+     if (a == 1) break;
      // comment
+     else if (a > 1) a --;

+     else a ++;
+ }
```
It will be considered as 3 hunks. However actually we know they are in a single hunk in logic, so we have script `convert_patches.py` to add the actual hunks number to the hunks information.  

`python3 convert_patches.py [<path_of_bug_projects>] [<project_name>] [<path_of_hunks_information>]`  

The first argument is the path of checked out bug projects, and each bug project should be named as its bug id.  

The output is as the content of file `./convert_log` (it is redirected from console output).  

The script does not overwrite the original hunks information. It creates a new directory `./pacthes_ci` to save the result.  

## Reproduce the experiments
Run `./run.sh` or execute the scripts as the usage.  

