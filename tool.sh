mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo  http://mirrors.aliyun.com/repo/Centos-7.repo
yum make cache

#wget https://dl.bintray.com/boostorg/release/1.66.0/source/boost_1_66_0.zip
#unzip boost_1_66_0.zip

#yum intall gcc gcc-c++ python-devel cmake -y

#cd boost_1_66_0

#./bootstrap.sh –with-libraries=all –with-toolset=gcc -with-python=/usr/bin/python2.7

#./b2 toolset=gcc
#./b2 install --prefix=/usr
#ldconfig -v

#git clone https://github.com/xyzwj/xtp_api_python.git

#git config --global user.email "xyz-wj@163.com"
#git config --global user.name "xyzwj"

