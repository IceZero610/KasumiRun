# Main Gaming
import sys, os
import time
import random
sys.path.append(os.path.dirname(__file__))

from Chara import *

text = ''
def output(string):
    global text
    text += str(string)
    text += '\n'

def msgSend():
    global text
    print('---------------------')
    print(text)
    text = ''

class KasumiRunGame:

    def __init__(self, test=False, delay=True):
        self.chara = [Chara('t.json') for i in range(4)]
        for i in range(4):
            self.chara[i].name += str(i+1)
        self.destination = 60
        self.test = test
        self.delay = delay
        self.pre_selector = []


    # 开始游戏 函数将会在有胜利者出现之后return
    def start(self):
        self.turn = 0
        while 1:

            self.turn += 1

            if self.delay:
                time.sleep(1)

            self.clearingStatus()

            self.tpRecovery()

            self.skillActivate()

            self.checkWinner()

            if len(self.winners) > 0:
                return self.clearingWinner()

            self.normalMove()

            self.checkWinner()

            if len(self.winners) > 0:
                return self.clearingWinner()

            if self.test:
                self.showResult()


    # 结算状态效果
    def clearingStatus(self):
        for i in self.chara:
            i.decStatus()


    '''
    检查是否有角色到达终点 把角色写入winners
    有角色到达终点前这个winner应该是空的'''
    def checkWinner(self):
        self.winners = []
        for i in self.chara:
            if i.progress >= self.destination:
                self.winners += [i]
    
    # 稳定TP回复
    def tpRecovery(self):
        for i in self.chara:
            i.tpRecovery()       

    '''
    结算胜利结果 
    这一步可以用来统计胜率
    输出比赛结果'''
    def clearingWinner(self):
        for i in self.winners:
            output('%s获得了胜利!' % (i.name))
        msgSend()

    # 常规移动
    def normalMove(self):
        for i in self.chara:
            i.normalMove()

    # 展示跑步结果
    def showResult(self):
        output('第%d回合结果' % self.turn)
        for i in range(4):
            output('%s:   %d / 60  TP: %d' % (self.chara[i].name, self.chara[i].progress, self.chara[i].TP))
        #output('领先: %d' % self.rank[i])
        msgSend()
    '''
    调用Chara的skillActivate获取技能的发动情况
    这步之前，函数将会运行一次rankCal()来更新排名情况
    即，技能生效先后并不会影响到目标选择
    '''
    def skillActivate(self):
        self.rankCal()
        for i in range(4):
            skill_gotten = self.chara[i].skillActivate()
            if skill_gotten != None:
                for effect in skill_gotten['effect']:
                    selected = self.selector(i, effect['param'])
                    self.chara[i].useEffect(selected, effect)

                s = '%s对' % self.chara[i].name
                for item in selected:
                    s += item.name
                s += '发动了%s!' % skill_gotten['name']
                output(s)


           
    
    '''
    邪道排序(  如果有更优办法可以改一下
    做好一个rank的dict，用排名为键值可以找到对应角色在chara数组里的index
    此外 对于进度完全相同的角色 会有一点点随机的排名变化
    '''
    def rankCal(self):
        progress = []
        for item in self.chara:
            progress += [item.progress]
        t1 = {}
        t2 = []
        for i in range(4):
            temp = progress[i] * 4
            # 防止重键 随机排名变化
            while temp in t1:
                temp += random.randint(-2, 2)

            t1[temp] = i
            t2 += [temp]
        t2.sort(reverse=True)
        self.rank = {}
        for i in range(4):
            self.rank[i] = t1[t2[i]]


    '''
    选择器。 关键函数之一
    - 0——对自己生效 (不再考虑目标数量)
    - 1——优先对最靠前的其他角色生效
    - 2——仅对随机其他角色生效
    - 3——优先对最靠后的角色生效(可能是自己)
    - 4——全部角色随机生效
    - 5——使用上一次的目标选择器结果(尽量保证这个选择器之前同一个技能内已经有一条效果)

    
    函数需要传入的有：
    index: chara的角标
    param: "effect"内的"param"项
    按照 效果列表.md 所述，前两个参数分别是目标选择和目标数量
    函数将会返回一个存储了所选择到的chara数组
    如果没有任何角色被选中 则返回None
    不过从设计上来看不应该返回None
    '''
    def selector(self, index: int, param: list):

        # 防错误输入导致的死循环
        if param[1] > 4:
            self.pre_selector = []
            return []

        # 0: 对自己生效
        if param[0] == 0:
            self.pre_selector = [self.chara[index]]
            return [self.chara[index]]

        # 1: 优先对最靠前的其他角色生效
        if param[0] == 1:
            ret = []
            for i in range(4):
                temp = self.rank[i]
                # 不算上自己
                if temp != index:
                    ret += [self.chara[temp]] 

                # 人数凑够了就可以返回了
                if len(ret) >= param[1]:
                    self.pre_selector = ret
                    return ret

        # 2: 仅对随机其他角色生效
        if param[0] == 2:
            temp = random.sample([0,1,2,3], 4)
            temp.remove(index)
            self.pre_selector = [self.chara[i] for i in temp[0:param[1]]]
            return self.pre_selector

        # 3：优先对最靠后的角色生效(可能是自己)
        if param[0] == 3:
            ret = []
            for i in range(3, -1, -1):
                ret += [self.chara[self.rank[i]]] 

                # 人数凑够了就可以返回了
                if len(ret) >= param[1]:
                    self.pre_selector = ret
                    return ret

        # 4: 全部角色随机生效
        if param[0] == 4:
            temp = random.sample([0,1,2,3], 4)

            self.pre_selector = [self.chara[i] for i in temp[0:param[1]]]
            return self.pre_selector


        # 5: 使用上一次的目标选择器结果
        if param[0] == 5:
            return self.pre_selector














