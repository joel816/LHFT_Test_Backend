# LHFT_Test_Backend


The server needs to support configuration of the following style:

{ "symbols": [ "AAAA", "BBBB", "CCCC", "DDDD" ], "update_frequency_milliseconds": 300, "elements_per_update": 50 }

The server should output the number of elements at a frequency configured for symbols.

Example elements update:

[ { "symbol": "AAAA", "price": 3003 }, { "symbol": "BBBB", "price": 43124 } ]

The price should be randomly generated.
