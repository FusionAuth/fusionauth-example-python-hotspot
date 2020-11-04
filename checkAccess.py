#script checkAccess.py: check the token: reply on port TCP 8080. You must execute it at the boot time!
from fusionauth.fusionauth_client import FusionAuthClient
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import urllib.parse
from datetime import datetime
from getmac import get_mac_address
import os
import json
import yaml
import sys

##############################################################
# Declaration Section
##############################################################
apiKey='yfEzL94JXNFKotLzH75My-s96Bh4oTb9-wkhXe--iUs'
applicationID='4616f048-dd20-47cc-b7a0-33b2c0f237f6'
clientSecret='2sRxJ1BXglI2TwptwpJ--b-PI6xu3ArUK9LnmViAKWs'
redirectURL='http://192.168.144.133:8080'

GWInterface='ens37'
gwIPInterface='192.168.43.254'

client = FusionAuthClient(apiKey, 'http://127.0.0.1:9011')
logoutUrl='http://192.168.144.133:9011/oauth2/logout?client_id=' + applicationID
##############################################################
# End of Declaration Section
##############################################################

class GetHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    parsed_path = urlparse(self.path)
    result=''
    if parsed_path.query.find('code')>-1:
      parameters = dict(urllib.parse.parse_qs(parsed_path.query))
      ipClient = self.client_address[0]
      macClient = get_mac_address(ip=ipClient)
      authCode=parameters.get("code")
      print (datetime.now())
      print ('code: ' + str(authCode))
      print ('IP: ' + str(ipClient))
      print ('MAC: ' + str(macClient))
      client_response = client.exchange_o_auth_code_for_access_token(authCode,applicationID,redirectURL,clientSecret)
      if client_response.was_successful():
        print(client_response.success_response)
        result = '<p style="color:green">Access granted!.</p> <a href="' + logoutUrl + '">Logout</a>'

        cmd='/usr/sbin/iptables -w -t nat -A POSTROUTING -s ' + str(ipClient) + ' -o ' + GWInterface + ' -j SNAT --to-source ' + gwIPInterface
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A INPUT -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 80 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A INPUT -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 443 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A INPUT -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 53 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A INPUT -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p udp -m udp --dport 53 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A FORWARD -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 80 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A FORWARD -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 443 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A FORWARD -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p tcp -m tcp --dport 53 -j clientRule'
        os.system(cmd)

        cmd='/usr/sbin/iptables -w -A FORWARD -m mac --mac-source ' + str(macClient) + ' -m conntrack --ctstate NEW -p udp -m udp --dport 53 -j clientRule'
        os.system(cmd)

#########################################################################
#              pay attention!
#              below we try to acquire the user's username to make any considerations.
#              but if the authentication was performed via SAML, the username may not be there and at some point this code will fail and you will get an "Access DENIED!"
#########################################################################  
        jsonResponse=json.loads(str(client_response.success_response).replace("\'", "\""))        
        userId= jsonResponse['userId']
        userInfo=client.retrieve_user(userId)
        userInfoStr= str(userInfo.success_response).replace("\'", "\"")
        userInfoJson = yaml.load(userInfoStr, Loader=yaml.FullLoader)
        userName = userInfoJson['user']['username']
        userName = userName.lower()
        print ("Authenticated user: " + userName)
        if userName.startswith('gst-'):
          print ("Guest user identified! Now you need to delete it. This part is left to the reader ...")
#########################################################################
#                  part not implemented! not essential at the moment.
#          imagine that the various guest users (see specific script for the creation) can navigate only until the next reset of the rules.
#          we do not want to be able to surf more days with the same coupon: therefore after accessing the user must be deleted (or deactivated).
#########################################################################
        sys.stdout.flush()

      else:
        print(client_response.error_response)
        result = '<p style="color:red">Access DENIED!</p> <a href="' + logoutUrl + '">Retry</a>'
        sys.stdout.flush()

    message1 = [
        '<html>',
        '<head>',
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">',
        '<title>Result of access to the ACME Hotspot</title>',
        '</head>',
        '<body>',
        result,
        '</body>',
        '</html>'
        ]

    message1.append('')
    message2 = ''.join(message1)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(message2.encode(encoding='utf_8'))
    return

if __name__ == '__main__':
  from http.server import BaseHTTPRequestHandler, HTTPServer
  server = HTTPServer(('0.0.0.0', 8080), GetHandler)
  print('Starting server, use <Ctrl-C> to stop')
  server.serve_forever()

