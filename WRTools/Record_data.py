"""
ChipPower 数据服务客户端类
用于替代原 MySqlHelp_recommanded.DBRecommandChip，通过HTTP API写入数据

使用方法：
    from ChipPowerService.app.record_data import RecordData

    # 全局初始化一次即可（单例模式，多次调用RecordData()只会创建一个实例）
    db = RecordData()
    # 或连接远程服务：
    # db = RecordData(base_url="http://your-server:5001/api/data")

    # 之后在任何地方调用都复用同一个实例：
    result = [[...]]
    db.ic_cxyx_stock_write(result)
    db.bom_price_write(result)
    # ... 其他方法同理
"""

import time
import requests
from typing import List, Optional, Any

# local_url = "http://localhost:8001/api/data"
product_url = "http://47.236.113.155:8001/api/data"


def singleton(cls):
    """单例装饰器 - 与原history.py保持一致，但允许传入新参数重新初始化"""
    instances = {}

    def wrapper(*args, **kwargs):
        # 如果传入了参数（不是空参调用），说明要更新配置，重新创建实例
        if args or kwargs:
            instances[cls] = cls(*args, **kwargs)
            return instances[cls]
        # 空参调用：如果实例不存在则创建（使用默认参数），否则返回已存在的
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return wrapper


@singleton
class RecordData:
    """数据记录客户端类，接口与原 DBRecommandChip 保持一致（单例模式）"""

    def __init__(self, base_url: str = product_url, timeout: int = 120):
        """
        初始化客户端（单例模式，传入参数时会重新初始化）
        :param base_url: 数据服务API地址
        :param timeout: 请求超时时间（秒）
        """
        # 单例模式下，只有第一次初始化或传入新参数时才重新创建session
        if hasattr(self, '_initialized') and base_url == self.base_url:
            return
        self._initialized = True

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _post(self, endpoint: str, data: List[List[Any]], params: Optional[dict] = None, max_retries: int = 2) -> bool:
        """
        发送POST请求写入数据（兼容旧方法，带重试）
        :param endpoint: API端点
        :param data: 二维数组数据（与原方法格式一致）
        :param params: URL查询参数
        :param max_retries: 最大重试次数（默认2次，与原sql_write_twice一致）
        :return: 是否成功
        """
        url = f"{self.base_url}/{endpoint}"
        data = self._make_json_safe(data)
        print(f'\nwrite data ({endpoint}):\n {data}')

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if result.get('code') == 200:
                    print(f'{endpoint} 写入成功 (第{attempt + 1}次尝试)')
                    return True
                else:
                    last_error = f"API返回错误: {result.get('message', '未知错误')}"
                    print(f'{endpoint} 第{attempt + 1}次写入失败: {last_error}')
            except Exception as e:
                last_error = str(e)
                print(f'{endpoint} 第{attempt + 1}次写入异常: {e}')

            # 如果不是最后一次尝试，等待一下再重试
            if attempt < max_retries - 1:
                time.sleep(1)  # 重试前等待1秒

        print(f'{endpoint} 写入失败，已重试{max_retries}次，最终错误: {last_error}')
        return False

    def _post_dicts(self, endpoint: str, data: Any, params: Optional[dict] = None, max_retries: int = 2) -> bool:
        """
        发送字典/字典列表数据（推荐使用，带重试机制）
        :param endpoint: API端点
        :param data: 字典或字典列表
        :param params: URL查询参数
        :param max_retries: 最大重试次数（默认2次，与原sql_write_twice一致）
        :return: 是否成功
        """
        url = f"{self.base_url}/{endpoint}"
        data = self._make_json_safe(data)
        print(f'\nwrite data ({endpoint}):\n {data}')

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if result.get('code') == 200:
                    print(f'{endpoint} 写入成功 (第{attempt + 1}次尝试)')
                    return True
                else:
                    last_error = f"API返回错误: {result.get('message', '未知错误')}"
                    print(f'{endpoint} 第{attempt + 1}次写入失败: {last_error}')
            except Exception as e:
                last_error = str(e)
                print(f'{endpoint} 第{attempt + 1}次写入异常: {e}')

            # 如果不是最后一次尝试，等待一下再重试
            if attempt < max_retries - 1:
                time.sleep(1)  # 重试前等待1秒
        print(f'{endpoint} 写入失败，已重试{max_retries}次，最终错误: {last_error}')
        return False

    @staticmethod
    def _make_json_safe(obj):
        """
        递归将 datetime/date/Decimal 等无法直接 JSON 序列化的对象转为字符串/浮点数。
        原直连 MySQL 时 mysql.connector 能自动处理这些类型，走 service(HTTP+JSON) 后必须显式转换。
        对不含这些类型的常规 str/int/float/None 数据无影响。递归用内部闭包实现，不依赖类名。
        """
        from datetime import datetime, date
        from decimal import Decimal

        def _safe(o):
            if isinstance(o, datetime):
                return o.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(o, date):
                return o.strftime('%Y-%m-%d')
            if isinstance(o, Decimal):
                return float(o)
            if isinstance(o, dict):
                return {k: _safe(v) for k, v in o.items()}
            if isinstance(o, (list, tuple)):
                return [_safe(v) for v in o]
            return o

        return _safe(obj)

    def _get(self, endpoint: str, params: Optional[dict] = None, filter_contend: str = "") -> Optional[List]:
        """
        发送GET请求查询数据
        :param endpoint: API端点
        :param params: 查询参数
        :param filter_contend: 自定义WHERE条件字符串（兼容旧代码）
        :return: 数据列表或None
        """
        url = f"{self.base_url}/{endpoint}"

        # 合并参数
        req_params = params or {}
        if filter_contend:
            req_params['filter_contend'] = filter_contend
            print(f'\nquery data ({endpoint}), filter: {filter_contend}')
        else:
            print(f'\nquery data ({endpoint}), params: {req_params}')

        last_error = None
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=req_params, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', [])
                    print(f'{endpoint} 查询成功，返回{len(data)}条记录')
                    return data
                else:
                    last_error = f"API返回错误: {result.get('message', '未知错误')}"
                    print(f'{endpoint} 第{attempt + 1}次查询失败: {last_error}')
            except Exception as e:
                last_error = str(e)
                print(f'{endpoint} 第{attempt + 1}次查询异常: {e}')

            if attempt < max_retries - 1:
                time.sleep(1)

        print(f'{endpoint} 查询失败，已重试{max_retries}次，最终错误: {last_error}')
        return None

    def sql_write(self, sql: str, data: List, needLog: bool = True) -> bool:
        """兼容旧接口，建议使用具体的xxx_write方法"""
        # 此方法仅为兼容保留，实际应使用具体方法
        print("警告：sql_write方法已废弃，请使用具体的xxx_write方法")
        return True

    def sql_read(self, sql: str) -> List:
        """兼容旧接口，建议使用具体的xxx_read方法"""
        print("警告：sql_read方法已废弃，请使用具体的xxx_read方法")
        return []

    # ==================== Task 任务管理 ====================
    def task_write(self, data: List[List[Any]]) -> bool:
        """
        写入任务数据
        data格式: [[Tname, Tdes, Tstate, Tlevel], ...]
        Tname: str, Tdes: str, Tstate: int, Tlevel: int
        """
        dicts = [{'Tname': row[0], 'Tdes': row[1], 'Tstate': row[2], 'Tlevel': row[3]} for row in data]
        return self._post_dicts('task/write', dicts)

    def task_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('task/read', filter_contend=filter_contend)

    # ==================== IC Hot Monthly 月热度 ====================
    def IC_hot_m_write(self, data: List[List[Any]]) -> bool:
        """
        写入IC月热度数据
        data格式: [[ppn, manu, m1, m2, ..., m12, task_name], ...]
        """
        dicts = []
        for row in data:
            item = {'ppn': row[0], 'manu': row[1], 'task_name': row[14] if len(row) > 14 else ''}
            for i in range(12):
                item[f'm{i + 1}'] = row[i + 2] if i + 2 < len(row) else 0
            dicts.append(item)
        return self._post_dicts('ic_hot_m/write', dicts)

    def IC_hot_m_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_hot_m/read', filter_contend=filter_contend)

    # ==================== IC Hot Weekly 周热度 ====================
    def IC_hot_w_write(self, data: List[List[Any]]) -> bool:
        """
        写入IC周热度数据
        data格式: [[ppn, manu, w1, w2, ..., w52, task_name], ...]
        """
        dicts = []
        for row in data:
            item = {'ppn': row[0], 'manu': row[1], 'task_name': row[54] if len(row) > 54 else ''}
            for i in range(52):
                item[f'w{i + 1}'] = row[i + 2] if i + 2 < len(row) else 0
            dicts.append(item)
        return self._post_dicts('ic_hot_w/write', dicts)

    def IC_hot_w_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_hot_w/read', filter_contend=filter_contend)

    # ==================== IC Price Demand 价格需求 ====================
    def ic_price_demand_write(self, data: List[List[Any]]) -> bool:
        """
        写入IC价格需求数据
        data格式: [[ppn, manu, price, month_search_count, supplierCount, cp_count, rank_count, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'price': row[2], 'month_search_count': row[3],
                  'supplierCount': row[4], 'cp_count': row[5], 'rank_count': row[6], 'task_name': row[7]}
                 for row in data]
        return self._post_dicts('ic_price_demand/write', dicts)

    def ic_price_demand_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_price_demand/read', filter_contend=filter_contend)

    # ==================== CXYX Stock 有样小芯库存 ====================
    def ic_cxyx_stock_write(self, data: List[List[Any]]) -> bool:
        """
        写入有样小芯库存数据
        data格式: [[supplier_name, model, brand, category, price_step, stock_num, batch_info, task_name], ...]
        """
        dicts = [{'supplier_name': row[0], 'model': row[1], 'brand': row[2], 'category': row[3],
                  'price_step': row[4], 'stock_num': row[5], 'batch_info': row[6], 'task_name': row[7]}
                 for row in data]
        return self._post_dicts('cxyx_stock/write', dicts)

    def ic_cxyx_stock_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('cxyx_stock/read', filter_contend=filter_contend)

    # ==================== IC Stock IC库存 ====================
    def ic_stock(self, data: List[List[Any]]) -> bool:
        """
        写入IC库存数据
        data格式: [[ppn, st_manu, supplier_ppn, supplier_manu, supplier, isICCP, isSSCP, iSRanking, isHotSell, isYouXian, batch, pakaging, stock_num, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'st_manu': row[1], 'supplier_ppn': row[2], 'supplier_manu': row[3],
                  'supplier': row[4], 'isICCP': row[5], 'isSSCP': row[6], 'iSRanking': row[7],
                  'isHotSell': row[8], 'isYouXian': row[9], 'batch': row[10], 'pakaging': row[11],
                  'stock_num': row[12], 'task_name': row[13]} for row in data]
        return self._post_dicts('ic_stock/write', dicts)

    def ic_stock_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_stock/read', filter_contend=filter_contend)

    # ==================== IC Des IC描述 ====================
    def ic_des_write(self, data: List[List[Any]]) -> bool:
        """
        写入IC描述数据
        data格式: [[ppn, manu, todaySearch, todaySearch_person, yesterdaySearch, yesterdaySearch_person, reference_price, week_search, market_hot, risk, mainLand_stock, international_stock, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'todaySearch': row[2], 'todaySearch_person': row[3],
                  'yesterdaySearch': row[4], 'yesterdaySearch_person': row[5], 'reference_price': row[6],
                  'week_search': row[7], 'market_hot': row[8], 'risk': row[9], 'mainLand_stock': row[10],
                  'international_stock': row[11], 'task_name': row[12]} for row in data]
        return self._post_dicts('ic_des/write', dicts)

    def ic_des_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_des/read', filter_contend=filter_contend)

    # ==================== HQ Stock 华强库存 ====================
    def hq_stock_write(self, data: List[List[Any]]) -> bool:
        """
        写入华强库存数据
        data格式: [[ppn, std_manu, supplier, sup_ppn, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'std_manu': row[1], 'supplier': row[2], 'sup_ppn': row[3],
                  'sup_manu': row[4], 'batch': row[5], 'stock': row[6], 'packing': row[7],
                  'param': row[8], 'place': row[9], 'instruction': row[10], 'publish_date': row[11],
                  'task_name': row[12]} for row in data]
        return self._post_dicts('hq_stock/write', dicts)

    def hq_stock_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('hq_stock/read', filter_contend=filter_contend)

    # ==================== HQ Hot 华强热度 ====================
    def hq_hot_write(self, data: List[List[Any]]) -> bool:
        """
        写入华强热度数据
        data格式: [[ppn, manu, week_hot, month_hot, week_price, month_stock, week_price, month_price, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1],
                  'week_hot': row[2], 'month_hot': row[3],
                  'week_stock': row[4], 'month_stock': row[5],
                  'week_price': row[6], 'month_price': row[7],
                  'task_name': row[8]}
                 for row in data]
        return self._post_dicts('hq_hot/write', dicts)

    def hq_hot_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('hq_hot/read', filter_contend=filter_contend)

    def query_ppn_by_models(self, model_list: List[str]) -> List:
        """根据型号列表查询华强热度数据"""
        try:
            response = self.session.post(f"{self.base_url}/hq_hot/query_by_models",
                                         json={'models': model_list}, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            if result.get('code') == 200:
                return [[item.get('ppn'), item.get('manu'),
                         item.get('week_hot'), item.get('month_hot'),
                         item.get('week_stock'), item.get('month_stock'),
                         item.get('week_price'), item.get('month_price'),
                         ]
                        for item in result.get('data', [])]
            return [[model, '--', '--', '--', '--', '--', '--', '--'] for model in model_list]
        except Exception as e:
            print(f"query_ppn_by_models失败: {e}")
            return [[model, '--', '--', '--', '--', '--', '--', '--'] for model in model_list]

    # ==================== EFind Stock 维库库存 ====================
    def efind_stock_write(self, data: List[List[Any]]) -> bool:
        """
        写入维库库存数据
        data格式: [[ppn, manu, sup_manu, supplier, publish_date, info, price, stock, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'sup_manu': row[2], 'supplier': row[3],
                  'publish_date': row[4], 'info': row[5], 'price': row[6], 'stock': row[7],
                  'task_name': row[8]} for row in data]
        return self._post_dicts('efind_stock/write', dicts)

    def efind_stock_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('efind_stock/read', filter_contend=filter_contend)

    # ==================== EFind Supplier 维库供应商 ====================
    def efind_supplier_write(self, data: List[List[Any]]) -> bool:
        """
        写入维库供应商数据
        data格式: [[ppn, manu, all_supplier, price_supplier, stock_supplier, stock, middle_price, min_price, max_price, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'all_supplier': row[2], 'price_supplier': row[3],
                  'stock_supplier': row[4], 'stock': row[5], 'middle_price': row[6], 'min_price': row[7],
                  'max_price': row[8], 'task_name': row[9]} for row in data]
        return self._post_dicts('efind_supplier/write', dicts)

    def efind_supplier_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('efind_supplier/read', filter_contend=filter_contend)

    # ==================== BOM Price BOM价格 ====================
    def bom_price_write(self, data: List[List[Any]]) -> bool:
        """
        写入BOM价格数据
        data格式: [[ppn, manu, supplier, package, lot, quoted_price, release_time, stock_num, valid_supplier, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'supplier': row[2], 'package': row[3],
                  'lot': row[4], 'quoted_price': row[5], 'release_time': row[6], 'stock_num': row[7],
                  'valid_supplier': row[8], 'task_name': row[9]} for row in data]
        return self._post_dicts('bom_price/write', dicts)

    def bom_price_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('bom_price/read', filter_contend=filter_contend)

    # ==================== Octopart Price Octopart价格 ====================
    def octopart_price_write(self, data: List[List[Any]]) -> bool:
        """
        写入Octopart价格数据
        data格式: [[ppn, manu, is_star, distribute, sku, stock, moq, currency_type, k_price, updated, opn, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'is_star': row[2], 'distribute': row[3],
                  'sku': row[4], 'stock': row[5], 'moq': row[6], 'currency_type': row[7],
                  'k_price': row[8], 'updated': row[9], 'opn': row[10], 'task_name': row[11]} for row in data]
        return self._post_dicts('octopart_price/write', dicts)

    def octopart_price_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('octopart_price/read', filter_contend=filter_contend)

    # ==================== Octopart Market Octopart市场 ====================
    def octopart_market_write(self, data: List[List[Any]]) -> bool:
        """
        写入Octopart市场数据
        data格式: [[ppn, manu, des, distribute, stock, currency_type, k_price, stock_pic, opn, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'des': row[2], 'distribute': row[3],
                  'stock': row[4], 'currency_type': row[5], 'k_price': row[6], 'stock_pic': row[7],
                  'opn': row[8], 'task_name': row[9]} for row in data]
        return self._post_dicts('octopart_market/write', dicts)

    def octopart_market_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('octopart_market/read', filter_contend=filter_contend)

    # ==================== Octopart Info Octopart详情 ====================
    def octopart_info_write(self, data: List[List[Any]]) -> bool:
        """
        写入Octopart详情数据
        data格式: [[ppn, manu, des, distribute, stock, currency_type, k_price, opn, stock_data, tech_data, supplier_data, task_name], ...]
        """
        dicts = [{'ppn': row[0], 'manu': row[1], 'des': row[2], 'distribute': row[3],
                  'stock': row[4], 'currency_type': row[5], 'k_price': row[6], 'opn': row[7],
                  'stock_data': row[8], 'tech_data': row[9], 'supplier_data': row[10], 'task_name': row[11]}
                 for row in data]
        return self._post_dicts('octopart_info/write', dicts)

    def octopart_info_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('octopart_info/read', filter_contend=filter_contend)

    # ==================== FindChip Stock FindChips库存 ====================
    def findchip_stock_write(self, data: List[List[Any]]) -> bool:
        """
        写入FindChips库存数据
        data格式: [[ppn, manu, supplier, authorized, part_url, stock_str, task_name], ...]
        注意：原history.py中SQL少写了task_name参数，这里已修复
        """
        dicts = []
        for row in data:
            item = {'ppn': row[0], 'manu': row[1], 'supplier': row[2], 'authorized': row[3],
                    'part_url': row[4], 'stock_str': row[5]}
            if len(row) > 6:
                item['task_name'] = row[6]
            else:
                item['task_name'] = ''
            dicts.append(item)
        return self._post_dicts('findchip_stock/write', dicts)

    def findchip_stock_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('findchip_stock/read', filter_contend=filter_contend)

    # ==================== Digikey Attr Digikey属性 ====================
    def digikey_attr_write(self, data: List[List[Any]]) -> bool:
        """
        写入Digikey属性数据
        data格式: [[ppn, manu, digi_key_code, manu_code, des, delivery_time, detail_des, category, serial, package, status, kind, single_channel, voltage_reverse, voltage_breakdown, voltage_ipp, peakCurrentPulse, peakPowerPulse, protect_power, apply, capacitance, operating_temperature, install_kind, shell, supplier_packeage, product_code, task_name], ...]
        """
        keys = ['ppn', 'manu', 'digi_key_code', 'manu_code', 'des', 'delivery_time', 'detail_des',
                'category', 'serial', 'package', 'status', 'kind', 'single_channel', 'voltage_reverse',
                'voltage_breakdown', 'voltage_ipp', 'peakCurrentPulse', 'peakPowerPulse', 'protect_power',
                'apply', 'capacitance', 'operating_temperature', 'install_kind', 'shell', 'supplier_packeage',
                'product_code', 'task_name']
        dicts = [dict(zip(keys, row)) for row in data]
        return self._post_dicts('digikey_attr/write', dicts)

    def digikey_attr_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('digikey_attr/read', filter_contend=filter_contend)

    # ==================== Wheat Record 小麦记录 ====================
    def wheat_record_write(self, data: List[List[Any]], isRU: bool = False) -> bool:
        """
        写入小麦记录
        data格式: [[keyword, records, task_name], ...]
        isRU: 是否是俄罗斯数据
        """
        dicts = []
        for row in data:
            if isRU:
                dicts.append({'keyword': row[0], 'ru_records': row[1], 'task_name': row[2] if len(row) > 2 else ''})
            else:
                dicts.append({'keyword': row[0], 'all_records': row[1], 'task_name': row[2] if len(row) > 2 else ''})
        return self._post_dicts('wheat_record/write', dicts, params={'is_ru': str(isRU).lower()})

    def wheat_record_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('wheat_record/read', filter_contend=filter_contend)

    # ==================== Wheat Buyer 小麦买家 ====================
    def wheat_buyer_write(self, data: List[List[Any]]) -> bool:
        """
        写入小麦买家数据
        data格式: [[keyword, wheat_date, buyer, supplier, HSCode, description, buy_country, supplier_country, productContry, weight, number, totalValue, current_page, task_name], ...]
        """
        keys = ['keyword', 'wheat_date', 'buyer', 'supplier', 'HSCode', 'description', 'buy_country',
                'supplier_country', 'productContry', 'weight', 'number', 'totalValue', 'current_page', 'task_name']
        dicts = [dict(zip(keys, row)) for row in data]
        return self._post_dicts('wheat_buyer/write', dicts)

    def wheat_buyer_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('wheat_buyer/read', filter_contend=filter_contend)

    # ==================== Rusprofile 俄罗斯公司 ====================
    def rusprofile_write(self, data: List[List[Any]]) -> bool:
        """
        写入俄罗斯公司数据
        data格式: [[company_name, profile_id, full_name, inn, activity, register_date, industry_rank, company_address, phone, email, website, revenue, profit, cost, task_name], ...]
        """
        keys = ['company_name', 'profile_id', 'full_name', 'inn', 'activity', 'register_date',
                'industry_rank', 'company_address', 'phone', 'email', 'website', 'revenue', 'profit', 'cost',
                'task_name']
        dicts = [dict(zip(keys, row)) for row in data]
        return self._post_dicts('rusprofile/write', dicts)

    def rusprofile_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('rusprofile/read', filter_contend=filter_contend)

    # ==================== Future 富昌电子 ====================
    def future_info_write(self, data: List[List[Any]]) -> bool:
        """
        写入富昌电子数据
        data格式: [[st_part, st_manu, f_ppn, f_manu, OnOrder, stock, leadTime, unitPrice, task_name], ...]
        """
        dicts = [{'st_part': row[0], 'st_manu': row[1], 'f_ppn': row[2], 'f_manu': row[3],
                  'OnOrder': row[4], 'stock': row[5], 'leadTime': row[6], 'unitPrice': row[7],
                  'task_name': row[8]} for row in data]
        return self._post_dicts('future_info/write', dicts)

    def future_info_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('future_info/read', filter_contend=filter_contend)

    # ==================== Arrow 艾睿电子 ====================
    def arrow_info_write(self, data: List[List[Any]]) -> bool:
        """
        写入艾睿电子数据
        data格式: [[st_part, st_manu, a_ppn, a_manu, stock, leadTime, price, batch, task_name], ...]
        """
        dicts = [{'st_part': row[0], 'st_manu': row[1], 'a_ppn': row[2], 'a_manu': row[3],
                  'stock': row[4], 'leadTime': row[5], 'price': row[6], 'batch': row[7],
                  'task_name': row[8]} for row in data]
        return self._post_dicts('arrow_info/write', dicts)

    def arrow_info_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('arrow_info/read', filter_contend=filter_contend)

    # ==================== PPN 型号库 ====================
    def ppn_write(self, data: List[List[Any]]) -> bool:
        """
        写入PPN型号数据
        data格式: [[ppn, manu_id, manu_name, source, note], ...]
        note 可选,缺省为空字符串
        """
        dicts = [{'ppn': row[0], 'manu_id': row[1], 'manu_name': row[2],
                  'source': row[3], 'note': row[4] if len(row) > 4 else ''} for row in data]
        return self._post_dicts('ppn/write', dicts)

    def ppn_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ppn/read', filter_contend=filter_contend)

    # ==================== OPN 原厂型号 ====================
    def opn_write(self, data: List[List[Any]]) -> bool:
        """
        写入OPN型号数据
        data格式: [[opn, manu_id, manu_name], ...]
        """
        dicts = [{'opn': row[0], 'manu_id': row[1], 'manu_name': row[2]} for row in data]
        return self._post_dicts('opn/write', dicts)

    def opn_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('opn/read', filter_contend=filter_contend)

    # ==================== 健康检查 ====================
    def health_check(self) -> bool:
        """检查服务是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

    # ==================== Monitor IC 监控芯片库存 (monitor_market库) ====================
    def monitor_ic_write(self, data: List[List[Any]]) -> bool:
        """
        写入监控芯片库存数据
        data格式: [[st_ppn, st_manu, supplier, sup_ppn, sup_manu, sup_stock, m_date], ...]
        m_date: 日期字符串如 "2024-06-25"，传None则使用当天日期
        """
        from datetime import date
        dicts = []
        for row in data:
            m_date = row[6] if len(row) > 6 and row[6] else date.today().strftime('%Y-%m-%d')
            dicts.append({
                'st_ppn': row[0], 'st_manu': row[1], 'supplier': row[2],
                'sup_ppn': row[3], 'sup_manu': row[4], 'sup_stock': row[5],
                'm_date': m_date
            })
        return self._post_dicts('monitor_ic/write', dicts)

    def monitor_ic_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('monitor_ic/read', filter_contend=filter_contend)

    # ==================== IC Supplier Info 供应商信息 (monitor_market库) ====================
    def ic_supplier_info_write(self, data: List[List[Any]]) -> bool:
        """
        写入IC供应商信息数据
        data格式: [[name, age, address, hot, qq, tel, phone], ...]
        name: 供应商名称（唯一键，冲突时更新其他字段）
        """
        dicts = [{'name': row[0], 'age': row[1], 'address': row[2], 'hot': row[3],
                  'qq': row[4], 'tel': row[5], 'phone': row[6]} for row in data]
        return self._post_dicts('ic_supplier_info/write', dicts)

    def ic_supplier_info_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('ic_supplier_info/read', filter_contend=filter_contend)

    # ==================== RTS Tender 招标数据 (tender_info库) ====================
    _TENDER_FIELDS = [
        'No', 'title_ru', 'starting_price', 'application_security', 'contract_security',
        'status', 'published', 'apply_data', 'show_data', 'org_name', 'org_TinKpp',
        'org_contact', 'cus_name', 'cus_TinKppReg', 'cus_contact', 'cus_address',
        'detail_url', 'page', 'update_time'
    ]

    def rts_tender_a_write(self, data: List[List[Any]]) -> bool:
        """
        写入 t_rts_tender_a 表
        data格式: [[No, title_ru, starting_price, ..., page, update_time], ...] 共19个字段
        """
        if not data:
            print('[rts_tender_a_write] 数据为空，跳过写入')
            return True
        dicts = [dict(zip(self._TENDER_FIELDS, row)) for row in data]
        return self._post_dicts('rts_tender_a/write', dicts)

    def rts_tender_a_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('rts_tender_a/read', filter_contend=filter_contend)

    def rts_tender_b_write(self, data: List[List[Any]]) -> bool:
        """
        写入 t_rts_tender_b 表
        data格式: [[No, title_ru, starting_price, ..., page, update_time], ...] 共19个字段
        """
        if not data:
            print('[rts_tender_b_write] 数据为空，跳过写入')
            return True
        dicts = [dict(zip(self._TENDER_FIELDS, row)) for row in data]
        return self._post_dicts('rts_tender_b/write', dicts)

    def rts_tender_b_read(self, filter_contend: str = "") -> Optional[List]:
        return self._get('rts_tender_b/read', filter_contend=filter_contend)


# 兼容旧的导入方式，提供一个与原类名相同的别名
DBRecommandChip = RecordData
