FROM nikolaik/python-nodejs:python3.10-nodejs20 
COPY requirements.txt ./
RUN python -m pip install --user -r requirements.txt
ENV NODE_ENV=production
# Uncomment the following line to enable agent logging
LABEL "network.forta.settings.agent-logs.enable"="true"
WORKDIR /app
COPY ./malicious_token_model_02_07_23_exp6.joblib ./
COPY ./src ./src
COPY package*.json ./
RUN npm ci --production
CMD [ "npm", "run", "start:prod" ]
