import time
import re


class Arrow_transition_info:
    def __init__(self, cate, manufacture, ManuPartNum, public_str, buffer_str, multiple_str, spq_str, pipeline_all_info, lead_time):
        self.cate = cate
        self.manufacture = manufacture  # 来自当前网页
        self.ManuPartNum = ManuPartNum
        self.public = get_number(source_str=public_str, name='Public')
        self.buffer = get_number(source_str=buffer_str, name='Buffer')
        self.multiple = get_number(source_str=multiple_str, name='Multiple')
        self.spq = get_number(source_str=spq_str, name='SPQ')
        self.inventory_str = public_str + buffer_str + multiple_str + spq_str
        if pipeline_all_info is not None and len(pipeline_all_info) > 0 and pipeline_all_info != '--':
            pip_list = pipeline_all_info.split(' ')
            if len(pip_list) >= 1:
                self.pipeline = pip_list[0]
                self.pip_quantity = pip_list[-1]
        else:
            self.pipeline = '--'
            self.pip_quantity = '--'
        self.lead_time = lead_time
        self.search_date = time.strftime('%Y-%m-%d', time.localtime())

    def description_str(self):
        result = f'{self.cate or "--"}, {self.manufacture or "--"}, {self.ManuPartNum}, {self.public}, {self.buffer}, {self.multiple}, {self.spq}, {self.inventory_str}, {self.pipeline}, {self.pip_quantity}, {self.lead_time}, {self.search_date}'
        return result

    def descritpion_arr(self):
        result = [self.cate or "--", self.manufacture or "--", self.ManuPartNum, self.public, self.buffer, self.multiple, self.spq,
                  self.pipeline, self.pip_quantity, self.inventory_str, self.lead_time, self.search_date]
        return result


# get string get num for public&buffer&multiple&spq
def get_number(source_str, name):
    result = '--'
    if source_str.startswith(name):
        result = ''.join(re.findall('[0-9]', source_str))
    return result