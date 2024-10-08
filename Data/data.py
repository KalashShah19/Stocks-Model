import yfinance as yf

#Reliance
reliance = yf.download('RELIANCE.NS', start='2020-01-01', end='2024-09-13')
reliance.to_csv('D:/! Kalash/AI/Models/Stocks/Data/reliance.csv')
reliance.to_excel('D:/! Kalash/AI/Models/Stocks/Data/reliance.xlsx')
print("Reliance Data saved successfully!")

#Vedanta
reliance = yf.download('VEDL.NS', start='2020-01-01', end='2024-09-13')
reliance.to_csv('D:/! Kalash/AI/Models/Stocks/Data/vedanta.csv')
reliance.to_excel('D:/! Kalash/AI/Models/Stocks/Data/vedanta.xlsx')
print("Vedanta Data saved successfully!")