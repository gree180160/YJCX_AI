import mysql.connector
from Manager import AccManage
from WRTools import ExcelHelp, PathHelp, LogHelper

# 建立数据库连接
cnx = mysql.connector.connect(
    host=AccManage.mys['h'],
    user=AccManage.mys['n'],
    password=AccManage.mys['p'],
    database="tender_info",
    connection_timeout=180
)


def sql_write(sql, data):
    try:
        # 创建游标对象
        print(f'write data:\n {data}')
        cursor = cnx.cursor()
        # 执行插入操作
        cursor.executemany(sql, data)
        # 提交事务
        cnx.commit()
        # 关闭游标和数据库连接
        cursor.close()
    except Exception as e:
        LogHelper.write_log(log_file_name= PathHelp.get_file_path('WRTools', 'MySqlHelpLog.txt'), content=f'yjcx_recommended wirte error {e} {data}')


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


def rts_render_A(data:list):
    sql_str = "REPLACE  INTO t_rts_tender_a(No, title_ru, starting_price, application_security, contract_security, status, published, apply_data, show_data, org_name, org_TinKpp, org_contact, cus_name, cus_TinKppReg, cus_contact, cus_address, detail_url, page, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_write(sql_str, data)


def rts_render_B(data:list):
    sql_str = "REPLACE  INTO t_rts_tender_b(No, title_ru, starting_price, application_security, contract_security, status, published, apply_data, show_data, org_name, org_TinKpp, org_contact, cus_name, cus_TinKppReg, cus_contact, cus_address, detail_url, page, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_write(sql_str, data)


if __name__ == "__main__":
    rts_render_A()
