#!/usr/bin/env bash

mongod --logpath=/dev/null &
sleep 5
mongo /nearshops/startup.js
echo "User shopproxy created"
echo "Database populated"
echo "Restarting MongoDB"
mongod --smallfiles --bind_ip_all --logpath=/dev/null