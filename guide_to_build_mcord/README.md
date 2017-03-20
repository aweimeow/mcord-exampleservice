# Guide to build M-CORD

This document is reference from [M-CORD's Document](https://wiki.opencord.org/display/CORD/M-CORD+Developer+Environment)

## Build CORD 2.0 version

because of version 2.0 & Master branch are something different, 
in here we will use version 2.0 to build Service

### Get Install Script and run

```bash
curl -o ~/cord-in-a-box.sh https://raw.githubusercontent.com/opencord/cord/cord-2.0/scripts/cord-in-a-box.sh
bash ~/cord-in-a-box.sh -t | tee ~/install.out
```

### Login to XOS VM

CORD in a Box have 3 VM: corddev, **prod**, computed.

```bash
aweimeow@node:~$ ssh prod
vagrant@prod:~$ ls
admin-openrc.sh  keystone_juju_ca_cert.crt  node_key  onos-cord  onos-fabric  service-profile  xos  xos_libraries  xos_services
```

### Copy requirement files

```bash
vagrant@prod:~$ cd ~/service-profile/cord-pod
vagrant@prod:~/service-profile/cord-pod$ cp admin-openrc.sh id_rsa* node_key nodes.yaml ../mcord/
```

### Clean up CORD-POD environment

```bash
vagrant@prod:~/service-profile/cord-pod$ make stop
vagrant@prod:~/service-profile/cord-pod$ make cleanup
```

### Build MCORD

```bash
vagrant@prod:~/service-profile/cord-pod$ cd ~/service-profile/mcord/
vagrant@prod:~/service-profile/mcord$ make local_containers

# Pull vBBU, vPGWC, vSGW from gerrit
vagrant@prod:~/service-profile/mcord$ make pull_services

vagrant@prod:~/service-profile/mcord$ make xos
vagrant@prod:~/service-profile/mcord$ make vtn

# This line is only for using fabric, but CiaB will not have fabric
vagrant@prod:~/service-profile/mcord$ make fabric

vagrant@prod:~/service-profile/mcord$ make mcord
```

## Access Admin Page

Connect to **https://server_ip:8080/xos**

* Username: padmin@vicci.org
* Password: letmein
