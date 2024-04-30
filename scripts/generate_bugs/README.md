# Detecting and Creating Indivisible Bugs
## Overview
Scripts under this folder are to detect and create indivisible bugs, convert them into patch files and generate summary for the bugs.  
The required files are also prepared and provided as the Tests Minimization Experiment because the experiment is important. Most dependent files are copied from where they are generated, some files such as `ignored_bug_ids` is written manually, and file `res5.json` is modified (check [split\_tests](../split_tests/README.md) for reasons).  

## Usage
### Run the algorithm  
Script [runner.py](./runner.py) contains the core algorithm to detect and create indivisible bugs, you can find its usage in script [run.py](./run.py) (specifically, line 26 to 31).  

Run `python3 ./run.py [-b <bug_id>] [-n <n_jobs>]` to execute the algorithm on bug ids in file [2toMore](./2toMore). The argument `<bug_id>` is optional. When it is set, only the specified bug id will be processed.  

The output is in the directory [working](./working) including the checked out bug projects, logs, and the created bugs.  

The script is executed in parallel by default, you can specify the optional argument `<n_jobs>` to control the number of parallel tasks.  

Notice because of the timeout and computing in parallel, the result of bug ids reaching the timeout (caused by resource competition in parallel) may be different in multiple runs.  

### Extract bugs for dataset
Script [export.py](./export.py) can extract bugs data from [working](./working). The extracted data includes patches for source code and tests and the metadata of the bug.  

`python3 export.py -m <mode>`  

Argument `<mode>` could be *all* or *skip_indivisible* (if the option set, originally indivisible bugs will be excluded from the generated bugs)  

The output is in the directory [export](./export) which can be copied as dataset's **projects** directory.  

### Validate the result
Script [validate.py](./validate.py) can check exceptions occur in the algorithm, and the output is wriiten into `./validation` by which we can find if the result is expected.  

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
root@container_id:~/scripts/generate_bugs# python3 run.py -b Lang_1
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
