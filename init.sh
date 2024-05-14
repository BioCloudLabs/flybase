#!/bin/bash
mkdir fasta blastdb_custom
chmod -R 777 fasta/ blastdb_custom/
apt install python3-pip docker.io -y 
pip install docker
docker pull ncbi/blast
(crontab -l ; echo "00 00 * * * /usr/bin/python3 update_blastdb.py") | crontab -
