import json

def effectGen(tag: str, param:list) -> dict:
    eff = {}
    eff['tag'] = tag
    eff['param'] = param
    return eff

def skillGen(name: str, info: str, TP_expend: int, prob: float, times_limit: int, cool_down: int, effect: list) -> dict:
    skill = {}
    skill['name'] = name
    skill['type'] = 'SKILL'
    skill['info'] = info
    skill['TP_expend'] = TP_expend
    skill['prob'] = prob
    skill['times_limit'] = times_limit
    skill['cool_down'] = cool_down
    skill['effect'] = effect
    return skill

def charaGen(name: str, icon: str, speed: list, UB: list) -> dict:
    chara = {}
    chara['name'] = name
    chara['icon'] = icon
    chara['speed'] = speed
    chara['UB'] = UB
    return chara

def UBGen(name: str, info: str, effect: list) -> dict:
    UB = {}
    UB['name'] = name
    UB['type'] = 'UB'
    UB['info'] = info
    UB['effect'] = effect
    return UB   

chara = charaGen('カスミ', '[CQ:emoji]', [3,3,3,3,3,5,5,5], UBGen('魔力棱镜', '大幅度减少其他角色的TP，小幅度回复自身TP', [effectGen('TPSTEAL', [2, 3, 120, 50])]))
skill_1 = skillGen('魔力抽取', '使目标后退 自己前进', 25, 0.07, 5, 4, [])
skill_1['effect'] += [effectGen('GOAHEAD', [0, 1, 3])]
skill_1['effect'] += [effectGen('KNOCKBACK', [1, 1, 3])]

chara['skill_1'] = skill_1
chara['skill_2'] = skillGen('魔法枷锁', '击晕最靠前的两个对手', 35, 0.05, 2, 5, [effectGen('STUN', [1, 2])])

print(json.dumps(chara, sort_keys=False, indent=4, ensure_ascii=False))

with open('./kasumiRun/chara/t.json', 'w+', encoding='utf-8') as f:
    f.write(json.dumps(chara, sort_keys=False, indent=4, ensure_ascii=False))