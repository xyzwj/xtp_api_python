cp bin/Linux/Linux+python2.7/*.so /usr/lib64/python2.7/site-packages/
#cp /root/xtp_api_python/boost_1_66_0/stage/lib/* /usr/lib64/python2.7/site-packages/
cp ./source/Linux/xtp_python2_18.19/xtpapi/*.so /usr/lib/
cp ./boost_1_66_0/stage/lib/* /usr/lib/
ldconfig -v
