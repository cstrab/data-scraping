# Build stage
FROM node:14 as builder

RUN mkdir /app
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build


# Production
FROM nginx:1.16.0-alpine

RUN mkdir /app
WORKDIR /app

COPY --from=builder /app/build /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh ./
COPY .env.list ./

EXPOSE 80

# Add bash
RUN apk add --no-cache bash

# # Make our shell script executable
RUN chmod +x entrypoint.sh

# Start Nginx server
CMD ["/bin/bash", "-c", "./entrypoint.sh .env.list /usr/share/nginx/html/env.js && nginx -g \"daemon off;\""]
