# Inception-web  

It's the [Inception](http://mysql-inception.github.io/inception-document/) based **MySQL SQL Audit Platform** by Python.

### Architecture  
   
       [Get dynamic code] via tokengen tool  
                || login  
      +------------------+  
      |                  |  
      |  Inception-web   |(Flask webserver:5000)  
      |                  |  
      +------------------+  
                |  
                |  
                v  
     +--------------------+  
     |                    |  
     |  Inception-server  |(Inception proxyserver:33066)  
     |                    |  
     +--------------------+  
                |  
                |  
                v  
     +--------------------+  
     |                    |  
     |   MySQL Instance   |(Your dbserver:3306)  
     |                    |  
     +--------------------+  
  
### Usage  
Prerequisites  

    # pip install flask gunicorn  
    # pip install python-redmine    // If you want to make inception-web working with [Redmine](http://www.redmine.org), please install the package. 
    # yum install nginx mysql-community-server
    # bin/Inception --defaults-file=bin/inc.conf   
    # mysql -uroot -h127.0.0.1 -P3306 < ./schema.sql
    # add an inception user on your dbserver with the necessory privileges, which is used to execute your SQLs.

Start inception-web.  

    # python ./inception-web.py  

Goto token page.  

    # http://127.0.0.1:5000                        // Get dynamic code through the redmine issue# 
    # http://127.0.0.1:5000/tokenKznxVczC          // Get dynamic code directly if don't set the with-redmine option

Goto login/portal page.  

    # http://127.0.0.1:5000/login   

Enter your code on home page to login the **SQL Audit PLatform**. And then enjoy your SQL! So easy:P 

 *<mark>Note:</mark> each code will expire in 3600 seconds, which can be set by the code_timeout variable of the inception-web group in inception-web.conf. 
