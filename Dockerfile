FROM jenkins/inbound-agent:alpine

USER root

RUN apk add --no-cache nmap curl grep python3 py3-psycopg2 speedtest-cli

USER jenkins
