
import mysql.connector
from mysql.connector import pooling
from Manager import AccManage
from WRTools import ExcelHelp, PathHelp, LogHelper


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

@singleton
# 建立数据库连接
class DBRecommandChip:

    cnx = mysql.connector.connect(
        host=AccManage.mys['h'],
        user=AccManage.mys['n'],
        password=AccManage.mys['p'],
        database="yjcx_recommended",
        connection_timeout=180
    )

    def __init__(self):
        config = {
            "host": AccManage.mys['h'],
            "user": AccManage.mys['n'],
            "password": AccManage.mys['p'],
            "database": "yjcx_recommended",
        }
        self.connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=30, **config)

    def sql_write(self, sql, data):
        # 创建游标对象
        # 从连接池获取连接
        try:
            cnx = self.connection_pool.get_connection()
            print(f'write data:\n {data}')
            cursor = cnx.cursor()
            # 执行插入操作
            cursor.executemany(sql, data)
            # 提交事务
            cnx.commit()
            # 关闭游标和数据库连接
            cursor.close()
            cnx.close()
        except Exception as e:
            LogHelper.write_log(log_file_name=PathHelp.get_file_path('WRTools', 'MySqlHelpLog.txt'),
                                content=f'yjcx_recommended wirte error {e} {data}')

    def sql_read(self, sql):
        # 从连接池获取连接
        cnx = self.connection_pool.get_connection()
        # 创建游标对象
        cursor = cnx.cursor()
        # 查询数据的SQL语句
        query = sql
        # 执行查询操作
        cursor.execute(query)
        # 获取查询结果
        result = cursor.fetchall()
        # 将结果转换为列表
        data_list = list(result)
        # 打印查询结果
        # 关闭游标和数据库连接
        cursor.close()
        cnx.close()
        print(f'read data:\n {data_list}')
        return data_list

    # 输入二维数组
    def IC_hot_m_write(self, data: list):
        # 插入数据的SQL语句
        # 插入数据的SQL语句
        sql_str = "REPLACE INTO t_IC_hot_m (ppn, manu"
        for index in range(1, 13):
            sql_str += f', m{index}'
        sql_str += ') VALUES (%s, %s '
        for index in range(1, 13):
            sql_str += ', %s'
        sql_str += ")"
        self.sql_write(sql=sql_str, data=data)

    def IC_hot_m_read(self, filter_contend):
        query = f"SELECT * FROM t_IC_hot_m where {filter_contend}"
        result = self.sql_read(query)
        print(result)
        return result

    def IC_hot_w_write(self, data: list):
        # 插入数据的SQL语句
        sql_str = "REPLACE INTO t_IC_hot_w (ppn, manu"
        for index in range(1, 53):
            sql_str += f', w{index}'
        sql_str += ') VALUES (%s, %s '
        for index in range(1, 53):
            sql_str += ', %s'
        sql_str += ")"
        self.sql_write(sql_str, data)

    def IC_hot_w_read(self, filter_contend):
        query = f"SELECT * FROM t_IC_hot_w where {filter_contend}"
        result = self.sql_read(query)
        print(result)
        return result

    def ic_stock(self, data: list):
        sql_str = "REPLACE INTO t_ic_stock (ppn, manu, supplier, isICCP, isSSCP, iSRanking, isHotSell, stock_num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.sql_write(sql_str, data)

    def bom_price_write(self, data: list):
        sql_str = "REPLACE INTO t_bom_price (ppn, manu, supplier, package, lot, quoted_price, release_time, stock_num, valid_supplier) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.sql_write(sql_str, data)

    def octopart_price_write(self, data: list):
        sql_str = "REPLACE INTO t_octopart_price (ppn, manu, is_star, distribute, sku, stock, moq, currency_type,k_price, updated, opn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.sql_write(sql_str, data)

    def ppn_write(self, data: list):
        sql_str = "REPLACE INTO t_ppn (ppn, manu_id, manu_name, source) VALUES (%s, %s, %s, %s)"
        self.sql_write(sql_str, data)

    def ppn_read(self, filter_contend):
        query = f"SELECT ppn FROM t_ppn where {filter_contend}"
        result = self.sql_read(query)
        print(result)
        return result

    def opn_write(self, data: list):
        sql_str = "REPLACE INTO t_opn (opn, manu_id, manu_name) VALUES (%s, %s, %s)"
        self.sql_write(sql_str, data)

    def opn_read(self, filter_contend):
        query = f"SELECT opn FROM t_opn where {filter_contend}"
        result = self.sql_read(query)
        print(result)
        return result

    def IC_hot_adjust(self):
        cnx = self.connection_pool.get_connection()
        cursor = cnx.cursor()
        # 定义要修改的数组和新的manu值
        array1 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TTI.xlsx'), sheet_name='ppn',
                                            col_index=1)[800:900]
        new_manu = 'Texas Instruments'

        # 循环遍历数组中的值，逐行进行修改
        for ppn in array1:
            # 构建更新语句
            update_query = f"UPDATE t_ic_hot_m SET manu = '{new_manu}' WHERE ppn = '{ppn}'"
            # 执行更新语句
            cursor.execute(update_query)
            # 提交更改
            cnx.commit()
        # 关闭连接
        cursor.close()
        cnx.close()


if __name__ == "__main__":
    manager = DBRecommandChip()
    manager.octopart_price_write([['X9317UV8IZ-2.7', 'Renesas', 1, 'DigiKey Marketplace', '2156-X9317UV8IZ-2.7-ND', '0', '1', 'USD', '1.000', '2m', 'X9317UV8'], ['X9317UV8IZ-2.7', 'Renesas', 1, 'Avnet', 'X9317UV8IZ-2.7', '0', '1200', '', '', '1d', 'X9317UV8'], ['X9317UV8IZ-2.7', 'Renesas', 1, 'Newark', '79K9315', '0', '600', 'USD', '5.990', '20h', 'X9317UV8'], ['X9317UV8IZ', 'Renesas', 1, 'Avnet', 'X9317UV8IZ', '0', '800', '', '', '1d', 'X9317UV8'], ['X9317UV8IZ', 'Renesas', 1, 'Newark', '79K9314', '0', '400', 'USD', '5.180', '20h', 'X9317UV8'], ['X9317UV8IZT1', 'Renesas', 1, 'Avnet', 'X9317UV8IZT1', '0', '2500', '', '', '1d', 'X9317UV8'], ['X9317UV8IZT1', 'Renesas', 1, 'Newark', '79K9317', '0', '2500', 'USD', '', '20h', 'X9317UV8'], ['X9317UV8Z', 'Renesas', 1, 'Avnet', 'X9317UV8Z', '0', '1000', '', '', '1d', 'X9317UV8'], ['X9317UV8Z', 'Renesas', 1, 'Newark', '79K9318', '0', '500', 'USD', '4.150', '20h', 'X9317UV8'], ['X9317UV8Z-2.7', 'Renesas', 1, 'Avnet', 'X9317UV8Z-2.7', '0', '1600', '', '', '1d', 'X9317UV8'], ['X9317UV8Z-2.7', 'Renesas', 1, 'Newark', '79K9319', '0', '800', 'USD', '4.530', '20h', 'X9317UV8'], ['X9317UV8IZ-2.7T1', 'Renesas', 1, 'Avnet', 'X9317UV8IZ-2.7T1', '0', '2500', '', '', '1d', 'X9317UV8'], ['X9317UV8IZ-2.7T1', 'Renesas', 1, 'Newark', '79K9316', '0', '2500', 'USD', '', '20h', 'X9317UV8'], ['X9317UV8ZT1', 'Renesas', 1, 'Avnet', 'X9317UV8ZT1', '0', '2500', '', '', '1d', 'X9317UV8'], ['X9317UV8ZT1', 'Renesas', 1, 'Newark', '79K9321', '0', '2500', 'USD', '', '20h', 'X9317UV8'], ['X9317UV8Z-2.7T1', 'Renesas', 1, 'Avnet', 'X9317UV8Z-2.7T1', '0', '2500', '', '', '1d', 'X9317UV8'], ['X9317UV8Z-2.7T1', 'Renesas', 1, 'Newark', '79K9320', '0', '2500', 'USD', '', '20h', 'X9317UV8']])
    # IC_hot_m_read("update_time > '2023/08/15'")
    # IC_hot_w_write(
    #     [['VI-261-CU', 'Vicor', 5, 0, 4, 0, 0, 0, 0, 3, 0, 7, 2, 0, 0, 0, 5, 0, 1, 0, 0, 0, 2, 2, 2, 0, 1, 5, 0, 0, 1,
    #       10, 0, 0, 0, 5, 0, 1, 0, 6, 8, 0, 1, 0, 1, 1, 3, 5, 2, 0, 1, 0, 0, 2]]
    # )
