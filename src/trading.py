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


    agent = Agent(credentials, base_url='https://api.ig.com/gateway/deal')




if __name__ == "__main__":
    main()
