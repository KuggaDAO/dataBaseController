import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re


class DataFetcher:

    @classmethod
    def get_all_transaction_data(cls, address, apikey):
        """
        get all transaction data on a certain contract address. The process will terminate if
        it gets all data and print a message.
        :param address: erc20 smart contract address
        :param apikey: your alchemy apikey
        :return: pd.dataframe object which stands for the request result
        """
        url = "https://eth-mainnet.g.alchemy.com/v2/" + apikey
        result = []
        tmp_data = DataFetcher._get_thousand_transaction_data(address, url)
        try:
            while True:
                transfers = tmp_data['result']['transfers']
                df = pd.DataFrame(transfers)
                result.append(df)
                print("data time:", transfers[0]['metadata']['blockTimestamp'])
                pagekey = tmp_data['result']['pageKey']
                tmp_data = DataFetcher._get_thousand_transaction_data(address, url, pagekey)
        except KeyError:
            print("Note: there are only {0} transactions".format(sum(len(a) for a in result)))
            return pd.concat(result)

    @classmethod
    def _get_thousand_transaction_data(cls, address, url, pagekey=None, reverse=False):
        order = ("desc" if reverse else "asc")
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": "0x0",
                    "toBlock": "0xfd21b6",
                    "contractAddresses": [address],
                    "category": ["erc20"],
                    "withMetadata": True,
                    "excludeZeroValue": True,
                    "maxCount": "0x3e8",
                    "order": order
                }
            ]
        }
        if pagekey is not None:
            payload["params"][0]["pageKey"] = pagekey
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        return requests.post(url, json=payload, headers=headers).json()

    @classmethod
    def get_historical_price(cls):
        EXCHANGE = "gateio"
        PAIR = "bankusdt"
        START_DATE = '5/5/2021'
        END_DATE = '12/10/2022'
        PERIOD = 60
        start_ts = DataFetcher.to_timestamp(START_DATE)
        end_ts = DataFetcher.to_timestamp(END_DATE)
        params = {
            'after': start_ts,
            'before': end_ts,
            'periods': PERIOD,
        }
        ohlc_resp = requests.get(
            f'https://api.cryptowat.ch/markets/{EXCHANGE}/{PAIR}/ohlc',
            params=params)
        data = [tuple([datetime.fromtimestamp(i[0])] + i[1:])
                for i in ohlc_resp.json()['result'][f'{PERIOD}']]
        columns = ['date', 'open', 'high', 'low', 'close',
                   'volume', 'qt_volume']
        df = pd.DataFrame.from_records(data, columns=columns)
        return df

    @classmethod
    def find_exchange(cls, swap_name):
        resp = requests.get('https://api.cryptowat.ch/exchanges')
        exchange_names = [e['symbol'] for e in resp.json()['result'] if e['active']]
        for name in exchange_names:
            print("finding:", name)
            exchange_resp = requests.get(f'https://api.cryptowat.ch/markets/{name}')
            try:
                pairs = [i['pair'] for i in exchange_resp.json()['result'] if i['active']]
            except TypeError:
                print("exchange error at", name)
            for pair in pairs:
                if re.search(swap_name, pair):
                    print("find exchange", pair, "at", name)

    @classmethod
    def get_his_price_cc_min(cls, to_ts):
        fsym = "BANK"
        tsym = "USDT"
        exchange = "gateio"
        params = {
            'fsym': fsym,
            'tsym': tsym,
            'toTs': to_ts,
            'e' : exchange,
            'limit': 2000,
            'api_key' : "3ae071e4e690b0e6314b25c6dff969c281f5c52847284e722a175aeea7cf6ca8"
        }
        resp = requests.get("https://min-api.cryptocompare.com/data/v2/histominute", params=params)
        data = resp.json()['Data']['Data']
        for i in data:
            i['time'] = datetime.fromtimestamp(i['time'])
        columns = ['date', 'high', 'low', 'open', 'volume_from',
                   'volume_to', 'close', 'conversion_type', 'conversion_symbol']
        return pd.DataFrame.from_records(data, columns=columns)

    @classmethod
    def to_timestamp(cls, date_string):
        element = datetime.strptime(date_string, '%Y/%m/%d')
        return int(datetime.timestamp(element))

    @classmethod
    def get_n_thousand(cls, address, apikey, n, reverse=False):
        """
        get a number of thousand transaction data.
        :param address: smart contract address
        :param apikey: your alchemy apikey
        :param n: how many thousand data you want
        :param reverse: the function defaults transaction history from old to new,
                        put this to true if you want to reverse
        :return: pd.dataframe object
        """
        url = "https://eth-mainnet.g.alchemy.com/v2/" + apikey
        tmp_data = DataFetcher._get_thousand_transaction_data(address, url, reverse=reverse)
        result = []
        try:
            for i in range(n):
                transfers = tmp_data['result']['transfers']
                df = pd.DataFrame(transfers)
                result.append(df)
                print("data time:", transfers[0]['metadata']['blockTimestamp'])
                pagekey = tmp_data['result']['pageKey']
                tmp_data = DataFetcher._get_thousand_transaction_data(address, url, pagekey, reverse=reverse)
        except KeyError:
            print("Note: there are only {0} transactions".format(sum(len(a) for a in result)))
        except IndexError:
            print(address)
        return pd.concat(result)

    @classmethod
    def get_num_from_dict(cls, addresses, apikey, num, reverse=False):
        """
        get num thousand transaction data from alchemy api and save it to ./transaction_data folder
        :param addresses: a dictionary that contains all contract addresses
        :param apikey: your alchemy api key
        :param num: how much thousand transaction data you want
        :param reverse: the function defaults transaction history from old to new,
                        put this to true if you want to reverse
        :return: True
        """
        for name in addresses:
            df = DataFetcher.get_n_thousand(addresses[name], apikey, num, reverse=reverse)
            df.to_csv('./transaction_data/{0}{1}.csv'.format(name, num * 1000))
        return True

    @classmethod
    def get_num_from_list(cls, addresses, apikey, num, reverse=False):
        """
        get num thousand transaction data from alchemy api and save it to ./transaction_data folder
        :param addresses: a list that contains all contract addresses
        :param apikey: your alchemy api key
        :param num: how much thousand transaction data you want
        :param reverse: the function defaults transaction history from old to new,
                        put this to true if you want to reverse
        :return: True
        """
        for adr_num in range(823, len(addresses)):
            df = DataFetcher.get_n_thousand(addresses[adr_num], apikey, num, reverse=reverse)
            df.to_csv('./transaction_data/{0}/{1}.csv'.format(num * 1000, adr_num))
        return True

    @classmethod
    def get_erc20_contract_address(cls):
        """
        get contract addresses of all erc20 tokens
        :return: a list in descending order of all etherscan erc20 contract addresses
        """
        url = "https://etherscan.io/tokens?p="
        headers = {'User-Agent': """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"""}
        result = []
        try:
            for page_num in range(1, 23):
                html_txt = requests.get(url + str(page_num), headers=headers).text
                soup = BeautifulSoup(html_txt, "html.parser")
                div_node = soup.find("div", id="ContentPlaceHolder1_divresult")
                links = div_node.find_all('a')
                for link in links:
                    match_obj = re.match(r"/token/(.*)", link['href'])
                    if match_obj:
                        result.append(match_obj.group(1))
        except requests.exceptions.SSLError:
            print("ssl error, stop at " + str(page_num - 1))
            # The reason I add this is that I always have some unstable network issues...
        return result

