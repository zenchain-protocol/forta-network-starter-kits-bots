FROM nikolaik/python-nodejs:python3.10-nodejs20

# Define build-time arguments
#ARG CHAIN_ID
#ARG EVM_RPC
#ARG STORAGE_API_URL
#ARG NODE_ENV

# Set environment variables in the container
ENV CHAIN_ID=8408
ENV EVM_RPC=https://zenchain-testnet.api.onfinality.io/public
ENV STORAGE_API_URL=https://forta-storage.vercel.app
ENV NODE_ENV=production

COPY requirements.txt ./
RUN python -m pip install --user -r requirements.txt
# Argument to control whether to install dev dependencies
ARG INSTALL_DEV=false
# Uncomment the following line to enable agent logging
LABEL "network.forta.settings.agent-logs.enable"="true"
WORKDIR /app
COPY ./malicious_token_model_02_07_23_exp6.joblib ./
COPY requirements.txt ./
#COPY requirements_dev.txt ./
COPY ./src ./src
COPY package*.json ./
# Use the conditional logic to install dependencies
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        npm install && npm install -g nodemon; \
    else \
        npm ci --production; \
    fi
CMD [ "npm", "run", "start:prod" ]
