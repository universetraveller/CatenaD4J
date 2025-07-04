FROM ubuntu:20.04
# Install Defects4J
ENV TZ=America/Los_Angeles
ENV JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
RUN \
  apt-get update -y && \
  apt-get install software-properties-common -y && \
  apt-get update -y && \
  apt-get install -y openjdk-8-jdk \
                git \
                build-essential \
				subversion \
				perl \
				curl \
				unzip \
				cpanminus \
				make \
		&& \
	ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /root
RUN git clone https://github.com/rjust/defects4j.git defects4j && \
	cd defects4j && \
	cpanm --installdeps . && \
	./init.sh

# Install CatenaD4J
WORKDIR /root
RUN git clone https://github.com/universetraveller/CatenaD4J.git

RUN cd /root/CatenaD4J/toolkit && \
	bash compile.sh && \
	cd /root

# Configure the environment variable PATH
ENV PATH="/root/defects4j/framework/bin:${PATH}:/root/CatenaD4J"
