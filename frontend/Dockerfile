# Base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Enable legacy peer deps if needed (sometimes helps with next/react versions)
# ENV NPM_CONFIG_LEGACY_PEER_DEPS=true

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Build the application
# Note: NEXT_PUBLIC_API_URL should be passed as build-arg or env vars if possible
# For now, we build it. If env vars change, we might need rebuild or use runtime config
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
