#!/bin/sh

# Copyright(c) Gordon Elliott 2014

/usr/bin/python3.4 /projects/bitcoin/src/event_api/notify_endpoint.py &

cd /projects/bitcoin-testnet-box-master
make start

# in the event that this delay isn't sufficient and the generate-true fail
# just rerun it by hand once bitcoind has started responding
sleep 10
make generate-true
