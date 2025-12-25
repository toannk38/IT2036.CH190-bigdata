# Vietnam Stock Frontend - Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the Vietnam Stock Frontend application to production environments.

## Prerequisites

### System Requirements
- Node.js 18.x or higher
- npm 9.x or higher
- Modern web browser with ES2020 support
- HTTPS-enabled web server (recommended)

### Environment Setup
- Backend API server running and accessible
- Environment variables configured
- SSL certificates (for HTTPS deployment)

## Build Configuration

### Environment Variables

Create a `.env.production` file in the frontend directory:

```bash
# API Configuration
VITE_API_BASE_URL=https://your-api-domain.com
VITE_API_TIMEOUT=10000

# Application Configuration
VITE_APP_NAME="Vietnam Stock AI"
VITE_APP_VERSION="1.0.0"

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_REPORTING=true

# Performance Configuration
VITE_CACHE_DURATION=300000
VITE_RETRY_ATTEMPTS=3
```

### Production Build

1. **Install Dependencies**
   ```bash
   cd frontend
   npm ci --production=false
   ```

2. **Run Tests**
   ```bash
   npm run test:run
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

4. **Verify Build**
   ```bash
   npm run preview
   ```

The build process will:
- Compile TypeScript to JavaScript
- Bundle and minify all assets
- Optimize images and fonts
- Generate source maps for debugging
- Create a `dist/` directory with production files

### Build Optimization

The current build configuration includes:
- **Code Splitting**: Automatic chunk splitting for better caching
- **Tree Shaking**: Removes unused code
- **Minification**: Reduces bundle size
- **Asset Optimization**: Compresses images and fonts

**Note**: The current bundle size is ~929KB (292KB gzipped). Consider implementing dynamic imports for further optimization if needed.

## Deployment Options

### Option 1: Static File Hosting (Recommended)

Deploy the `dist/` folder to any static file hosting service:

#### Netlify
1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Configure environment variables in Netlify dashboard

#### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod`
3. Configure environment variables in Vercel dashboard

#### AWS S3 + CloudFront
1. Upload `dist/` contents to S3 bucket
2. Configure S3 for static website hosting
3. Set up CloudFront distribution for CDN
4. Configure custom domain and SSL certificate

### Option 2: Docker Deployment

Create a `Dockerfile` in the frontend directory:

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
}
```

Build and run:
```bash
docker build -t vietnam-stock-frontend .
docker run -p 80:80 vietnam-stock-frontend
```

### Option 3: Traditional Web Server

For Apache or Nginx deployment:

1. Copy `dist/` contents to web server document root
2. Configure URL rewriting for client-side routing
3. Set up HTTPS with SSL certificates
4. Configure caching headers for static assets

## Configuration

### API Integration

Ensure the backend API is accessible from the frontend domain. Configure CORS settings on the backend to allow requests from the frontend domain.

### Performance Optimization

1. **Enable Gzip Compression**
   - Configure web server to compress text assets
   - Reduces transfer size by ~70%

2. **Set Cache Headers**
   - Cache static assets for 1 year
   - Use ETags for cache validation

3. **Enable HTTP/2**
   - Improves loading performance
   - Reduces connection overhead

### Security Configuration

1. **HTTPS Only**
   - Redirect all HTTP traffic to HTTPS
   - Use HSTS headers

2. **Content Security Policy**
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://your-api-domain.com;
   ```

3. **Security Headers**
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block

## Monitoring and Maintenance

### Health Checks

The application includes built-in health checks:
- API connectivity verification
- Component error boundaries
- Automatic retry mechanisms

### Performance Monitoring

Monitor these metrics:
- Page load times
- API response times
- Error rates
- User engagement

### Updates and Maintenance

1. **Regular Updates**
   - Update dependencies monthly
   - Monitor security advisories
   - Test updates in staging environment

2. **Backup Strategy**
   - Version control for source code
   - Backup deployment configurations
   - Document rollback procedures

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify VITE_API_BASE_URL is correct
   - Check CORS configuration on backend
   - Verify network connectivity

2. **Build Failures**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

3. **Routing Issues**
   - Ensure web server is configured for SPA routing
   - Check React Router configuration
   - Verify base URL settings

### Debug Mode

For debugging in production:
1. Enable source maps in build
2. Use browser developer tools
3. Check console for error messages
4. Monitor network requests

## Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test API connectivity
4. Review browser console errors

## Rollback Procedure

In case of deployment issues:
1. Stop current deployment
2. Restore previous version from backup
3. Verify functionality
4. Investigate and fix issues
5. Redeploy when ready

---

**Last Updated**: December 2024
**Version**: 1.0.0