#!usr/bin/env python3

from agent import Agent
import os


def main():
    credentials = {}
    try:
        credentials['user'] = os.environ["user"]
        credentials['password'] = os.environ['password']
        credentials['apikey'] = os.environ['apikey']
    except:
        raise ValueError("missing credentials in environment")


    parameters = {'numPoints_rsi': 10,
                  'numPoints_force':10,
                  'M1': 12,
                  'M2': 26,
                  'M3': 9}

    agent = Agent(credentials, parameters, base_url='https://api.ig.com/gateway/deal')

    agent.login()

    # agent.get_price(epic='CS.D.AUDUSD.CFD.IP', resolution='HOUR', numPoints=100, type='ask')
    agent.calc_metrics(epic='CS.D.EURUSD.CFD.IP', resolutions=['DAY','HOUR_4', 'HOUR', 'MINUTE_30', 'MINUTE_15'], type='ask')


if __name__ == "__main__":
    main()
