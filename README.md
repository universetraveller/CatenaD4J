# CatenaD4j
## Set up
* add executable script 'catena4j' to environment variable 'PATH':  
`export PATH=$PATH:<path to this repo>`  
* check installation:  
`catena4j`  
## Usage  
* checkout bugs  
`catena4j checkout -p <project_name> -v <bug_id of defects4j:int><'b' or 'f'><cid of catena4j> -w <working_dir>`
* export 'tests.trigger' or 'classes.modified'  
`catena4j export -p <property_name> -w <working_dir> -o <output_file>`  
## Active bugs  
You can check all available cids with its bug_id in file './projects/<project_name>/bugs-registry.csv'  
