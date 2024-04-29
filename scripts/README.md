# Reprocuce experiments in the FSE 2024 paper
## Requirements
* pip install joblib
* pip install tqdm

## Dependencies
There are dependencies to run the experiment, and you can install them using the following ways.  
### Manually
* Install python dependencies
You can run `./install_requirements.sh` or install the dependencies using commands in the Requirement Section  

### Dockerfile
You can run `./build.sh` to build the image directly, or build as the following steps.  
1. Build the main CatenaD4J image  
`docker build -t catena4j:main -f ../Dockerfile .` or `curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile.main && docker build -t catena4j:main -f ./Dockerfile.main .`  

2. Build the image used for experiments  
`docker build -t catena4j:experiments -f ./Dockerfile .`  

3. Run a new container using the new image  
`docker run -it catena4j:experiments /bin/bash`  

## Notice
1. Bad code style and english 
When the project started I was a freshman and when the paper was accepted (2024) I am a junior student. I do agree that the experiment code written in the past year (2023) may be hard to read and bad in code style and apologize for that.  

2. The current code is highly integreted with Defects4J  
The paper says the proposed algorithms could be used in datasets other than defects4j, and that is true. However, we select to focus on 6 projects in Defects4J v2.0 due to the heavy workload, so the current implementation of algorithms is highly integrated with Defects4J (e.g. invoke defects4j's commands in the processes). Futhermore, the defects4j dataset is easy to use that has good dependencies supports and do not need to create docker containers that make the using awkward and it is outstanding in data accessibility (e.g. metadata of bugs).  
Nevertheless, defects4j is not enough for APR research, in both bugs quality and quantity. We will try to implement the algorithms on other datasets if necessary.  
