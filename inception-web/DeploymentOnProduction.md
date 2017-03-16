## To deploy **Inception-web** via [Gunicorn](http://gunicorn.org/) and [Nginx](http://nginx.org/) in Linux as follow:  

Install Gunicorn.  

    # pip install gunicorn  
Install Nginx.   

    # yum install nginx  
Configuring Nginx to Proxy Requests.  

    # vim /etc/nginx/nginx.conf  
        server {  
        listen       80;  
        server_name  _;  
        server_name  sqlaudit.cmug.com;  
        root         /usr/share/nginx/html;  
        location / {  
            proxy_pass http://127.0.0.1:5000;  
            proxy_set_header Host $host;  
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  
            proxy_connect_timeout 3600s;
            proxy_read_timeout 3600s;
        }  

Start Nginx and Gunicorn.  
 
    # service nginx start 
	# cd /PATH_TO/inception-web   
    # gunicorn --daemon --workers 16 --timeout 3600 --graceful-timeout 3600 --bind 127.0.0.1:5000 --log-file /tmp/gunicorn.log inception-web:app  

FAQ

    502/504 Gateway timeout: http://stackoverflow.com/questions/6816215/gunicorn-nginx-timeout-problem
