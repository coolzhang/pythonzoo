# Inception-web  

It's the [Inception](http://mysql-inception.github.io/inception-document/) based MySQL SQL audit platform by Python.

### Architecture  
   
       [Get dynamic code] via icoder tool  
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
Start inception-web  

    # python ./inception-web.py  
Goto home page  

    # http://127.0.0.1:5000  
Goto icoder page to get a dynamic code  

    # http://127.0.0.1:5000/icoder  
Enter your codge on home page to login the **SQL Audit PLatform**. And then enjoy your SQL! So easy:P 

Note: each code will expire in 3600 seconds.

