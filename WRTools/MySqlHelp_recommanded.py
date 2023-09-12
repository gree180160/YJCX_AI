import mysql.connector
from Manager import AccManage
from WRTools import ExcelHelp, PathHelp

# 建立数据库连接
cnx = mysql.connector.connect(
    host=AccManage.mys['h'],
    user=AccManage.mys['n'],
    password=AccManage.mys['p'],
    database="yjcx_recommended",
    connection_timeout=60
)


def sql_write(sql, data):
    # 创建游标对象
    print(f'write data:\n {data}')
    cursor = cnx.cursor()
    # 执行插入操作
    cursor.executemany(sql, data)
    # 提交事务
    cnx.commit()
    # 关闭游标和数据库连接
    cursor.close()


def sql_read(sql):
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
    print(f'read data:\n {data_list}')
    return data_list


# 输入二维数组
def IC_hot_m_write(data: list):
    # 插入数据的SQL语句
    # 插入数据的SQL语句
    sql_str = "REPLACE INTO t_IC_hot_m (ppnManu, ppn, manu"
    for index in range(1, 13):
        sql_str += f', m{index}'
    sql_str += ') VALUES (%s, %s, %s '
    for index in range(1, 13):
        sql_str += ', %s'
    sql_str += ")"
    sql_write(sql_str, data)


def IC_hot_m_read(filter_contend):
    query = f"SELECT * FROM t_IC_hot_m where {filter_contend}"
    result = sql_read(query)
    print(result)
    return result


def IC_hot_w_write(data:list):
    # 插入数据的SQL语句
    sql_str = "REPLACE INTO t_IC_hot_w (ppnManu, ppn, manu"
    for index in range(1, 53):
        sql_str += f', w{index}'
    sql_str += ') VALUES (%s, %s, %s '
    for index in range(1, 53):
        sql_str += ', %s'
    sql_str += ")"
    sql_write(sql_str, data)


def IC_hot_w_read(filter_contend):
    query = f"SELECT * FROM t_IC_hot_w where {filter_contend}"
    result = sql_read(query)
    print(result)
    return result


def octopart_price_write(data:list):
    sql_str = "REPLACE INTO t_octopart_price (ppnManu, ppn, manu, is_star, distribute, sku, stock, moq, currency_type,k_price, updated, opn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_write(sql_str, data)


def ppn_write(data:list):
    sql_str = "REPLACE INTO t_ppn (ppnManu, ppn, manu_id, manu_name, source) VALUES (%s, %s, %s, %s, %s)"
    sql_write(sql_str, data)


def ppn_read(filter_contend):
    query = f"SELECT ppn FROM t_ppn where {filter_contend}"
    result = sql_read(query)
    print(result)
    return result


def IC_hot_adjust():
    cursor = cnx.cursor()
    # 定义要修改的数组和新的manu值
    array1 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TTI.xlsx'), sheet_name='ppn', col_index=1)[800:900]
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


if __name__ == "__main__":
    ppn_list = ppn_read('1')
    print(ppn_list)
    # IC_hot_m_read("update_time > '2023/08/15'")
    # IC_hot_w_write(
    #     [['VI-261-CU', 'Vicor', 5, 0, 4, 0, 0, 0, 0, 3, 0, 7, 2, 0, 0, 0, 5, 0, 1, 0, 0, 0, 2, 2, 2, 0, 1, 5, 0, 0, 1,
    #       10, 0, 0, 0, 5, 0, 1, 0, 6, 8, 0, 1, 0, 1, 1, 3, 5, 2, 0, 1, 0, 0, 2]]
    # )
