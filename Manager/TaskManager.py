import time

from HQSearch import HQPeakfire, HQPeakfire2, HQPeakfire3, HQPeakfire4, HQHotResult
from HQStock import HQStock, HQStock2, HQStock3, HQStock4, HQStockResult
from IC_stock import IC_stock_cate, IC_stock_cate2, IC_stock_cate3, IC_stock_cate4, IC_stock_result
from Bom_price import bom_price_cate, bom_price_cate2,  BomResult
from EFIND import e_find_stock, e_find_stock2, e_find_stock3, e_find_stock4, e_find_result
from WRTools import PathHelp
import subprocess


def for_ppn():
    subprocess.run(["python", PathHelp.get_file_path('HQSearch', 'HQPeakfire.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQSearch', 'HQPeakfire2.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQSearch', 'HQPeakfire3.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQSearch', 'HQPeakfire4.py')])


def for_ppn2():
    subprocess.run(["python", PathHelp.get_file_path('HQStock', 'HQStock.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQStock', 'HQStock2.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQStock', 'HQStock3.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('HQStock', 'HQStock4.py')])
    time.sleep(120.0)

    subprocess.run(["python", PathHelp.get_file_path('IC_stock', 'IC_stock_cate.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('IC_stock', 'IC_stock_cate2.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('IC_stock', 'IC_stock_cate3.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('IC_stock', 'IC_stock_cate4.py')])
    time.sleep(120.0)

    subprocess.run(["python", PathHelp.get_file_path('EFIND', 'e_find_stock.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('EFIND', 'e_find_stock2.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('EFIND', 'e_find_stock3.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('EFIND', 'e_find_stock4.py')])
    time.sleep(120.0)

    subprocess.run(["python", PathHelp.get_file_path('Bom_price', 'bom_price_cate.py')])
    time.sleep(120.0)
    subprocess.run(["python", PathHelp.get_file_path('Bom_price', 'bom_price_cate2.py')])


# 查询数据库统计数据
def for_statistic():
    subprocess.run(["python", PathHelp.get_file_path('HQStock', 'HQStockResult.py')])
    time.sleep(3*60)
    subprocess.run(["python", PathHelp.get_file_path('IC_stock', 'IC_stock_result.py')])
    time.sleep(3 * 60)
    subprocess.run(["python", PathHelp.get_file_path('EFIND', 'e_find_result.py')])
    time.sleep(3 * 60)
    subprocess.run(["python", PathHelp.get_file_path('Bom_price', 'BomResult.py')])


if __name__ == "__main__":
    for_ppn()
    # for_ppn2()
    # for_statistic()

