# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 15:17:38 2021

@author: A2010183
"""


import requests       # HTTP library for requesting website
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

class SDW_API:
    
    def __init__(self, ticker_list, start=None, end=None, outpath=None, filename=None, target_freq=None,method=None):
        if type(ticker_list)!=list:
            raise Exception("TypeError: 'ticker_list' must be list")
        
        if type(start)!=str and start is not None: 
            raise Exception("TypeError: 'start' must be str or None")
            
        if type(end)!=str and end is not None: 
            raise Exception("TypeError: 'end' must be str or None")
            
        if type(outpath)!=str and outpath is not None: 
            raise Exception("TypeError: 'outpath' must be str or None")
            
        if type(filename)!=str and filename is not None: 
            raise Exception("TypeError: 'filename' must be str or None")
            
        if type(target_freq)!=str and target_freq is not None: 
            raise Exception("TypeError: 'target_freq' must be str or None")
        
        if type(method)!=str and method is not None: 
            raise Exception("TypeError: 'method' must be str or None")
            
        self.ticker_list = ticker_list
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
        self.outpath = outpath
        self.filename = filename
        self.target_freq = target_freq
        self.method = method
        
    def __call__(self):
        self.__requrl()
        self.__fetch()
        self.__allign_freq()
        
    def __requrl(self):
        """
        Function to convert ticker into request url. The first ticker sequence 
        denotes the database id.

        Parameters
        -------
            ticker.list : list
                list of time series tickers

        """
        # unpack ticker_list
        ticker_list = self.ticker_list
        
        # create empty list of search strings
        searchstrings = {}

        # adjust search strings to match database format
        for i in ticker_list:
            decoded = re.findall(r"(\w+)\.",i)
    
            db = decoded[0]
            ticker = '.'.join(re.findall(r"\.(\w+)",i))
    
            searchstrings[i] = "https://sdw-wsrest.ecb.europa.eu/service/data/" + db + "/" + ticker + "?format=genericdata"

        self.__searchstrings = searchstrings


    def __fetch(self):
        """
        Function to webscrape data. Data and relevant attributes are stored in
        output dictionary.

        """
        searchstrings = self.__searchstrings
        
        # create empty dictionary to store data
        req = {}
        for i in searchstrings:
            # request data 
            response = requests.get(url=searchstrings[i])

            # test response
            if response.status_code == 200:
                print("request for '" + i + "' successful")
            else:
                print("request for '" + i + "'failed. Proceeding with next ticker. Error Code: " + str(response.status_code))
                continue
                
            # extract parse tree
            soup = bs(response.content, 'html.parser')
            
            # create empty dictionary to store data
            data = {}
            freq = soup.find_all('generic:value',{'id':'FREQ'})[0]['value']
    
            if freq == 'M':
                for j in soup.find_all('generic:obs'):
                    date = pd.to_datetime(j.find_all('generic:obsdimension')[0]['value']) + pd.offsets.MonthEnd(0)
                    
                    if self.start is not None:
                        if date >= self.start:
                            data[date] = j.find_all('generic:obsvalue')[0]['value']
                            
                        if self.end is not None:
                            if date >self.end:
                                break
                    else:
                        data[date] = j.find_all('generic:obsvalue')[0]['value']
        
            if freq == 'Q':
                for j in soup.find_all('generic:obs'):
                    date = pd.to_datetime(j.find_all('generic:obsdimension')[0]['value']) + pd.offsets.QuarterEnd(0)
                    
                    if self.start is not None:
                        if date >= self.start:
                            data[date] = j.find_all('generic:obsvalue')[0]['value']
                    
                        if self.end is not None:
                            if date >self.end:
                                break
                        
                    else:
                        data[date] = j.find_all('generic:obsvalue')[0]['value']
                        
            # store data in dataframe
            data_ = pd.DataFrame.from_dict(data, orient='index')

            # store data under corresponding ticker name
            req[i] = {'data' : data_, 'freq' : freq}
            
        self.__req = req


    def __allign_freq(self):
        """
        Function to allign frequency of variables.

        """
        
        req = self.__req
        
        # read out frequencies
        freqs = [req[i]['freq'] for i in req.keys()]
        
        
        minfreq = min(freqs)
        
        #breakpoint()

        dfs = []
        for i in req.keys():
            #breakpoint()
            
            # set column name to dict keys
            req[i]['data'].columns = [i]
            
            # convert to numeric
            req[i]['data'] = pd.to_numeric(req[i]['data'][i])
            
            if self.target_freq == None:    
                if req[i]['freq']>minfreq:
                    req[i]['data'] = req[i]['data'].resample(minfreq, convention='start').asfreq()
                        
            else:
                if self.method == None:
                    print("\nNo method set, using mean()")
                    self.method = 'mean'
                    
                if self.method == 'mean':
                    #breakpoint()
                    if req[i]['freq']<self.target_freq:
                         req[i]['data'] = req[i]['data'].groupby([pd.Grouper(freq=self.target_freq)]).mean()
                    elif req[i]['freq']>=self.target_freq:
                         req[i]['data'] = req[i]['data'].resample(self.target_freq, convention='start').asfreq()
                          
            
            #breakpoint()
            # collect data in a list
            dfs.append(req[i]['data'])
        
        # concatenate data
        output = pd.concat(dfs,axis=1)
        
        self.data = output
        
        if self.outpath is not None:
            output.to_excel(self.outpath + "/" + self.filename)


print('SDW_API class initialized')



