import mysql.connector
from mysql.connector import Error
from Manager import AccManage
from WRTools import ExcelHelp, PathHelp, LogHelper


class MonitorDatabaseManager:
    _instance = None

    def __new__(cls):
        config = {
            "host": AccManage.mymonitor['h'],
            "user": AccManage.mymonitor['n'],
            "password": AccManage.mymonitor['p'],
            "database": "monitor_market",
        }
        if cls._instance is None:
            cls._instance = super(MonitorDatabaseManager, cls).__new__(cls)
            cls._instance.initialize(config)
        return cls._instance

    def initialize(self, config):
        self.config = config
        self.connection = None

    def create_connection(self):
        """创建数据库连接"""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(**self.config)
                if self.connection.is_connected():
                    print("成功连接到数据库")
            except Error as e:
                print(f"连接失败: {e}")

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")

    def execute_query(self, query, params=None):
        """执行查询"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            print("查询执行成功")
        except Error as e:
            LogHelper.write_log(log_file_name=PathHelp.get_file_path('WRTools', 'MySqlHelpLog.txt'),
                                content=f'monitor wirte error: {params}')
        finally:
            cursor.close()

    def insert_monitor_ic(self, st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock):
        """插入数据到 monitor_ic 表"""
        insert_query = """  
        INSERT INTO monitor_ic (st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date)  
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)  
        """
        self.execute_query(insert_query, (st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock))

    def insert_monitor_ic_date(self, st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date):
        """插入数据到 monitor_ic 表"""
        insert_query = """  
        INSERT INTO monitor_ic (st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date)  
        VALUES (%s, %s, %s, %s, %s, %s, %s)  
        """
        self.execute_query(insert_query, (st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date))

    def insert_monitor_ics(self, records):
        """批量插入数据到 monitor_ic 表"""
        insert_query = """  
           INSERT INTO monitor_ic (st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date)
           VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)  
           """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(insert_query, records)
            self.connection.commit()
            print(f"成功插入 {cursor.rowcount} 条记录")
        except Error as e:
            LogHelper.write_log(log_file_name=PathHelp.get_file_path('WRTools', 'MySqlHelpLog.txt'),
                                content=f'monitor wirte error: {records}')
        finally:
            cursor.close()


if __name__ == "__main__":
    db_manager = MonitorDatabaseManager()
    # 创建连接
    db_manager.create_connection()
    try:
        arr = []
        result = []
        for element in arr:
            temp = [element[0], element[1], element[3], element[0], element[2], element[4]]
            result.append(temp)
        db_manager.insert_monitor_ics(result)
    except Exception as e:
        print(e)
    finally:
        db_manager.close_connection()



