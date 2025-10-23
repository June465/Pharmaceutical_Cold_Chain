# explorer/Dockerfile

# Use an official Node.js runtime
FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies first for better caching
COPY package.json .
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the React app runs on
EXPOSE 3000

# Command to start the development server
CMD ["npm", "start"]