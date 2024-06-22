FROM python:3.10-slim-bookworm

# Install dependencies and Node Version Manager (nvm)
RUN apt-get update && \
    apt-get install -y bash curl build-essential coreutils && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages"
ARG NODE_ENV=development
# Argument to control whether to install dev dependencies
ARG INSTALL_DEV=false
ENV NODE_ENV=${NODE_ENV}
ENV NVM_DIR="/root/.nvm"

# Install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

WORKDIR /app

COPY ./src ./src
COPY package*.json ./
COPY package-lock.json ./
COPY requirements.txt .
COPY requirements_dev.txt .
COPY .nvmrc .

# Install Node.js dependencies
RUN bash -c "source $NVM_DIR/nvm.sh --no-use && nvm install && nvm use && nvm alias default $(cat .nvmrc) && node --version"

# Use the conditional logic to install dependencies
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        bash -c "source $NVM_DIR/nvm.sh --no-use && nvm use && npm install && npm install -g nodemon"; \
    else \
        bash -c "source $NVM_DIR/nvm.sh --no-use && nvm use && npm ci --omit=dev"; \
    fi

# Uncomment the following line to enable agent logging
LABEL "network.forta.settings.agent-logs.enable"="true"

CMD [ "bash", "-c", "source $NVM_DIR/nvm.sh --no-use && nvm use && npm run start:prod" ]