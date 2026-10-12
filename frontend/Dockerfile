# syntax=docker/dockerfile:1

FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

FROM node:22-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./package.json
# adapter-node: el servidor se ejecuta con `node build`.
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 3000
ENV PORT=3000 HOST=0.0.0.0
CMD ["node", "build"]
