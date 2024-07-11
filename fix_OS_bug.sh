#!/bin/bash

grep -E "lp|sync|halt|news|uucp|operator|games|gopher|smmsp|nfsnobody|nobody" /etc/passwd|cut -f 1 -d ':'>/tmp/account.txt
for i in `cat /tmp/account.txt` ; do userdel $i; done

useradd audit -s /sbin/nologin
echo "DFwe34#231"|passwd --stdin -l audit

lock_rule_nu=`grep -c pam_tally2.so /etc/pam.d/system-auth`
if [ "${lock_rule_nu}" = "0" ] ; then
    echo "auth        required      pam_tally2.so    deny=5    unlock_time=300 even_deny_root root_unlock_time=300
account     required      pam_tally2.so">>/etc/pam.d/system-auth
elif [ "${lock_rule_nu}" = "1" ] ; then
    sed -i "s/.*pam_tally2.so.*//g" /etc/pam.d/system-auth
    echo "auth        required      pam_tally2.so    deny=5    unlock_time=300 even_deny_root root_unlock_time=300
account     required      pam_tally2.so">>/etc/pam.d/system-auth
elif [ "${lock_rule_nu}" = "2" ] ; then
sed -i "s/^auth.*pam_tally2.so.*unlock_time.*/auth        required      pam_tally2.so    deny=3    unlock_time=300 even_deny_root root_unlock_time=300/g" /etc/pam.d/system-auth
sed -i "s/.*pam_tally2.so$/account     required      pam_tally2.so/g" /etc/pam.d/system-auth
fi
sed -i "s/^password.*requisite.*pam_cracklib.so.*/password    requisite     pam_pwquality.so try_first_pass retry=3 ucredit=-1  lcredit=-1  dcredit=-1  ocredit=-1 minlen=8/g" /etc/pam.d/system-auth
sed -i "s/^password.*requisite.*pam_pwquality.so.*/password    requisite     pam_cracklib.so try_first_pass local_users_only retry=3 authtok_type= difok=1 minlen=8 ucredit=-1 lcredit=-1 dcredit=-1/g" /etc/pam.d/system-auth
sed -i "s/^password.*sufficient.*pam_unix.so.*shadow.*nullok.*try_first_pass.*use_authtok.*/password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok remember=5/g" /etc/pam.d/system-auth


sed -i "s/^PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/g" /etc/login.defs
sed -i "s/^PASS_MIN_DAYS.*/PASS_MIN_DAYS 10/g" /etc/login.defs
sed -i "s/^PASS_WARN_AGE.*/PASS_WARN_AGE 7/g" /etc/login.defs


wheel_nu=`grep -c  "pam_wheel.so group=wheel" /etc/pam.d/su`
if [ "${wheel_nu}" = "0" ] ; then
echo "auth           required        pam_wheel.so group=wheel">>/etc/pam.d/su
fi

echo "order hosts，bind" >> /etc/host.conf
#echo "multi on" >> /etc/host.conf


#sed -i "s/.*PermitRootLogin.*yes/PermitRootLogin no/g" /etc/ssh/sshd_config
touch /etc/motd
echo " Authorized users only. All activity may be monitored and reported " > /etc/motd

touch /etc/ssh_banner
chown bin:bin /etc/ssh_banner
chmod 644 /etc/ssh_banner
echo " Authorized only. All activity will be monitored and reported " > /etc/ssh_banner


banner_nu=`grep ssh_banner /etc/ssh/sshd_config|wc -l`
if [ "${banner_nu}" = "0" ] ; then
echo "Banner /etc/ssh_banner">>/etc/ssh/sshd_config
elif [ "${banner_nu}" = "1" ] ; then
sed -i "s#.*Banner.*/etc/ssh_banner#Banner /etc/ssh_banner#g" /etc/ssh/sshd_config
fi
#systemctl restart sshd



###口令策略
banner_nu1=`grep 'even_deny_root root_unlock_time=300' /etc/pam.d/login|wc -l`
if [ "${banner_nu1}" = "0" ] ; then
	echo "auth    required    pam_tally2.so deny=3 lock_time=300 even_deny_root root_unlock_time=300" >> /etc/pam.d/login
fi

sy=`grep  'auth       include      system-auth' /etc/pam.d/login |wc -l`
if [ "${sy}" = "0" ] ; then
	echo "auth       include      system-auth" >> /etc/pam.d/login
fi


sshd_nu1=`grep 'even_deny_root root_unlock_time=300' /etc/pam.d/sshd|wc -l`
if [ "${sshd_nu1}" = "0" ] ; then
	echo "auth    required    pam_tally2.so deny=3 lock_time=300 even_deny_root root_unlock_time=300" >> /etc/pam.d/sshd
fi


echo "umask 027">>/etc/profile
#source /etc/profile
chmod 644 /etc/passwd
chmod 400 /etc/shadow
chmod 644 /etc/group
chmod 644 /etc/services
chmod 600 /etc/xinetd.conf
chmod 600 /etc/security

chmod 640 /etc/rsyslog.d/listen.conf
chmod 640 /var/log/boot.log

###远程访问控制
echo "telnet:1.201.*">/etc/hosts.deny
echo "all:all:allow">/etc/hosts.allow


echo "* soft core 0
* hard core 0">>/etc/security/limits.conf
chattr +a /var/log/messages
echo "alias ls='ls -aol'
alias rm='rm -i'">>~/.bashrc
echo "TMOUT=300
export TMOUT">>/etc/profile
sed -i "s/^TMOUT=.*/TMOUT=300/g" /etc/profile
source /etc/profile
sysctl -p

###启用远程日志
echo "*.err;kern.debug;daemon.notice /var/adm/messages">>/etc/rsyslog.conf
echo "*.* @192.168.1.222">>/etc/rsyslog.conf
touch /var/adm/messages
chmod 640 /var/adm/messages
systemctl restart rsyslog




####fix the mistake
#cp -fa /tmp/check_server_linux.pl /root/crontab_scripts/
#/bin/sh /root/crontab_scripts/auto_audit_report.sh
#/bin/rm -rf /tmp/fix_OS_bug.sh



#口令复杂度
#sed -i "s/^password.*requisite.*pam_cracklib.so.*/password    requisite     pam_pwquality.so try_first_pass retry=3 ucredit=-1  lcredit=-1  dcredit=-1  ocredit=-1 minlen=8/g" /etc/pam.d/system-auth
sed -i "s/^auth.*pam_tally2.so.*unlock_time.*/auth        required      pam_tally2.so    deny=3    deny=5 lock_time=30 even_deny_root root_unlock_time=300/g" /etc/pam.d/system-auth
echo "password    requisite     pam_cracklib.so try_first_pass retry=3 dcredit=-1 lcredit=-1 ucredit=-1 ocredit=-1 minlen=8" >> /etc/pam.d/system-auth
echo "auth       include      system-auth" >> /etc/pam.d/login
echo "password    required     pam_pwquality.so retry=3" >> /etc/pam.d/passwd
echo "minlen=8
dcredit=-1
ucredit=-1
lcredit=-1
ocredit=-1" >>  /etc/security/pwquality.conf
echo "auth            required        pam_wheel.so use_uid" >> /etc/pam.d/su

#日志报告
cd /var/log/
chmod 640 authpriv.log boot.log cron errors.log kern.log

sed -i 's/net.ipv4.tcp_syncookies = 0/net.ipv4.tcp_syncookies = 1/g' /etc/sysctl.conf
sed -i 's/net.ipv4.tcp_syncookies=0/net.ipv4.tcp_syncookies = 1/g' /etc/sysctl.conf
sysctl -p

#sed -i "/HISTSIZE/d" /etc/profile
#echo "HISTFILESIZE=5">> /etc/profile
#echo "HISTSIZE=5">> /etc/profile
#source /etc/profile
