FROM python:3.10-slim-bookworm

# Install dependencies and Node Version Manager (nvm)
RUN apt-get update && \
    apt-get install -y bash curl build-essential coreutils && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages"
ENV NODE_ENV=production
ENV NVM_DIR="/root/.nvm"

# Install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

WORKDIR /app

COPY ./src ./src
COPY package*.json ./
COPY package-lock.json ./
COPY .nvmrc .

# Install Node.js dependencies
RUN bash -c "source $NVM_DIR/nvm.sh --no-use && nvm install && nvm use && nvm alias default $(cat .nvmrc) && node --version"
RUN bash -c "source $NVM_DIR/nvm.sh --no-use && nvm use && npm ci --omit=dev"

# Uncomment the following line to enable agent logging
LABEL "network.forta.settings.agent-logs.enable"="true"

CMD [ "bash", "-c", "source $NVM_DIR/nvm.sh --no-use && nvm use && npm run start:prod" ]