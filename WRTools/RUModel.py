def getS6():
    S5 = '其他'
    S6 = '连接器'
    match (S5):
        case '半导体':
            s6 = 'parameter!$E$2:$E$5'
        case "被动件":
            s6 = 'parameter!$E$6:$E$8'
        case '电源':
            s6 = 'parameter!$E$10:$E$13'
        case '机电设备':
            s6 = 'parameter!$E$14:$E$17'
        case '传感器':
            s6 = 'parameter!$E$18:$E$20'
        case '微波射频':
            s6 = 'parameter!$E$21:$E$23'
        case '其他':
            s6 = 'parameter!$E$24:$E$30'
    return S6


#运费率
def getU5():
    T5='模组'
    U5=999 #运费率
    match(T5):
        case'分立器件-单管':
            U5=0.01
        case '分立器件-模块':
            U5 = 0.25
        case 'IC':
            U5 = 0.01
        case '模组':
            U5 = 0.12
        case '常见阻容感':
            U5 = 0.72
        case '冷门阻容感':
            U5 = 0.25
        case '晶振、滤波器':
            U5 = 0.04
        case '连接器':
            U5 = 0.12
        case '电池':
            U5 = 999
        case '变压器':
            U5 = 0.35
        case '板载电源':
            U5 = 0.02
        case '非板载电源':
            U5 = 0.15
        case '开关':
            U5 = 0.33
        case '继电器':
            U5 = 0.084
        case '工业自动化':
            U5 = 0.2
        case '风扇及热管理':
            U5 = 0.08
        case '半导体传感器及MEMS':
            U5 = 0.01
        case '机械式传感器':
            U5 = 999
        case '电路传感器':
            U5 = 0.05
        case '射频器件':
            U5 = 0.12
        case '射频模块':
            U5 = 0.12
        case '射频配件':
            U5 = 0.12
        case '光电器件':
            U5 = 0.15
        case '电路保护':
            U5 = 0.05
        case '大型设备':
            U5 = 999
        case '小型工具':
            U5 = 0.14
        case '线缆':
            U5 = 0.14
        case '测试设备':
            U5 = 0.25
        case '杂类':
            U5 = 0.2
    return U5

#运费
def getW5():
    U5='0.25' #default value
    E5=100 #数量
    O5=3.00 #采购单价
    if E5*O5*U5 >= 50:
        W5 = E5*O5*U5
    else:
        W5 = 50.00
    return W5

#成本系数
def getV5():
    E5 = 100  # 数量
    O5 = 3.00  # 采购单价
    T5 = '连接器' # 细分类别
    U5 = 0.25   #运清费率
    V5=1    #成本系数
    if E5*O5*U5 < 50:
        V5 = 1.22+(50/(O5*E5))
    else:
        match (T5):
            case '分立器件-单管':
                V5 = 1.23
            case '分立器件-模块':
                V5 = 1.47
            case 'IC':
                V5 = 1.23
            case '模组':
                V5 = 1.34
            case '常见阻容感':
                V5 = 1.94
            case '冷门阻容感':
                V5 = 1.47
            case '晶振、滤波器':
                V5 = 1.26
            case '连接器':
                V5 = 1.32
            case '电池':
                V5 = 999
            case '变压器':
                V5 = 1.37
            case '板载电源':
                V5 = 1.24
            case '非板载电源':
                V5 = 1.37
            case '开关':
                V5 = 1.55
            case '继电器':
                V5 = 1.2
            case '工业自动化':
                V5 = 1.42
            case '风扇及热管理':
                V5 = 1.3
            case '半导体传感器及MEMS':
                V5 = 1.23
            case '机械式传感器':
                V5 = 999
            case '电路传感器':
                V5 = 1.27
            case '射频器件':
                V5 = 1.32
            case '射频模块':
                V5 = 1.32
            case '射频配件':
                V5 = 1.32
            case '光电器件':
                V5 = 1.37
            case '电路保护':
                V5 = 1.27
            case '大型设备':
                V5 = 999
            case '小型工具':
                V5 = 1.36
            case '线缆':
                V5 = 1.36
            case '测试设备':
                V5 = 1.47
            case '杂类':
                V5 = 1.42
    return V5


