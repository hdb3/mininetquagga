echo "starting AS ${1}"
sed -e "s/^.-${1}-//g" < ../bgpd.conf > bgpd.conf
bgpd  -f bgpd.conf -i $(pwd)/bgpd.pid -z $(pwd)/zebra.api -d
