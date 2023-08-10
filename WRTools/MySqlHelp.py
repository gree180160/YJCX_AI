import mysql.connector

# 建立数据库连接
cnx = mysql.connector.connect(
    host="161.117.187.27",
    user="river",
    password="K7tXjn2jFwb8ADFD",
    database="yjcxrecoomanchip",
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
    sql_str = "INSERT INTO t_IC_hot_m (ppn, manu"
    for index in range(1, 13):
        sql_str += f', m{index}'
    sql_str += ') VALUES (%s, %s '
    for index in range(1, 13):
        sql_str += ', %s'
    sql_str += ")"
    sql_write(sql_str, data)


def IC_hot_m_read():
    query = "SELECT * FROM t_IC_hot_m"
    result = sql_read(query)
    return result


def IC_hot_w_write(data:list):
    # 插入数据的SQL语句
    sql_str = "INSERT INTO t_IC_hot_w (ppn, manu"
    for index in range(1, 53):
        sql_str += f', w{index}'
    sql_str += ') VALUES (%s, %s '
    for index in range(1, 53):
        sql_str += ', %s'
    sql_str += ")"
    sql_write(sql_str, data)


def IC_hot_w_read():
    query = "SELECT * FROM t_IC_hot_w"
    result = sql_read(query)
    return result


if __name__ == "__main__":
    IC_hot_w_write(
        [['VI-261-CU', 'Vicor', 5, 0, 4, 0, 0, 0, 0, 3, 0, 7, 2, 0, 0, 0, 5, 0, 1, 0, 0, 0, 2, 2, 2, 0, 1, 5, 0, 0, 1,
          10, 0, 0, 0, 5, 0, 1, 0, 6, 8, 0, 1, 0, 1, 1, 3, 5, 2, 0, 1, 0, 0, 2]]
    )
