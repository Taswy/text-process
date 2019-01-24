# code=utf-8
import re
import random

class Point(object):
    """Point对象,包含id, x, y三个属性"""
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    def tostring(self):
        """返回对应的字符串:x y """
        return "{} {} ".format(self.x, self.y)

class Line(object):
    """Line对象,包含id, p1, p2,其中p1和p2是Line对象的两个端点"""
    def __init__(self, id, p1_index, p2_index):
        self.id = id
        self.p1_index = p1_index
        self.p2_index = p2_index
    def tostring(self, processer, index):
        """返回对应的字符串, processer是Processer的对象, index是一bool值,用来选择p1断电还是p2端点"""
        if index:
            return processer.points[self.p1_index].tostring()
        return processer.points[self.p2_index].tostring()

class LineLoop(object):
    """Line Loop对象,包含字段length: line对象的个数, line_list: Line对象的列表"""
    def __init__(self, line_list):
        self.length = len(line_list)
        self.line_list = line_list
    def tostring(self, processer):
        """返回这一行Line的点的字符串"""
        bool_list = list(map(lambda x: x > 0, self.line_list)) # 根据line_list的正负号返回bool值的列表
        attr_list = [(processer.lines[abs(self.line_list[i])], bool_list[i]) for i in range(len(self.line_list))] # attr列表,每个attr是一个两元组,包含Line对象的id,和为选取Line中端点的bool值
        str_list = [line.tostring(processer, index) for (line, index) in attr_list] # str_list:用上述attr_list中的元素调用Line.tostring方法获取每个Line对象的处理后的字符串,然后构成列表
        return ''.join(str_list) # 将上述列表构成一行字符串,并将其返回

class Processer(object):
    """Processer对象,对文本进行读取,处理和输出的类"""
    start_line = "Lines & Boundaries"  # 开始读取的关键语句
    end_line = "Surfaces and physical entities" # 结束读取的关键语句
    def __init__(self, probability_list=[0.3, 0.6, 0.1]):
        """对象初始化函数, 根据probability_list字段调整第二行输出元素的概率,Processer对象存储了读取后的LineLoop列表,Line和Point字典"""
        self.probability_list=probability_list
        self.points = {}
        self.lines = {}
        self.line_loops = []

    """三个set方法用来将新读取的元素存储在对象的集合或字典中,便于以后使用"""
    def set_point(self, point):
        self.points[point.id] = point
    def set_line(self, line):
        self.lines[line.id] = line
    def set_line_loop(self, line_loop):
        self.line_loops.append(line_loop)

    def display(self, dest_file):
        """通过display方法完成所有的输出过程"""
        self.length_display(dest_file)
        self.random_serial_display(dest_file)
        self.points_display(dest_file)

    def length_display(self, dest_file):
        """第一行数据"""
        length_list = [line_loop.length for line_loop in self.line_loops]
        length_str = " ".join(list(map(str, length_list)))  # 将获取每一个line的长度转化为一行字符串
        self.write_file(length_str, dest_file)

    def random_serial_display(self, dest_file):
        """第二行数据"""
        len_list = [int(len(self.line_loops)*self.probability_list[i]) for i in range(len(self.probability_list)-1)]
        len_list.append(len(self.line_loops) - sum(len_list))   # 前两行代码计算每种元素(1,2,3)的个数
        # 创建有序的序列
        raw_list = []
        for i in range(len(len_list)):
            raw_list += [i+1] * len_list[i] 
        random.shuffle(raw_list)  # 将有序的序列乱序
        random_str = " ".join(list(map(str, raw_list))) # 组成一个字符串
        self.write_file(random_str, dest_file)

    def points_display(self, dest_file):
        """剩余N行数据"""
        for line_loop in self.line_loops:
            self.write_file(line_loop.tostring(self), dest_file) # 输出每行数据(每行数据的字符串通过line_loop.tostring(processer)方法获得)
            
    def read_obj(self, text_line):
        """根据一行数据读取对象的属性"""
        if text_line.strip() == '':
            return None
        class_names = ["Point", "Line", "Line Loop"]
        [obj_str, data_str] = text_line.strip().split("=") # 通过"="对字符串进行分割
        # 判断是哪种对象
        obj_type = None
        for class_name in class_names:
            if class_name in obj_str:
                obj_type = class_name
        if not obj_type:
            return None
        # 通过正则匹配,获取对象的id
        pattern = re.compile(r'[(](.*?)[)]')
        obj_id = int(re.findall(pattern, obj_str)[0])
        return obj_type, obj_id, data_str

    def set_obj(self, obj_context):
        """读完每一行后,若发现包含对象元素,那么就将其封装成对象"""
        if obj_context is None:
            return
        (obj_type, obj_id, data_str) = obj_context
        # 根据正则匹配获取元素的内容
        pattern = re.compile(r'[{](.*?)[}]')
        data_content_list = list(map(lambda s: s.strip(), re.findall(pattern, data_str)[0].split(',')))
        if obj_type == "Point":
            (x, y) = tuple(map(float, data_content_list[0:2])) # 获取Point的x,y两个值
            point = Point(obj_id, x, y) #建立对象
            self.set_point(point) # 存储对象
        elif obj_type == "Line":
            (p1, p2) = tuple(map(int, data_content_list)) #获取Line的定点p1, p2的值
            line = Line(obj_id, p1, p2) #建立对象
            self.set_line(line)
        else:
            line_list = list(map(int, data_content_list)) #获取LineLoop中的Line的id,并以整数列表的形式输出
            line_loop = LineLoop(line_list) #建立对象
            self.set_line_loop(line_loop) # 存储对象
    
    def process_line(self, text_line):
        """对每一行文本进行处理,处理之后将会对内含的对象进行存储"""
        obj_context = self.read_obj(text_line)
        self.set_obj(obj_context)

    def read_file(self, file_name):
        """打开文件并将所有的内容以行为单位读取到列表中"""
        context = []
        with open(file_name, 'r') as fo:
            context = fo.readlines()
        return context

    def write_file(self, line, dest_file):
        """将字符串写入到目标文件,并在最后加一个换行"""
        with open(dest_file, 'a') as fi:
            fi.write(line + '\n')

    def process(self, src_file, dest_file):
        """对源文件进行处理,并将结果输出到目标文件"""
        context = self.read_file(src_file)  #读入
        readable = False #读入开始关键语句时,将readable设置为True,并且其后的行都会准许进行处理过程
        i = 1
        # 读取每一行,并进行处理
        for text_line in context:
            i += 1
            if self.start_line in text_line:
                readable = True
                continue
            if self.end_line in text_line:
                break
            if readable:
                self.process_line(text_line)
        self.display(dest_file) #输出

if __name__ == "__main__":
    src_file = "neperdda.geo" # 输入文件
    dest_file = "out.geo" # 输出文件
    
    processer = Processer()  #可以调用　processer = Processer([0.3, 0.6, 0.1]）修改概率，默认就是0.3 0.6 0.1
    processer.process(src_file, dest_file) # 调用processer.process函数处理文件

