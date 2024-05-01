# Detecting and Creating Indivisible Bugs
## Overview
Scripts under this folder are to detect and create indivisible bugs, convert them into patch files and generate summary for the bugs.  
The required files are also prepared and provided as the Tests Minimization Experiment because the experiment is important. Most dependent files are copied from where they are generated, some files such as `ignored_bug_ids` and `indivisible_bug_ids` are written manually, and file `res5.json` is modified (check [split\_tests](../split_tests/README.md) for reasons).  

## Usage
### Run the algorithm  
Script [runner.py](./runner.py) contains the core algorithm to detect and create indivisible bugs, you can find its usage in script [run.py](./run.py) (specifically, line 26 to 31).  

Run `python3 ./run.py [-b <bug_id>] [-n <n_jobs>] [-m <path_to_metadata_file>] [-t <path_to_minimized_tests_file>] [-p <path_to_patches_dir>]` to execute the algorithm on bug ids in file [2toMore](./2toMore). The argument `<bug_id>` is optional. When it is set, only the specified bug id will be processed.  

The output is in the directory [working](./working) including the checked out bug projects, logs, and the created bugs.  

The script is executed in parallel by default, you can specify the optional argument `<n_jobs>` to control the number of parallel tasks.  

Default argument `<path_to_metadata_file>`: `./database.json`  

Default argument `<path_to_minimized_tests_file>`: `./res5.json`  

Default argument `<path_to_patches_dir>`: `./patches`  

*Notice because of the timeout and computing in parallel, the result of bug ids reaching the timeout (caused by resource competition in parallel) may be different in multiple runs.*  

### Extract bugs for dataset
Script [export.py](./export.py) can extract bugs data from [working](./working). The extracted data includes patches for source code and tests and the metadata of the bug.  

`python3 export.py -m <mode>`  

Argument `<mode>` could be *all* or *skip_indivisible* (if the option set, originally indivisible bugs will be excluded from the generated bugs)  

The output is in the directory [export](./export) which can be copied as dataset's **projects** directory.  

### Validate the result
Script [validate.py](./validate.py) can check exceptions occur in the algorithm, and the output is written into `./validation` by which we can find if the result is expected.  

`python3 validate.py`  

### Generate the summary
Script [statstics.py](./statstics/statstics.py) can generate summary for execution of the algorithm, the result is written in `./statstics/statstics2(_<project_name>).csv` in which we can find the category, hunks number etc. of the original and created bugs.  

`cd statstics && python3 statstics.py && cd ..`  

Ensure you have finished experiment [parse\_patches](../parse_patches) before generating the summary.  

## Reproduce the experiment
The whole process takes more than 1 day (in parallel). If you choose to run in sequencial, it can take more than 20 days.   

If the environment is correctly configured, no exception occurs in the process. You can run the algorithm on a single bug id to check the configuration.  

`python3 run.py -b Lang_1`  

If the configuration is correct, at the end of the expected output is:  
```
root@container_id:~/CatenaD4J/scripts/generate_bugs# python3 run.py -b Lang_1
100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 318.14it/s]
---
Begin generate bug_id: Lang_1
num_of_hunks: 3
timeout for running: 3600
use working dir: ./working/data/Lang_1
Try to checkout Lang_1
build dir: ['target/classes', 'target/tests']
init FileManager
trace file: src/main/java/org/apache/commons/lang3/math/NumberUtils.java
trying to replace old failing tests
edit: replace from 249 range 36 at src/test/java/org/apache/commons/lang3/math/NumberUtilsTest.java
trace file: src/test/java/org/apache/commons/lang3/math/NumberUtilsTest.java
new test num: 26
ori test num: 0
pattern: 000
...
Pattern: 111
new failing tests:
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_21
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_8
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_23
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_19
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_5
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_6
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747$catena_20
Save found bug
processed: 111
Find 1 new bugs
Real time: 76.4700219631195s
```

Run `./run.sh` to reproduce the whole experiment or run scripts as the usage section to reproduce partial experiment as you like.  

## Run the algorithm on buggy projects other than 281 bugs
In theory, when **metadata**, **patch** and **minimized tests (optional)** is provided, the algorithm can be applied on the given bug project.  

The current implementation is integrated with Defects4J, so we will try to apply the algorithm on other defects4j project below.  

*Notice if you want to apply the algorithm on dataset other than defects4j, you may need to convert the related information into defects4j style.*  

For example, assume we are trying to apply the algorithm on bug id JxPath\_1.  

The following steps assuming you are in a same environment as image built from the Dockerfile (e.g. defects4j is installed in `/root`).  

1. At first, we should create database.json for it  

* Go to experiment [construct\_database](../construct_database)  
`cd ../construct_database`

* Create a bug id file contains JxPath\_1
* Run `./run.sh` with specified bug\_ids file
* Remove the temporary file  

The script check out the bug, export its metadata and convert the path in the metadata.  

```
echo "JxPath_1" > bug_id && \
./run.sh bug_id && \
rm bug_id
```

List the files in directory `./d4j_export`. The expected output is:  
```
root@container_id:~/CatenaD4J/scripts/construct_database# ls d4j_export
JxPath_1  database.json
```
2. Create a patch in json format  

* Go to experiment [parse\_patches](../parse_patches)
`cd ../parse_patches`

* Create patches for the project
```
root@container_id:~/CatenaD4J/scripts/parse_patches# python3 parse_defects4j_v2_0.py /root/defects4j JxPath
Unk type: \
Line:  No newline at end of file
...
Unk type: \
Line:  No newline at end of file
root@container_id:~/CatenaD4J/scripts/parse_patches# ls patches/JxPath/
1.json   11.json  13.json  15.json  17.json  19.json  20.json  22.json  4.json  6.json  8.json
10.json  12.json  14.json  16.json  18.json  2.json   21.json  3.json   5.json  7.json  9.json
```

3. Create minimized test

* Go to experiment [split\_tests](../split_tests)  
`cd ../split_tests`  

* Run `./run.py` on the specified bug id  
```
root@container_id:~/CatenaD4J/scripts/split_tests# rm running/res5.json
root@container_id:~/CatenaD4J/scripts/split_tests# python3 run.py -b JxPath_1 -m ../construct_database/d4j_export/database.json -w /tmp -d /root
/defects4j
100%|███████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.11it/s]
root@container_id:~/CatenaD4J/scripts/split_tests# ls running/res5.json
running/res5.json
```

4. Detect and create indivisible bug(s)  

* Go to experiment [generate\_bugs](../generate_bugs)  
`cd ../generate_bugs`

* Run `run.py` with specified arguments
```
root@container_id:~/CatenaD4J/scripts/generate_bugs# ./clean.sh
root@container_id:~/CatenaD4J/scripts/generate_bugs# python3 run.py -b JxPath_1 -m ../construct_database/d4j_export/database.json -t ../split_tests/running/res5.json -p ../parse_patches/patches
100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 466.40it/s]
---
Begin generate bug_id: JxPath_1
num_of_hunks: 2
timeout for running: 3600
use working dir: ./working/data/JxPath_1
Try to checkout JxPath_1
build dir: ['target/classes', 'target/test-classes']
init FileManager
trace file: src/java/org/apache/commons/jxpath/ri/model/dom/DOMNodePointer.java
trace file: src/java/org/apache/commons/jxpath/ri/model/jdom/JDOMNodePointer.java
trying to replace old failing tests
edit: replace from 64 range 6 at src/test/org/apache/commons/jxpath/ri/model/dom/DOMModelTest.java
edit: replace from 61 range 6 at src/test/org/apache/commons/jxpath/ri/model/jdom/JDOMModelTest.java
trace file: src/test/org/apache/commons/jxpath/ri/model/jdom/JDOMModelTest.java
trace file: src/test/org/apache/commons/jxpath/ri/model/dom/DOMModelTest.java
new test num: 8
ori test num: 0
...
used time: Finished in 2.73 seconds
Failing tests: 0
Can independently fix []
Could not fix independently
processed: 11
Find 2 new bugs
Real time: 11.183394432067871s
root@container_id:~/CatenaD4J/scripts/generate_bugs# ls working/JxPath_1/
log  newBugs.json
```

The result shows we have successfully applied the algorithm on a bug other than the 281 bugs.  
