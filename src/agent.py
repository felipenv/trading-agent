class Agent():
    """Class to handle all operations performed by the agent using REST API"""
    import requests, json
    import pandas as pd

    def __init__(self, credentials, parameters, base_url='https://api.ig.com/gateway/deal'):
        self.credentials = credentials
        self.security_token = None
        self.CST = None
        self.header = None
        self.base_url = base_url
        self.prices = {}
        self.rsi = {}
        self.force = {}
        self.osma = {}
        self.parameters = parameters

    def build_header(self):
        self.header = {'X-IG-API-KEY': self.credentials['apikey'],
                       "Content-Type": "application/json; charset=UTF-8",
                       "Accept": "application/json; charset=UTF-8",
                       "VERSION": "1"}

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
        
        prices_df = prices_df.dropna()

        self.prices[epic][resolution] = prices_df

    # TODO set maximum len for lists of metrics [self.rsi[epic][resolution], self.force[epic][resolution], self.osma[epic][resolution]] (maxBuffer parameter) to avoid lists grow to big and overflow memory.
    def calc_metrics(self, epic, resolutions, type='ask'):

        def initialize_dict(agent):
            agent.rsi[epic] = {k:[] for k in resolutions}
            agent.force[epic] = {k:[] for k in resolutions}
            agent.osma[epic] = {k:[] for k in resolutions}
            agent.prices[epic] = {k:[] for k in resolutions}

        def rsi(agent, resolution):
            agent.get_price(epic, resolution, agent.parameters['numPoints_rsi'], type)
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

            agent.rsi[epic][resolution].append(RSI)

        def force(agent, resolution):
            agent.get_price(epic, resolution, agent.parameters['numPoints_force'], type)
            sum = 0
            for index, row in agent.prices[epic][resolution].iterrows():
                sum += (row.closePrice - row.openPrice) * row.lastTradedVolume
            F = sum/len(agent.prices[epic])
            agent.force[epic][resolution].append(F)

        def osma(agent, resolution):
            agent.get_price(epic, resolution, 2*agent.parameters['M2']-1, type)
            def EMA1():
                def first_EMA(agent, alpha, t):
                    numerator = 0
                    denominator = 0
                    power = 0
                    for i in range(t, -1, -1):
                        numerator += agent.prices[epic][resolution].iloc[i]['closePrice'] * (1-alpha) ** power
                        denominator += (1-alpha) ** power
                        power +=1

                    return numerator/denominator

                alpha = 2/(1+agent.parameters['M1'])
                EMA1_list = []
                for t in range(len(agent.prices[epic][resolution]) - agent.parameters['M1'], len(agent.prices[epic][resolution])):
                    if len(EMA1_list) == 0:
                        ema = first_EMA(agent, alpha, t)
                        EMA1_list.append(ema)

                    else:
                        ema = (alpha*(agent.prices[epic][resolution].iloc[t]['closePrice'])) + ((1-alpha) * EMA1_list[-1])
                        EMA1_list.append(ema)

                return EMA1_list[-1]

            def EMA2():
                def first_EMA(agent, alpha, t):
                    numerator = 0
                    denominator = 0
                    power = 0
                    for i in range(t, -1, -1):
                        numerator += agent.prices[epic][resolution].iloc[i]['closePrice'] * (1-alpha) ** power
                        denominator += (1-alpha) ** power
                        power +=1

                    return numerator/denominator

                alpha = 2/(1+agent.parameters['M2'])
                EMA2_list = []
                for t in range(len(agent.prices[epic][resolution]) - agent.parameters['M2'], len(agent.prices[epic][resolution])):
                    if len(EMA2_list) == 0:
                        ema = first_EMA(agent, alpha, t)
                        EMA2_list.append(ema)

                    else:
                        ema = (alpha*(agent.prices[epic][resolution].iloc[t]['closePrice'])) + ((1-alpha) * EMA2_list[-1])
                        EMA2_list.append(ema)

                return EMA2_list[-1]

            def signal_M3():
                signal = 0
                for i in range(len(agent.prices[epic][resolution]) - agent.parameters['M3'], len(agent.prices[epic][resolution])):
                    signal += agent.prices[epic][resolution].iloc[i]['closePrice']

                return signal/agent.parameters['M3']

            ema1 = EMA1()
            ema2 = EMA2()
            signal_m3 = signal_M3()

            osma = ema1 - ema2 - signal_m3

            agent.osma[epic][resolution].append(osma)

        # calculate metrics for all resolutions

        if self.rsi == {} or self.force == {} or self.osma == {} or epic not in self.prices:
            initialize_dict(self)

        for resolution in resolutions:
            """call get price to calculate metrics"""
            rsi(self, resolution)
            force(self, resolution)
            osma(self, resolution)

