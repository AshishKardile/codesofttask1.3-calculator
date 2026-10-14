# Production-grade lightweight Nginx Alpine base image
FROM nginx:alpine

# Metadata labels
LABEL maintainer="Ashish Kardile"
LABEL description="Premium Off-White Desktop Calculator Web App"

# Remove default Nginx HTML files
RUN rm -rf /usr/share/nginx/html/*

# Copy web application assets into Nginx public directory
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/
COPY background.jpg /usr/share/nginx/html/

# Expose standard HTTP port 80
EXPOSE 80

# Healthcheck to verify the web server is responsive
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Launch Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
