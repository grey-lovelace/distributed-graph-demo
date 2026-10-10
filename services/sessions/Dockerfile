FROM oven/bun:1.4-slim
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production
COPY . .
EXPOSE 4002
CMD ["bun", "src/index.ts"]
