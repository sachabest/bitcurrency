# Blockchain margin trader

from Requests import requests
import simplejson as json
import sources
from Time import time
import multiprocessing

bitcoin_index = {}
viable_currencies = {}
viable_currencies_string = None
currency_index = {}
currency_refresh_interval = 10 * 60
currency_refresh_tolerance = 10
currency_refresh_last_update = None
wallet = 0.0
best_margin = ()

trade_available = False

def pull_bitcoin_index():
	global bitcoin_index, viable_currencies
	bitcoin_index = requests.get(sources.bitcoin_index).json()
	if viable_currencies is None:
		viable_currencies = bitcoin_index.keys()
		for currency in viable_currencies:
			viable_currencies_string += currency + ','
		viable_currencies_string = viable_currencies_string[:-1]

# note this is refreshed every x interval (currency_refresh_interval), so
# we only get viable data within a tolerance of the refresh (currency_refresh_tolerance)
def pull_currency_index():
	global currency_index, currency_refresh_last_update, trade_available
	new_index = requests.get(sources.currency_index)
	if currency_index != new_index.json():
		time_diff = time.now() - currency_refresh_last_update
		currency_refresh_last_update = time.now()
		if time_diff <= currency_refresh_tolerance:
			currency_index = new_index.json()
			trade_available = True

def find_best_margin():
	total_threads = len(viable_currencies)
	threads = [] # change to capacity later
	for i in xrange(total_threads):
		t = multiprocessing.Process(target=find_margin, args=(viable_currencies[i]))
		t.daemon = True
		threads.append(t)
		t.start()
	while not block_threads(threads):
		threading.current_thread.sleep(0.001)
	if time.now() - currency_refresh_last_update < currency_refresh_tolerance:
		execute_trade()

def block_threads(threads):
	for t in threads:
		if t.is_alive:
			return False
	return True

def find_margin(source_currency):
	'''
	Given a specific currency to sell Bitcoin for, what is the best currency to switch to
	in order to buy bitcoin back (locked at one step for now, this could in theory be indefinite)
	Question: how could this be modeled as a finite state machine given a number of steps? Is there
	a way to do so or is the system indeterminite regardless?
	'''

	global best_margin
	outgoing_currency = wallet * bitcoin_index[source_currency]['sell']
	current_best = -1
	current_best_intermediate = None
	for currency in viable_currencies:
		if currency == source_currency:
			continue
		step_new_currency = outgoing_currency * currency_index[source_currency + currency]
		step_new_currency = step_new_currency * bitcoin_index[currency]['buy']
		if step_new_currency > current_best:
			current_best = step_new_currency
			current_best_intermediate = currency
	if current_best > best_margin[2]:
		best_margin = (source_currency, current_best_intermediate, current_best)

def execute_trade():
	pass

def pull_bitcoin_indef():
	while True:
		pull_bitcoin_index()

def pull_currency_indef():
	while True:
		pull_currency_index()

def run_loop():
	bit_thread = multiprocessing.Process(target=pull_bitcoin_indef)
	bit_thread.daemon = True
	bit_thread.start()
	currentcy_thread = multiprocessing.Process(target=pull_currency_indef)
	currentcy_thread.daemon = True
	currentcy_thread.start()
	print 'Algorithm threads running. Type q or quit to quit'
	while True:
		cmd = raw_input()
		if cmd == 'q' or cmd =='quit':
			bit_thread.terminate()
			currentcy_thread.terminate()
			return

