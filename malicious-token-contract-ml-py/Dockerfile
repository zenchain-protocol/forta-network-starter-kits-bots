FROM nikolaik/python-nodejs:python3.10-nodejs20 
COPY requirements.txt ./
RUN python -m pip install --user -r requirements.txt
ARG NODE_ENV=development
# Argument to control whether to install dev dependencies
ARG INSTALL_DEV=false
ENV NODE_ENV=${NODE_ENV}
# Uncomment the following line to enable agent logging
LABEL "network.forta.settings.agent-logs.enable"="true"
WORKDIR /app
COPY ./malicious_token_model_02_07_23_exp6.joblib ./
COPY requirements.txt ./
COPY requirements_dev.txt ./
COPY ./src ./src
COPY package*.json ./
# Use the conditional logic to install dependencies
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        npm install && npm install -g nodemon; \
    else \
        npm ci --production; \
    fi
CMD [ "npm", "run", "start:prod" ]
