#!/bin/bash
echo "Enabling Robochall startup service..."
sudo systemctl enable robo_starter.service
sudo systemctl start robo_starter.service
echo "Service is now ACTIVE and enabled for boot."