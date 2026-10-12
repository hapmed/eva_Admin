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
COPY package.json package-lock.json* ./
# adapter-node externaliza las dependencias de producción: hay que instalarlas.
RUN npm ci --omit=dev || npm install --omit=dev
COPY --from=build /app/build ./build
# adapter-node: el servidor se ejecuta con `node build`.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 3000
ENV PORT=3000 HOST=0.0.0.0
CMD ["node", "build"]
