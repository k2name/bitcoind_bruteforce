#!/bin/bash

masscan -p8332 0.0.0.0-1.0.0.0 --rate=2000 -oG bitcoind.txt
grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" bitcoind.txt > ./log/ip.txt
rm bitcoind.txt

python3 main.py

