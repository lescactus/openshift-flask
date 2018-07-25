#!/bin/bash

# Ensure that assigned uid has entry in /etc/passwd.

if [ `id -u` -ge 10000 ]; then
    #cat /etc/passwd | sed -e "s/^$NB_USER:/builder:/" > /tmp/passwd
    #echo "$NB_USER:x:`id -u`:`id -g`:,,,:/home/$NB_USER:/bin/bash" >> /tmp/passwd
    #cat /tmp/passwd > /etc/passwd
    #rm /tmp/passwd
   sed -i "s/test:x:100001:0/test:x:`id -u`:0/g" /etc/passwd
   #sed -i "s/www-data:x:33:33/www-data:x:`id -u`:`id -g`/g" /etc/passwd
fi

exec "$@"
