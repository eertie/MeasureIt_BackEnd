#!/bin/bash
# to start this script at boot: 
# open:     sudo nano /etc/rc.local
# voeg toe: sudo bash /home/pi/pi_shared/Energy/src/server/startServer.sh

gunicorn main:app --workers 2 -k uvicorn.workers.UvicornWorker\
#--bind 0.0.0.0:9000 \
--access-logfile ./data/logs/gunicorn-access.log \
--error-logfile ./data/logs/gunicorn-error.log
