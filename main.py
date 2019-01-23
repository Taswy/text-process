# code=utf-8
import re
import random

class Point(object):
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    def tostring(self):
        return "{} {} ".format(self.x, self.y)

class Line(object):
    def __init__(self, id, p1_index, p2_index):
        self.id = id
        self.p1_index = p1_index
        self.p2_index = p2_index
    def tostring(self, processer, index):
        if index:
            return processer.points[self.p1_index].tostring()
        return processer.points[self.p2_index].tostring()

class LineLoop(object):
    def __init__(self, line_list):
        self.length = len(line_list)
        self.line_list = line_list
    def tostring(self, processer):
        bool_list = list(map(lambda x: x > 0, self.line_list))
        attr_list = [(processer.lines[abs(self.line_list[i])], bool_list[i]) for i in range(len(self.line_list))]
        str_list = [line.tostring(processer, index) for (line, index) in attr_list]
        return ''.join(str_list)

class Processer(object):
    start_line = "Lines & Boundaries"
    end_line = "Surfaces and physical entities"
    def __init__(self):
        self.points = {}
        self.lines = {}
        self.line_loops = []

    def set_point(self, point):
        self.points[point.id] = point
    def set_line(self, line):
        self.lines[line.id] = line
    def set_line_loop(self, line_loop):
        self.line_loops.append(line_loop)

    def display(self, dest_file):
        self.length_display(dest_file)
        self.random_serial_display(dest_file)
        self.points_display(dest_file)

    def length_display(self, dest_file):
        length_list = [line_loop.length for line_loop in self.line_loops]
        length_str = " ".join(list(map(str, length_list)))
        self.write_file(length_str, dest_file)

    def random_serial_display(self, dest_file, probability_list=[0.3, 0.6, 0.1]):
        len_list = [int(len(self.line_loops)*probability_list[i]) for i in range(len(probability_list)-1)]
        len_list.append(len(self.line_loops) - sum(len_list))
        raw_list = []
        for i in range(len(len_list)):
            raw_list += [i+1] * len_list[i] 
        random.shuffle(raw_list)
        random_str = " ".join(list(map(str, raw_list)))
        self.write_file(random_str, dest_file)

    def points_display(self, dest_file):
        for line_loop in self.line_loops:
            self.write_file(line_loop.tostring(self), dest_file)
            
    def read_obj(self, text_line):
        if text_line.strip() == '':
            return None
        class_names = ["Point", "Line", "Line Loop"]
        [obj_str, data_str] = text_line.strip().split("=")
        obj_type = None
        for class_name in class_names:
            if class_name in obj_str:
                obj_type = class_name
        if not obj_type:
            return None
        pattern = re.compile(r'[(](.*?)[)]')
        obj_id = int(re.findall(pattern, obj_str)[0])
        return obj_type, obj_id, data_str

    def set_obj(self, obj_context):
        if obj_context is None:
            return
        (obj_type, obj_id, data_str) = obj_context
        pattern = re.compile(r'[{](.*?)[}]')
        data_content_list = list(map(lambda s: s.strip(), re.findall(pattern, data_str)[0].split(',')))
        if obj_type == "Point":
            (x, y) = tuple(map(float, data_content_list[0:2]))
            point = Point(obj_id, x, y)
            self.set_point(point)
        elif obj_type == "Line":
            (p1, p2) = tuple(map(int, data_content_list))
            line = Line(obj_id, p1, p2)
            self.set_line(line)
        else:
            line_list = list(map(int, data_content_list))
            line_loop = LineLoop(line_list)
            self.set_line_loop(line_loop)
    
    def process_line(self, text_line):
        obj_context = self.read_obj(text_line)
        self.set_obj(obj_context)

    def read_file(self, file_name):
        context = []
        with open(file_name, 'r') as fo:
            context = fo.readlines()
        return context

    def write_file(self, line, dest_file):
        with open(dest_file, 'a') as fi:
            fi.write(line + '\n')

    def process(self, src_file, dest_file):
        context = self.read_file(src_file)
        readable = False
        i = 1
        for text_line in context:
            i += 1
            if self.start_line in text_line:
                readable = True
                continue
            if self.end_line in text_line:
                break
            if readable:
                self.process_line(text_line)
        self.display(dest_file)

if __name__ == "__main__":
    src_file = "neperdda.geo"
    dest_file = "out.geo"
    
    processer = Processer()
    processer.process(src_file, dest_file)