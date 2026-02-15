# Stage 1: build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
ARG VITE_FLOW_URL=/api/flow
ARG VITE_SCORING_URL=/api/scoring
ENV VITE_FLOW_URL=$VITE_FLOW_URL
ENV VITE_SCORING_URL=$VITE_SCORING_URL

RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
