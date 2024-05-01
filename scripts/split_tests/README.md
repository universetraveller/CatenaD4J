# Tests Minimization
## Overview
Scripts under this folder are for tests minimization process. Tests minimization is to split a test method into multiple ones. Each minimized test method contains only one assertion statement. Current approach is to isolate other assertions from the selected one (there may be better ways to do that such as modifying the junit lib so that the assertions could not throw an exception which interrupt the test execution).  

Dependent files ([2toMore](./2toMore), [database.json](./database.json) and [table](./table)) are prepared previously and provided because this experiment is important. You can also generate these files from the previous experiments (the version is identical to the generated version).  

## Usage
Script [spliter.py](./spliter.py) contains the core logic of tests minimization, and the usage can be found at the end of the script and in script [run.py](./run.py) (it is recommanded to read [spliter.py](./spliter.py) for usage).  

Script [run.py](./run.py) is to invoke the test minimization, we can run  

`python3 run.py [-d <path_to_defects4j>] [-w <path_to_bug_projects>] [-b <bug_id>] [-m <path_to_metadata_file>]`  

to execute test minimization.  

The first two arguments are optional. If they are not set, it takes default value (`/root/defects4j` and `/tmp`).  

The argument `<bug_id>` is optional. If it is set, the script only execute minimization process on the specified bug id, otherwise, the script execute minimization process on all bug ids in 2toMore.  

The argument `<path_to_metadata_file>` is optional. If it is not set, it use `./database.json` as default value.  

Example to minimize a single bug: `python3 run.py -d /root/defects4j -w /tmp -b Chart_25`  

The output is a json file `./running/res5.json` which contains information of the original and minimized tests.  

The log of execution is also generated, and written in file `./running/log5` which contains a list of test methods that the spliter could not minimize because of limitation of single file AST analysis. The unhandled test methods could be minimized via more pricise ways (e.g. using Eclipse JDT).  

Notice the output file `./running/res5.json` is not the final version, we should manually modify the name of some minimized tests because specific names may cause test failed (that is another not fixed bug of the buggy project).  

You can run `diff ./running/res5.json ../generate_bugs/res5.json` to find which test is manually modified.  

## Reproduce the experiment
The whole process takes about 5 minutes.  

If the environment is correctly configured, the output on console is a progress bar. You can also run the script on a single bug id (please refer to the usage section) to check if it works as expected.  

* Ensure you have finished experiment [construct\_database](../construct_database) so that you know where is bug projects checked out (`/tmp` by default).  

* Run `./run.sh` or `python3 run.py` directly.  
