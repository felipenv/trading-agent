class Agent():
    '''Class to handle all operations performed by the agent using REST API'''
    import requests
    import json
    def __init__(self, credentials, base_url='https://api.ig.com/gateway/deal'):
        self.credentials = credentials
        self.security_token = None
        self.CST = None
        self.header = None
        self.base_url = base_url

    def build_header(self):
        self.header = {'X-IG-API-KEY': self.credentials['apikey'],
                       "Content-Type": "application/json; charset=UTF-8",
                       "Accept": "application/json; charset=UTF-8",
                       "VERSION": "1"}
        pass

    def login(self):
        if self.header is None:
            self.build_header()

        data = {'identifier': self.credentials['user'],
                'password': self.credentials['password']}
        response = self.requests.post(f"{self.base_url}/session", json=data, headers=self.header)

        self.security_token = response.headers['X-SECURITY-TOKEN']
        self.CST = response.headers['CST']


