# Stage 1: Build the Vue application
FROM node:20-alpine as build-stage
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# Ensures .env variables point to backend if specified
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
