#!/bin/bash

(crontab -l ; echo "00 00 * * * /usr/bin/python3 update_blastdb.py") | crontab -