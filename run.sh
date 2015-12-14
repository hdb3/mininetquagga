#!/bin/bash
source $1.env
if [ -d $1 ] ;
then
  rm -rf $1
fi
mkdir -m 0777 -p $1
cd  $1
source ../zebra.sh
source ../bgpd.sh $ASN
