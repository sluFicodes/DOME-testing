FROM node:18-alpine

WORKDIR /app

COPY package.json ./
COPY server.js ./

RUN npm install

EXPOSE 4201

CMD ["node", "server.js"]
