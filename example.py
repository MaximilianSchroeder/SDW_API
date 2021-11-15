# Import the SDW_API class
from sdw_api import SDW_API

# define a list of tickers. In this case Inflation, GDP, Eonia, and employment in
# hour worked
tickers = ['ICP.M.U2.Y.XEF000.3.INX',
           'MNA.Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N',
           'FM.M.U2.EUR.4F.MM.EONIA.HSTA',
           'ENA.Q.Y.I8.W2.S1.S1._Z.EMP._Z._T._Z.HW._Z.N']

# initialize the class
example = SDW_API(tickers)

# call the class to download the data
example()

# he data file can be retrieved with
example.data