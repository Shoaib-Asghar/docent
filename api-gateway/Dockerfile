# Build Stage
FROM node:20-alpine AS builder
WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependencies
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Production Stage
FROM node:20-alpine
WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy prod dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Copy source code
COPY src ./src
COPY tsconfig.json ./

# Expose API Gateway port
EXPOSE 3000

# Start server using tsx directly (standard for lightweight TS services)
CMD ["pnpm", "exec", "tsx", "src/index.ts"]
