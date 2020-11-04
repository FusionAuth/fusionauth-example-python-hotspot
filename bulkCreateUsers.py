from fusionauth.fusionauth_client import FusionAuthClient
from datetime import datetime
import sys
import random
import string
  
api_key=<your api key>

def get_random_string(length):
  sample_letters = 'abcdefghimnpqrstuvzxykjy23456789ABCDEFGHLMNPQRSTUVZWYJKX'
  result_str = ''.join((random.choice(sample_letters) for i in range(length)))
  return result_str

def get_random_number(length):
  sample_letters = '23456789'
  result_str = ''.join((random.choice(sample_letters) for i in range(length)))
  return result_str

######################################################################################################
client = FusionAuthClient(api_key, 'http://127.0.0.1:9011')
application_id='5ef574b6-6929-427b-8f39-ec82ffc4e15b'
# if you have one tenant, it is not needed
tenant_id='a2541956-b963-bec0-7d6b-1d5d4359e621'

######################################################################################################

print ('This script generates a list of guest users on FuzionAuth for internet access.')
print ('You will be asked for a number from which to generate the user which will have')
print ('the form gst-xxxxxx with xxxxxx numeric.')
print ('Now you will be asked which number to start the generation from and for how')
print ('many, so check which is the last ID you generated earlier.')

print ('At the end a short report will be generated and a file called list_guests.csv')
print ('which will contain the list of users and passwords for the mail merge of the')
print ('coupons.')

startAt = input("What number do I start from? ")
total = input("How many users should I generate? ")

try:
  startNum = int(startAt)
  totalNum = int(total)
except ValueError:
  print("You have not entered valid numbers.")
  sys.exit(1)

print ('')
finalNum=startNum+totalNum-1

print ('I will start from gst-' + str(startNum).zfill(6))
print ('and I will end with gst-' + str(finalNum).zfill(6))
print ('for a total number of users: ' + str(total))

print ('')
conferma = input("Would you like to proceed?  (y/n) ")
if conferma.lower() != 'y':
  print ('Operation canceled!')
  sys.exit(1)

print ('Generating in progress. Wait for...')

list = ''
for x in range(totalNum):
  pwd = '' + get_random_string(8) + '-' + get_random_number(2)
  username = 'gst-' + str(x+startNum).zfill(6)
  user_registration_request = {
    'registration': {
      'applicationId': application_id
    },
    'user': {
      'tenantId' : tenant_id,
      'password': pwd,
      'firstName': 'User guest',
      'lastName': '---',
      'twoFactorEnabled': False,
      'username': username
    },
    'sendSetPasswordEmail': False,
    'skipVerification': False
  }

  client_response = client.register(user_registration_request)
  if client_response.was_successful():
    list = list + username + ',' + pwd + '\r\n'
  else:
    print ('Error ' + str(client_response.error_response))

try:
  text_file = open("/tmp/list_guests.csv", "wt")
  n = text_file.write(list)
  text_file.close()
  if n == 0:
    print ("File list_guest.csv is zero bytes!")
  else:
    print ("File list_guests.csv generated successfully.")
except ValueError:
  print("It was not possible to write the file list_guests.csv!")
  sys.exit(1)

