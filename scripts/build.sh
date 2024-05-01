if [ -z "$(docker images -q catena4j:main 2> /dev/null)" ]; then
        curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile.main
        docker build -t catena4j:main -f ./Dockerfile.main .
fi
if [ ! -f ./Dockerfile.experiments ] ; then
        curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/scripts/Dockerfile.experiments -o Dockerfile.experiments
fi
docker build -t catena4j:experiments -f ./Dockerfile.experiments .
