# uv docker image based on Debian bookworm
FROM node:24-alpine AS builder
#FROM python:3.13-slim


# make your code available within image at /app
ADD . /frontend
WORKDIR /frontend
#COPY package*.json #Line unnecessary since it's in the folder afaik
# install dependencies
RUN npm ci
# place installed packages at front of path
ENV PATH="/frontend/node_modules:$PATH"

# reset entrypoint 
ENTRYPOINT []
# expose port
EXPOSE 9000

# set env variables
# see https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
ENV DEBUG=true 

# run application
RUN npm run build
RUN npm prune --production