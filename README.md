# CatenaD4j
CatenaD4j (c4j) is a dataset aims to benchmark techniques' performance of repairing multi-hunk bugs.  

C4j works like a plugin of other datasets and now use Defects4J as default backend because c4j contains a lot of bugs generated from defects4j. But it is easy to switch its backend or expand its commands and bugs.  
## Bugs of CatenaD4j  
CatenaD4j now contains 6 projects and 367 bugs generated from Defects4J.  

- The dataset consists of original bugs that is indivisible from d4j and isolated new bugs what original bugs of d4j are divided into.

- Each bug would have its new failing tests that only contains single valid assertion statement so that techniques and debuggers cannot detect repairing effects from one failing test, and that is our real debugging scenario.

- All bugs in the dataset are isolated and minimal. We would like to name these bugs **catena bugs** that means the bugs are catenated which consist of hunks depending on each other so that only by fixing all hunks can we fix the catena bug.

- All bugs would be assigned a `catena_id (cid)`. To find a specific bug, you may use project\_name that the bug belongs to, bug\_id that indicates the source bug of this bug and the cid to recognize bugs generated from the same source bug.  

To distinguish a bug there is the tag `<bug_id><b/f><cid>`. **b/f** means the **buggy/fixed** version.  
## Active bugs  
You can check all available cids with its bug\_id in file `./projects/<project_name>/bugs-registry.csv`  

Every line in bugs-registry represents a `catena bug` and conforms to format `<project_name>, <bug_id>, <cid>, <loader>`.  

Each valid bug should have a entry in bugs-registry so that the dataset knows how to check out it.  
## Requirements
* Python3  
* Defects4J v2.0  
* Java 1.8  
## Set up
* add executable script **catena4j** to environment variable **PATH**:  
`export PATH=$PATH:<path to this repo>`  


* check installation:  
`catena4j pids`  

Note that the script `catena4j` assumes the command `python3` is usable otherwise you should edit the first line of the script to your python executable.  
## Available commands  
|Commands |Description |
|---------|------------|
|checkout |Check out the specific version of a bug|
|export   |Export specific infomation of a bug|
|reset    |Reset all unstaged modification for a working directory|
|pids     |Print available project\_names|
|bids     |Print available bug\_ids that contains at least one cid|
|cids     |Print available catena ids for a bug\_id|
|info     |Not implemented now|
|test     |Not implemented now|
|compile  |Not implemented now|
|ver      |Not implemented now|


If you try to pass not implemented commands to catena4j, the script would pass it to the backend to try to run it.  
## Usage  
* checkout bugs  
`catena4j checkout -p <project_name> -v <bug_id of defects4j><'b' or 'f'><cid of catena4j> -w <working_dir>`

example: `catena4j checkout -p Chart -v 15b1 -w ./buggy`  

* export `tests.trigger` or `classes.modified`

`catena4j export -p <property_name> -w <working_dir> -o <output_file>`

* reset working directory
  
`catena4j reset [-w <working_dir>]`

* print available ids

`catana4j pids`

`catana4j bids -p <project_name>`   

`catana4j cids -p <project_name> -b <bug_id>`  

## About Defects4J backend  
We did not fully re-implement checkout command of defects4j, so currently the default loader use defects4j to checkout original bugs. Besides we do not implement command test and compile now for defects4j supports them.   

However we note that defects4j is a complex system, and it works inefficient. Defects4J would call perl, ant, java and other commands so that it executes about n times slower than directly use these commands. It is better to re-implement defects4j's checkout, test and compile commands based on **git** and **java**.  

Future we would try to implement these commands and replace current defects4j backend with lightweight ones if possible.  

## Customization: Work with loader and command-entries  
It is easy to take control of the dataset because all components are designed as replaceable, so that you can design your own commands or change the behaviours of current commands.  

The implementation of the dataset is in folder `internal`.  

**Loaders** are the real executor of the commands, and all bugs should specify its loader in bugs-registry to load infomation for itself.  

**Command entries** are the entrances of commands. Command-line interface would find the command implementation from command-entries via command input and then pass all args to the implementation.  

By implementing custom command as python function which processes args namespace, we can add our custom function to command-entries with a command name, and then add this command name to config file, so that we can use this custom command in command line.  
### Example of custom command
Command `cids` can be an example of creating custom command. First, we implement our command `cids` in [ids.py](internal/ids.py) as `def CIDS(args)`, then we add it into [entries.py](internal/entries.py) by adding this function to `__entry_map` or using function `register_command`. Then when try to input `catena4j cids` it can print some messages.  

### Custom loader
By implementing custom loader as python class we can take control of bug loading. Add our new loader to [loaders.py](internal/loaders.py) and modify the loader specification of any bug in bugs-registry then the script would use our custom loader to load the bug.  

Every loader should implement function `load`, `fix` and `get_attr` (Arguments can refer to [default_loader](internal/default_loader.py)).  

### Default loader
Catena4J use [DefaultPathLoader](internal/default_loader.py) as default loader. It loads bugs' infomation via specific formatted paths. By creating these specific files and adding a new entry into bugs-registry assigning loader to default, we can create a new active bug.
## Reproduce experiments  
Folder `scripts` contains all experiment codes to construct this dataset.  
1. [constructDataBase](scripts/constructDataBase) contains scripts to prepare required data for following steps.  
2. [analyzeTests](scripts/analyzeTests) contains scripts to collect all possible identifiers of assertion statements for spliting tests.  
3. [splitTests](scripts/splitTests) is to generate new failing tests code to make sure the failing tests contain only single assertion statement.  
4. [parsePatches](scripts/parsePatches) is to identify hunks to fix automatically.  
5. [generateBugs](scripts/generateBugs) contains a implementation of bug isolation algorithm to generate isolated bugs from existing bugs.  

## Statistics
Check [here](scripts/generateBugs/statstics) for the statistics of current bugs
