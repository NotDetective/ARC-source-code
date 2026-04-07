#!/bin/bash
echo "Disabling Robochall startup service..."
sudo systemctl stop robo_starter.service
sudo systemctl disable robo_starter.service
echo "Service has been STOPPED and will not run at boot."