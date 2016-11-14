## To deploy **Inception-web** via [Gunicorn](http://gunicorn.org/) and [Nginx](http://nginx.org/) in Linux as follow:  

###   

Install Gunicorn.  

    # pip install gunicorn  
Install Nginx.   

    # yum install nginx  
Configuring Nginx to Proxy Requests.  
    # vim /etc/nginx/nginx.conf  

        server {  

        listen       80 default_server;  

        listen       [::]:80 default_server;  

        server_name  sqlaudit.cmug.com;  

        root         /usr/share/nginx/html;  

        location / {  

            proxy_pass http://127.0.0.1:5000;  

            proxy_set_header Host $host;  
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  

        }  

Start Gunicorn and Nginx.  
 
    # service nginx start  
    # gunicorn --daemon --workers 16 127.0.0.1:5000 inception-web:app  
