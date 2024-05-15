class Course:
    def __init__(self, name, day, startTime, endTime, location) -> None:
        self.name = name
        self.day = day
        self.startTime = startTime
        self.endTime = endTime
        self.location = location
    
    def __str__(self):
        return f"課程通知\n課程名稱：{self.name}\n教室：{self.location}\n上課時間：{self.startTime}\n下課時間：{self.endTime}\n祝您上課愉快！"

class LinkedList:
    def __init__(self, value) -> None:
        self.value = value
        self.next = None

class Weather:
    def __init__(self, wx, maxT, minT, ci, pop) -> None:
        # 天氣現象
        self.wx = wx
        # 最高溫
        self.maxT = maxT
        # 最低溫
        self.minT = minT
        # 舒適度
        self.ci = ci
        # 降雨機率
        self.pop = pop

    def __str__(self):
        return f"天氣現象:{self.wx}\n降雨機率:{self.pop}%\n最低溫度:{self.minT}°C\n最高溫度:{self.maxT}°C\n舒適度:{self.ci}"