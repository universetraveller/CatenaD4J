curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile.main
docker build -t catena4j:main -f ./Dockerfile.main .
docker build -t catena4j:experiments -f ./Dockerfile.experiments .
