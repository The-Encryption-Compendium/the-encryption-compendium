upstream encryption_compendium_server {
    # docker will automatically resolve this to "encryption_compendium"
    server tec-gunicorn:5000;
}

limit_req_zone $binary_remote_addr zone=mylimit:10m rate=60r/m;

# main server
server {

    listen 80;
    server_name encryption_compendium.com;

    location / {
        # everything is passed to Gunicorn
        proxy_pass http://encryption_compendium_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /static/ {
        # for static content
        alias /opt/services/tec-gunicorn/staticfiles/;
    }

    location ~* /research/login {
        limit_req zone=mylimit;
        # everything is passed to Gunicorn
        proxy_pass http://encryption_compendium_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

}