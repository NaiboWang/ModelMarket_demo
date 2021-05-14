# Nginx Configuration

* 1. Put certificate files .pem and .key to /etc/nginx/cert (should make dir first).
* 2. Modify the nginx configuration file.
* 3. Note rewrite all http requests to https, with 301 status.
* 4. Change the certificate per year.
    
# New method
Use certbot to generate certificates and use crond to set timed task to renew certificates automatically