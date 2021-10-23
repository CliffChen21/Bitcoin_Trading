from tools.deribit_api import Deribit
Tokens = {
  "Deribit": {
    "Read": {
      "id": "O9V1XdyF",
      "secret": "TXsmyJF_aYvw7GKjuKv-HOaZzMLC07bhOUO2m4vCqLE"
    }

  }
}

class ZeroCurve:

    def __init__(self, Tokens, ccy="BTC"):

        self.drb_api = Deribit(Tokens)
        self.symbs = self.drb_api.tradeable_symbols(ccy=ccy, kind="future")
        self.ccy = ccy

    @classmethod
    def get_price_from_orderbook(cls, orderbook):
        return (orderbook['bid'][0][0] + orderbook['ask'][0][0])/2

    def get_market_price(self):

        mkt_price = dict()
        for symb in self.symbs:
            price = ZeroCurve.get_price_from_orderbook(self.drb_api.get_order_book(symb))
            mkt_price[symb] = price
        mkt_price[self.ccy] = self.drb_api.get_index_price("{}_usd".format(self.ccy.lower()))['result']['index_price']

        return mkt_price

    def cal_market_zc_rate(self):

        mkt_price = self.get_market_price()
        for price in mkt_price:
            matu = 



if __name__ == '__main__':
    print(ZeroCurve(Tokens).get_market_price())



