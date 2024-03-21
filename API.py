import freecurrencyapi

API = freecurrencyapi.Client('fca_live_rMNPweUrCwlPY7gxrSmz1e4g0dXOWR4u71mRUiEV')

currenciesData = API.currencies()
latestExchangeRatesData = API.latest()

currencies = []
latestExchangeRates = []

for currency in currenciesData['data']:
        currencies.append((currenciesData['data'][currency]['name'], currenciesData['data'][currency]['symbol'], currenciesData['data'][currency]['code']))

for rate in latestExchangeRatesData['data']:
        latestExchangeRates.append((rate, round(latestExchangeRatesData['data'][rate], 2)))