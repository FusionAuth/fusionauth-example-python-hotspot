gwInterface="ens37"
iptables -F
iptables -F -t nat
iptables -w -P OUTPUT  DROP
iptables -w -P INPUT   DROP
iptables -w -P FORWARD DROP
iptables -w -A INPUT   -m conntrack --ctstate ESTABLISHED -j ACCEPT
iptables -w -A OUTPUT  -m conntrack --ctstate ESTABLISHED -j ACCEPT
iptables -w -A FORWARD -m conntrack --ctstate ESTABLISHED -j ACCEPT
iptables -w -A INPUT  ! -i $gwInterface -p tcp -m tcp  --dport 22  -m conntrack --ctstate NEW,ESTABLISHED -j  ACCEPT
iptables -w -A OUTPUT -p tcp -m tcp  --sport 22  -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -w -I INPUT ! -i $gwInterface -m conntrack --ctstate NEW  -p tcp --dport 8080 -j ACCEPT
iptables -w -I INPUT ! -i $gwInterface -m conntrack --ctstate NEW  -p tcp --dport 80 -j ACCEPT
iptables -w -I INPUT ! -i $gwInterface -m conntrack --ctstate NEW -p tcp --dport 9011 -j ACCEPT
iptables -w -I OUTPUT -p icmp -j ACCEPT
iptables -w -A INPUT -i lo -j ACCEPT
iptables -w -A OUTPUT -o lo -j ACCEPT
IPaddress=($(ip addr | grep 'inet ' | awk {'print $2'} | cut -d "/" -f 1))
for i in "${IPaddress[@]}"
do
  iptables -w -A INPUT -s $i -m conntrack --ctstate NEW  -j ACCEPT
done
iptables -w -A OUTPUT -m conntrack --ctstate NEW -j ACCEPT
iptables -w -A OUTPUT  -j LOG  --log-level info --log-prefix "OUTPUT -- DENY " # TODO should it be output?
iptables -w -A INPUT   -j LOG  --log-level info --log-prefix "INPUT -- DENY "
iptables -w -A FORWARD -j LOG  --log-level info --log-prefix "FORWARD -- DENY "
iptables -w -N clientRule
iptables -w -A clientRule  -j ACCEPT
