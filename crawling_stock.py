from pykrx import stock
import utils
import os
import time
import logging
import requests
import urllib
from urllib.request import urlopen
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from bs4 import BeautifulSoup
from finta import TA
import pandas as pd
from datetime import datetime, timedelta, date
from tqdm import tqdm
MAX_RETRY = 5


def get_html(html_url, timeout=30, decode='utf-8'):
    for tries in range(MAX_RETRY):
        try:
            with urllib.request.urlopen(html_url, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            logging.warning(str(e) + ',html_url:{0}'.format(html_url))
            print(f'Connection warning! tried : {tries}')
            if tries < (MAX_RETRY - 1):
                continue
            else:
                print('Has tried {0} times to access url {1}, all failed!'.format(MAX_RETRY, html_url))
                return None


def pykrx_read_csv(stock_name, Krx_Char_folder_path):
    condition = '.csv'
    csv_file_path = utils.search(Krx_Char_folder_path + '/' + stock_name, condition)
    if os.path.exists(csv_file_path[0]):
        stock_csv = pd.read_csv(csv_file_path[0], parse_dates=True)
    else:
        print('Can''t find csv file!')
    return stock_csv
    print('read done!')


def pykrx_scratch_save_csv(ticker, date_Start, date_End, Krx_Char_folder_path):
    stock_name = stock.get_market_ticker_name(ticker)
    # Get OHLCV
    df = stock.get_market_ohlcv_by_date(date_Start, date_End, ticker)
    if df.empty:
        return 0
    if df['시가'].iloc[0] == 0:
        return 0
    df = df.reset_index()
    df = df.rename(columns={'날짜': 'date', '시가': 'open', '고가': 'high', '저가': 'low', '종가': 'close', '거래량': 'volume'})
    if not os.path.exists(f"{Krx_Char_folder_path}/{stock_name}"):
        os.makedirs(f"{Krx_Char_folder_path}/{stock_name}")
    df.to_csv(f"{Krx_Char_folder_path}/{stock_name}/{ticker}.csv", sep=',', na_rep='0', index=False, header=True)


def pykrx_scratch(date_Start, date_End, Krx_Char_folder_path):
    print(f"* KRX Chart Folder Path >>> {Krx_Char_folder_path}")
    print(f"* Reading Daily Chart >>> {date_Start} - {date_End}")
    # create main folder
    if not os.path.exists(Krx_Char_folder_path):
        os.mkdir(Krx_Char_folder_path)
    # ticker scratch
    KOSPI_ticker_list = stock.get_market_ticker_list(market="KOSPI")
    KOSDAQ_ticker_list = stock.get_market_ticker_list(market="KOSDAQ")

    # KOSPI save as csv
    print('Reading KOSPI...')
    time.sleep(0.5)
    for ticker_KOSPI in tqdm(KOSPI_ticker_list, desc="from KOSPI"):
        pykrx_scratch_save_csv(ticker_KOSPI, date_Start, date_End, Krx_Char_folder_path)

    # KOSDAQ save as csv
    print('Reading KOSDAQ...')
    time.sleep(0.5)
    for ticker_KOSDAQ in tqdm(KOSDAQ_ticker_list, desc="from KOSDAQ"):
        pykrx_scratch_save_csv(ticker_KOSDAQ, date_Start, date_End, Krx_Char_folder_path)
    print('Scratching daily chart is done!')


def stock_52w_update(path, date):
    krx_list = os.listdir(path)
    today_date = utils.get_today_ymd()
    if date == today_date:
        one_year_ago = datetime.now() - timedelta(days=365)
    else:
        one_year_ago = utils.strdate_convert(date) - timedelta(days=365)
    stock_list_52w = []
    count = 0
    for stock_name in tqdm(krx_list):
        if '스팩' in stock_name:
            continue
        if '리츠' in stock_name:
            continue
        stock_csv = pykrx_read_csv(stock_name, path)
        if not (stock_csv['date'] <= date).any():
            continue
        stock_csv = stock_csv[stock_csv['date'] <= date]
        close_price_day = stock_csv.iloc[len(stock_csv) - 1]['close']
        stock_52w_csv = stock_csv[stock_csv['date'] >= one_year_ago.strftime("%Y-%m-%d")]
        high_price_52w = max(stock_52w_csv['high'].to_numpy())
        last_open_day = stock_csv['date'].tail(1)
        stock_date_52w = stock_52w_csv[stock_52w_csv['high'] == max(stock_52w_csv['high'])]['date']
        if high_price_52w == 0:
            # print('This stock has issue for administration.')
            continue
        if last_open_day.iloc[0] == stock_date_52w.iloc[0]:
            continue
        # print(stock_date_52w)
        if high_price_52w > close_price_day:
            gap_percentage = round(((high_price_52w / close_price_day) * 100) - 100, 4)
            stock_list_52w.append([str(stock_name), str(stock_date_52w.iloc[0]), float(gap_percentage), high_price_52w])
            # print('Stock : {}, 52w high date : {}, Gap : {}%, 52w high price : {}'.format(stock_name,
            # stock_date_52w.iloc[0], gap_percentage, high_price_52w))
            count += 1
        elif high_price_52w < close_price_day:
            gap_percentage = round(((close_price_day / high_price_52w) * 100) - 100, 4)
            # print('{} is already hit the 52 weeks target! Going up {}%'.format(stock_name, gap_percentage))
    df = pd.DataFrame(stock_list_52w)
    df = df.rename(columns={0: 'stock', 1: 'date', 2: 'gap', 3: 'high'})
    df_csv = df.sort_values(by='gap', ascending=True)
    df_csv.to_csv('results/this_year/' + '52_weeks_analysis_{}.csv'.format(date),
                  encoding='utf-8', index=False, header=True)
    return df_csv


def base_year_high_52_weeks(df, base_year, date):
    stock_csv = df
    stock_date_52w = stock_csv[stock_csv['high'] == max(stock_csv['high'])]['date']
    stock_csv = stock_csv[stock_csv['date'] < base_year]
    if not os.path.exists('results/base_year/{}'.format(base_year)):
        os.makedirs('results/base_year/{}'.format(base_year))
    stock_csv.to_csv(
        'results/base_year/{}'.format(base_year) + '/' + '52_weeks_analysis_{}_before_{}.csv'.format(date,
                                                                           base_year),
        encoding='utf-8', index=False, header=True)
    return stock_csv


def cal_technical_indicator_name(stock_name, path):
    stock_csv = pykrx_read_csv(stock_name, path)
    stock_csv['ema7'] = TA.EMA(stock_csv, 7)
    stock_csv['ema50'] = TA.EMA(stock_csv, 50)
    stock_csv['ema99'] = TA.EMA(stock_csv, 99)
    stock_csv['upper_band'] = TA.BBANDS(stock_csv)['BB_UPPER']
    stock_csv['lower_band'] = TA.BBANDS(stock_csv)['BB_LOWER']
    stock_csv['rsi'] = TA.RSI(stock_csv, 14)
    return stock_csv


def main(today_date):
    # Today date
    date_str = datetime.strftime(today_date, "%Y-%m-%d")
    Krx_char_folder_path = './krx_ohlcv'
    results_this_year_path = './results/this_year/'
    results_fig_path = './results/TI_fig/{}'.format(date_str)

    # From 2019-01-01 to today
    from_date = '2019-01-01'
    # Do not search this year
    base_year = '2022-01-01'
    # KOSPI & KOSDAQ all stock scratch
    # pykrx_scratch(from_date, date_str, Krx_char_folder_path)
    utils.check_folder(results_this_year_path)
    utils.check_folder(results_fig_path)
    results_52w_csv = results_this_year_path + '52_weeks_analysis_' + date_str + '.csv'
    if not os.path.exists(results_52w_csv):
        # Hit the high in 52 weeks until today
        print('{} - 52 weeks high update for analysis ...'.format(date_str))
        time.sleep(0.5)
        df_52w_csv = stock_52w_update(Krx_char_folder_path, date_str)
        # Hit the high in 52 weeks before 2020/01/01 (base year)
        base_52w_csv = base_year_high_52_weeks(df_52w_csv, base_year, date_str)
    else:
        print('File is existed in results/this_year {}'.format(date_str))
        df_52w_csv = pd.read_csv(results_52w_csv)
        base_52w_csv = base_year_high_52_weeks(df_52w_csv, base_year, date_str)
    top_10_stock_list = list(base_52w_csv[:10]['stock'])
    for stock_name in top_10_stock_list:
        stock_csv = cal_technical_indicator_name(stock_name,
                                                 Krx_char_folder_path)
        if stock_csv.iloc[-1]['volume'] > 0:
            fig = utils.plot_technical_indicators(stock_name, stock_csv, 365)
            fig.savefig('./results/TI_fig/{}/{}.png'.format(date_str, stock_name))
            # In folder, only exists one csv file
            stock_code, _ = os.path.splitext(utils.read_folder_list(Krx_char_folder_path + '/' + stock_name)[0])
            stock_info_url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}'.format(stock_code)
            # Not allowed a new open window
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=options)
            driver.get(stock_info_url)
            html = driver.page_source
            # res = urllib.request.urlopen(stock_info_url).read()
            bs = BeautifulSoup(html, "html.parser")
            # Company information
            bs.find_all('li', {'class': 'dot_cmp'})
            # Crawling all table
            table = bs.select('table')
            table_html = str(table)
            table_fs_list = pd.read_html(table_html)
            # Finantial Statement
            fs = table_fs_list[12]


if __name__ == '__main__':
    main(date.today())