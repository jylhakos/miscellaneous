

FROM hyperledger/sawtooth-shell:1.0

# Install Python, Node.js, and Ubuntu dependencies
RUN echo "deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe" >> /etc/apt/sources.list \
  && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD \
  && apt-get update \
  && apt-get install -y -q \
    apt-transport-https \
    build-essential \
    ca-certificates \
    curl \
    libzmq3-dev \
    pkg-config \
    python3 \
    python3-colorlog \
    python3-dev \
    python3-grpcio-tools=1.1.3-1 \
    python3-grpcio=1.1.3-1 \
    python3-nose2 \
    python3-pip \
    python3-protobuf \
    python3-pytest-runner=2.6.2-1 \
    python3-pytest=2.9.0-1 \
    python3-sawtooth-sdk \
    python3-sawtooth-signing \
    python3-setuptools-scm=1.15.0-1 \
    python3-yaml \
    software-properties-common \
  && curl -s -S -o /tmp/setup-node.sh https://deb.nodesource.com/setup_8.x \
  && chmod 755 /tmp/setup-node.sh \
  && /tmp/setup-node.sh \
  && apt-get install nodejs -y -q \
  && rm /tmp/setup-node.sh \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && npm install -g prebuild-install \
  && npm install -g protobufjs \
  && npm install -g webpack \
  && npm install -g webpack-dev-server

WORKDIR /sawtooth-supply-chain

# Install NPM dependencies to central location, link to individual components
COPY bin/splice_json bin/
COPY demo_client/package.json demo_client/
COPY server/package.json server/

RUN mkdir /node_deps \
  && bin/splice_json \
    demo_client/package.json \
    server/package.json \
    > /node_deps/package.json \
  && cd /node_deps && npm install && cd - \
  && ln -s /node_deps/node_modules demo_client/ \
  && ln -s /node_deps/node_modules server/

ENV PATH $PATH:/sawtooth-supply-chain/bin

CMD ["tail", "-f", "/dev/null"]
