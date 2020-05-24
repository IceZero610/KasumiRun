# Character Class
import os
import json
import random

class Chara:
    # 通过传入文件名 读入对应的角色Json文档进行初始化
    def __init__(self, name: str):
        # 读文件
        with open('%s/chara/%s' % (os.path.dirname(__file__), name), 'r', encoding='utf-8') as f:
            self.json_data = json.loads(f.read())

        # 搬运数据
        self.name = self.json_data['name']
        self.icon = self.json_data['icon']
        self.speed = self.json_data['speed']
        self.UB = self.json_data['UB']
        self.skill_1 = self.json_data['skill_1']
        self.skill_2 = self.json_data['skill_2']
        del self.json_data

        # 其他数据  
        self.status = {}                        # 此处存储状态效果
        self.TP = random.randint(10, 40)         # 当前TP
        self.skill_1['curr_cool_down'] = 0      # 当前冷却时间  0表示可用
        self.skill_2['curr_cool_down'] = 0
        self.skill_1['dynamic_rate'] = 1        # 技能发动的动态倍率
        self.skill_2['dynamic_rate'] = 1
        self.progress = 0                       # 跑步的进度

    # 随机池内获取前进步数
    def getStepRandom(self):
        return random.choice(self.speed)

    def tpRecovery(self):
        self.TP += random.randint(12, 28)

    '''
    看看这个回合又发动了什么(
    这里就算作技能发动了 所以进CD 减次数 消耗TP都要在这里体现出来
    '''
    def skillActivate(self) -> dict:
        # 确认状态里没有沉默
        if 'SILENCE' in self.status:
            # 这里暂定返回一个None，以后可能会额外返回提示信息(？)
            return None

        # 优先检查UB是否发动
        if self.TP >= 200:
            self.TP = 0
            return self.UB

        # 考虑技能1 要求没进CD 有足够的TP 还有剩余使用次数
        if self.skill_1['curr_cool_down'] <= 0 and self.skill_1['times_limit'] > 0 and self.TP >= self.skill_1['TP_expend']:
            if self.getSkillRandom(1):
                self.skill_1['curr_cool_down'] = self.skill_1['cool_down']
                self.skill_1['times_limit'] -= 1
                self.TP -= self.skill_1['TP_expend']
                return self.skill_1

        # 考虑技能2 要求同上
        if self.skill_2['curr_cool_down'] <= 0 and self.skill_2['times_limit'] > 0 and self.TP >= self.skill_2['TP_expend']:
            if self.getSkillRandom(2):
                self.skill_2['curr_cool_down'] = self.skill_2['cool_down']
                self.skill_2['times_limit'] -= 1
                self.TP -= self.skill_2['TP_expend']
                return self.skill_2

        # 什么都没发动
        return None


    # 常规移动
    def normalMove(self):
        if 'STUN' in self.status.keys():
            return

        self.moveForward(self.getStepRandom())


    # 技能动态概率 skill_id只有1和2两种输入
    def getSkillRandom(self, skill_id: int):

        if skill_id == 1:
            skill = self.skill_1
        elif skill_id == 2:
            skill = self.skill_2
        else:
            return None

        if random.random() < skill['prob'] * skill['dynamic_rate']:
            # 触发大前进后重置概率倍率
            skill['dynamic_rate'] = 1 
            return True
        else:
            # 否则增加概率倍率
            skill['dynamic_rate'] += 0.75
            return False
        
    # 所有状态效果持续时间-1 移除已经到持续时间的buff 冷却-1
    def decStatus(self):
        for i in list(self.status.keys()):
            self.status[i] -= 1
            if self.status[i] < 0:
                self.status.pop(i)

        self.skill_1['curr_cool_down'] -= 1
        self.skill_2['curr_cool_down'] -= 1

    # 向前移动指定步数
    def moveForward(self, step: int):
        self.progress += step


    '''
    使用技能
    关键函数
    '''
    def useEffect(self, selector: list, effect: list):
    
    # 这块感觉可以用修饰器写 干净一点(然而我不熟)

        # 击退
        if effect['tag'] == 'KNOCKBACK':
            for item in selector:
                item.knockBack(effect['param'][2])
            return 

        # 击晕
        if effect['tag'] == 'STUN':
            for item in selector:
                item.status['STUN'] = 0
            return 

        # 前进
        if effect['tag'] == 'GOAHEAD':
            for item in selector:
                item.moveForward(effect['param'][2])
            return 

        # 窃取
        if effect['tag'] == 'TPSTEAL':
            self.TP += 50
            for item in selector:
                item.decTP(120)
            return

    # 击退效果调用的函数 不会变成负数
    def knockBack(self, step: int):
        self.progress -= step
        if self.progress < 0:
            self.progress = 0

    # 减少TP时调用的函数 防止扣到负数
    def decTP(self, value: int):
        self.TP -= value
        if self.TP < 0:
            self.TP = 0
    



if __name__ == '__main__':
    kasumi = Chara('t.json')