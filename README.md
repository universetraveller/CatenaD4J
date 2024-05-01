# CatenaD4J
This repo contains our tool CatenaD4J (c4j) for detecting and creating indivisible bugs. We provided a dataset that can be used to evaluate existing techniques on repairing 
indivisible multi-hunk bugs.

C4j works like a plugin of other datasets and now use Defects4J as default backend because c4j contains a lot of bugs generated from defects4j. But it is easy to switch its backend or expand its commands and bugs.  
## Bugs of CatenaD4J  
CatenaD4J now contains 6 projects and 367 bugs generated from Defects4J.  

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

  It is already installed in most Linux distributions and MacOS. If you are using OS without python3, check [python official website](https://www.python.org/downloads/) for installation.
    
* Defects4J v2.0
  
  Check [defects4j](https://github.com/rjust/defects4j.git) for installation.
  
* Java 1.8
  
  Check [JDK 8](https://openjdk.org/projects/jdk8/) for installation.
  
## Set up
### Install from Dockerfile
* Ensure you have docker installed on your computer  
If you have no docker cli available, check [Install Docker Engine](https://docs.docker.com/engine/install/) for installation.  

* Check if curl is available
If you have no curl installed on your computer, check [Install curl](https://curl.se/docs/install.html) for installation.  

* Download the Dockerfile  
`curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile`  
You can also use other approaches to download the Dockerfile.  

* Build the docker image via Dockerfile
`docker build -t catena4j:main -f ./Dockerfile .`

* Create a container with CatenaD4J using the created image  
`docker run -it catena4j:main /bin/bash`

### Install step by step manually
* Ensure the softwares in the **Requirements** section are all installed.  
  
* Clone the repository
`git clone https://github.com/universetraveller/CatenaD4J.git`  

* Add executable script **catena4j** to environment variable **PATH**:  
`export PATH=$PATH:<path to this repo>`  


* Check installation:  
`catena4j pids`  

Note that the script `catena4j` assumes the command `python3` is usable otherwise you should edit the first line of the script (It points to the path of your executable python).  
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

In the future we would try to implement these commands and replace current defects4j backend with lightweight ones if possible.  

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
1. [construct\_database](scripts/construct_database) contains scripts to prepare required data for following steps.  
2. [analyze\_tests](scripts/analyze_tests) contains scripts to collect all possible identifiers of assertion statements for spliting tests.  
3. [split\_tests](scripts/split_tests) is to generate new failing tests code to make sure the failing tests contain only single assertion statement.  
4. [parse\_patches](scripts/parse_patches) is to identify hunks to fix automatically.  
5. [generate\_bugs](scripts/generate_bugs) contains an implementation of bug isolation algorithm to generate isolated bugs from existing bugs.  

## Statistics
Check [here](scripts/generate_bugs/statstics) for the statistics of current bugs

## Development Plan
The current version is available. We will try to make this dataset more concrete and add some features in the future.   

The plan of development is as below. However, because the task is time-comsuming, some updates will only be developed when we have free time. Please notice that some urgent updates (e.g. bug fixes) will be prioritized and addressed as fast as possible.  

1. An implementation of faster `test` command using the custom test runner with abort-on-failure feature that supports up to Junit5.
2. An implementation of faster `checkout` command to replace the current version (using defects4j's checkout).  
3. Adding a fast and usable code coverage tool.  
4. Adding a fast and usable spectrum-based fault localization tool.
5. Complete replacement of the defects4j backend by re-implementing all used commands.

## Publications
* Q. Xin, H. Wu, J. Tang, X. Liu, S. Reiss and J. Xuan. Towards Effective Multi-Hunk Bug Repair: Detecting, Creating, Evaluating, and Understanding Indivisible Bugs. FSE 2024.  
