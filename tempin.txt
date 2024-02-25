1        import json

2        import socketserver

3        import sys

4        import os

5        

6        import requests

7        

8        # edit the values below

9        CONTROLLER_URL = "https://controller1.company.com:8443"

10        CA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ca.pem")

11        

12        PROVIDER = "local"

13        USERNAME = "username"

14        PASSWORD = "password"

15        

16        # do not edit anything below

17        LISTEN_HOST, LISTEN_PORT = "127.0.0.1", 5140

18        

19        

20        class SyslogHandler(socketserver.BaseRequestHandler):

21         def handle(self):

22            data = bytes.decode(self.request[0].strip())

23        

24           if len(data) == 0:

25              print("zero len message received")

26             return

27        

28            # parse to json

29            jlog = json.loads(data)

30        

31            # print(jlog["event_type"] + " received")

32        

33           if jlog["event_type"] == "ip_access" and jlog["action"] == "alert":

34              dn = jlog["distinguished_name"]

35              print(f"ALERT received for {dn}")

36              blacklist_user(dn)

37              revoke_tokens(dn)

38           else:

39              # print("skipping " + jlog["event_type"])

40             pass

41        

42        

43        def login():

44          headers = {"Accept": "application/vnd.appgate.peer-v16+json",

45                     "Content-Type": "application/json"}

46        

47          # authenticate

48          data = {"machineId": "f0031c00-0522-43b3-a642-ae23cfd1bc22",

49                 "providerName": PROVIDER, "username": USERNAME, "password": PASSWORD}

50        

51          res = requests.post(f"{CONTROLLER_URL}/admin/login",

52                              verify=CA_PATH, headers=headers, data=json.dumps(data), timeout=5)

53        

54         if res.status_code != 200:

55            print(f"CONTROLLER_URL login failed with http {str(res.status_code)}")

56            sys.exit(-1)

57        

58          token = json.loads(res.text)["token"]

59          headers["Authorization"] = f"Bearer {token}"

60        

61         return headers

62        

63        

64        def blacklist_user(dn):

65          auth_headers = login()

66        

67          # dn without deviceid

68          user_dn = dn.split(",", 1)[1]

69          data = {"userDistinguishedName": user_dn, "reason": "suspicious traffic"}

70        

71          res = requests.post(f"{CONTROLLER_URL}/admin/blacklist",

72                              data=json.dumps(data), verify=CA_PATH, headers=auth_headers)

73        

74          print(f"{user_dn} blacklisted {str(res.status_code)}")

75         return res.status_code

76        

77        

78        def revoke_tokens(dn):

79          auth_headers = login()

80        

81          data = {"revocationReason": "api revocation for alert", "delayMinutes": 0}

82          res = requests.put(f"{CONTROLLER_URL}/admin/token-records/revoked/by-dn/{dn}",

83                             data=json.dumps(data), verify=CA_PATH, headers=auth_headers)

84        

85          print(f"{dn} tokens revoked {str(res.status_code)}")

86         return res.status_code

87        

88        

89        if __name__ == "__main__":

90          print("========================================================")

91          print(f"Appgate SDP Alert Handler Started on {str(LISTEN_PORT)}")

92          print("========================================================")

93        

94         with socketserver.UDPServer((LISTEN_HOST, LISTEN_PORT), SyslogHandler) as server:

95            server.serve_forever(poll_interval=0.5)