class Agent():
    """Class to handle all operations performed by the agent using REST API"""
    import requests, json
    import pandas as pd
    def __init__(self, credentials, base_url='https://api.ig.com/gateway/deal'):
        self.credentials = credentials
        self.security_token = None
        self.CST = None
        self.header = None
        self.base_url = base_url
        self.prices = {}
        self.rsi = {}
        self.force = {}

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
        self.header['CST'] = self.CST
        self.header['X-SECURITY-TOKEN'] = self.security_token

    def get_price(self, epic, resolution, numPoints, type):
        data = {'identifier': self.credentials['user'],
                'password': self.credentials['password']}

        response = self.requests.get(f"{self.base_url}/prices/{epic}/{resolution}/{numPoints}", json=data, headers=self.header)

        prices = response.json()['prices']

        prices_df = Agent.pd.DataFrame()

        for price in prices:
            price_df = Agent.pd.DataFrame.from_dict(price)
            prices_df = prices_df.append(price_df.loc[type]).reset_index(drop=True)

        self.prices[epic][resolution] = prices_df

    def calc_metrics(self, epic, resolutions, numPoints, type):

        def initialize_dict(agent, epic, resolutions):
            agent.rsi[epic] = dict.fromkeys(resolutions)
            agent.force[epic] = dict.fromkeys(resolutions)
            agent.prices[epic] = dict.fromkeys(resolutions)

        def rsi(agent, resolution):
            sum_up = 0
            sum_down = 0
            for index, row in agent.prices[epic][resolution].iterrows():
                diff = row.closePrice - row.openPrice
                if diff > 0:
                    sum_up += diff
                else:
                    sum_down += (-diff)

            avg_up = sum_up/len(agent.prices[epic])
            avg_down = sum_down/len(agent.prices[epic])
            RS = avg_up/avg_down

            RSI = 100 - (100/(1+RS))

            agent.rsi[epic][resolution] = RSI

        def force(agent, resolution):
            sum = 0
            for index, row in agent.prices[epic][resolution].iterrows():
                sum += (row.closePrice - row.openPrice) * row.lastTradedVolume
                F = sum/len(agent.prices[epic])
                agent.force[epic][resolution] = F

        initialize_dict(self, epic, resolutions)

        for resolution in resolutions:
            """call get price to calculate metrics"""
            self.get_price(epic, resolution, numPoints, type)

            rsi(self, resolution)
            force(self, resolution)

