import requests
import json
import pymongo
import time

client = pymongo.MongoClient('localhost', 27017)


def saveDocToMongo(doc):
    """"
    保存数据至 MongoDB
    """
    db = client.spider
    db.ip.insert_one(doc)


def saveErrorToMongo(doc):
    """"
    保存 Error 至 MongoDB
    """
    db = client.spider
    db.err.insert_one(doc)


def detect(ip):
    """
        1). {"ret":-1,"ip":"192.168.1.101"}
        2). -2
        3). 正常
    :param ip:
    :return:
    """
    sina_url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip=%s'
    try:
        text = requests.get(sina_url % ip).text
        print(text)
        if text == '-2':
            return

        jsonObj = json.loads(text)
        if jsonObj['ret'] == 1:
            ipInfo = {
                '_id': ip,
                'city': jsonObj['city'],
                'country': jsonObj['country'],
                'desc': jsonObj['desc'],
                'district': jsonObj['district'],
                'isp': jsonObj['isp'],
                'province': jsonObj['province'],
                'type': jsonObj['type'],
            }
            saveDocToMongo(ipInfo)
            pass
    except Exception as e:
        print('Parse failed', e)
        saveErrorToMongo({'ip': ip})
        pass


def dec2Bin(decInt):
    """
    十进制转二进制
    """
    binStr = bin(decInt)[2:].zfill(32)
    return binStr


def bin2Dec(binInt):
    """
    二进制转十进制 返回值是 int
    """
    decInt = int(str(binInt), 2)
    # print(decInt)
    return decInt


def sliceBinStr(binStr):
    """
    32位二进制平均切成 4 片
    """
    aSection = binStr[0:8]
    bSection = binStr[8:16]
    cSection = binStr[16:24]
    dSection = binStr[24:]
    # print('aSection=%s, bSection=%s, cSection=%s, dSection=%s' % (aSection, bSection, cSection, dSection))
    return aSection, bSection, cSection, dSection


def composeIp(binSectionTuple):
    """
    将二进制元组拼接成 ip 地址
    :param binSectionTuple:
    :return: ip 字符串
    """
    ip = ''
    for binSection in binSectionTuple:
        ip = ip + str(bin2Dec(binSection)) + '.'
    return ip[:-1]


def dec2Ip(decInt):
    """
    十进制数字转换成 ip 地址
        1). 十进制数字转成 32 位二进制字符串
        2). 32 位二进制字符串平均切片
        3). 将切片后的每 8 位二进制字符串转化成十进制
        4). 拼接四段十进制字符串为 ip 地址
    :param decInt:
    :return:
    """
    binStr = dec2Bin(decInt)
    binSectionTuple = sliceBinStr(binStr)
    return composeIp(binSectionTuple)


def ip2Dec(ip):
    """
    将 ip 转换为对应的十进制数字
    :param ip:
    :return: 返回十进制 int
    """
    decSectionList = ip.split('.')
    binStr = ''
    for decSection in decSectionList:
        binSection = bin(int(decSection))[2:].zfill(8)
        binStr = binStr + binSection
    return bin2Dec(binStr)


def main():
    # 跳过以下保留ip，详情参见 https://zh.wikipedia.org/wiki/%E4%BF%9D%E7%95%99IP%E5%9C%B0%E5%9D%80
    skip1 = (ip2Dec('0.0.0.0'), ip2Dec('0.255.255.255'))
    skip2 = (ip2Dec('10.0.0.0'), ip2Dec('10.255.255.255'))
    skip3 = (ip2Dec('100.64.0.0'), ip2Dec('100.127.255.255'))
    skip4 = (ip2Dec('127.0.0.0'), ip2Dec('127.255.255.255'))
    skip5 = (ip2Dec('169.254.0.0'), ip2Dec('169.254.255.255'))
    skip6 = (ip2Dec('172.16.0.0'), ip2Dec('172.31.255.255'))
    skip7 = (ip2Dec('192.0.0.0'), ip2Dec('192.0.0.255'))
    skip8 = (ip2Dec('192.0.2.0'), ip2Dec('192.0.2.255'))
    skip9 = (ip2Dec('192.88.99.0'), ip2Dec('192.88.99.255'))
    skip10 = (ip2Dec('192.168.0.0'), ip2Dec('192.168.255.255'))
    skip11 = (ip2Dec('198.18.0.0'), ip2Dec('198.19.255.255'))
    skip12 = (ip2Dec('198.51.100.0'), ip2Dec('198.51.100.255'))
    skip13 = (ip2Dec('203.0.113.0'), ip2Dec('203.0.113.255'))
    skip14 = (ip2Dec('224.0.0.0'), ip2Dec('239.255.255.255'))
    skip15 = (ip2Dec('240.0.0.0'), ip2Dec('255.255.255.255'))
    print(skip1)

    i = 16854660
    s = 2 << 31
    while i < s:
        print(i)
        if skip1[0] <= i <= skip1[1] or skip2[0] <= i <= skip2[1] \
                or skip3[0] <= i <= skip3[1] or skip4[0] <= i <= skip4[1] \
                or skip5[0] <= i <= skip5[1] or skip6[0] <= i <= skip6[1] \
                or skip7[0] <= i <= skip7[1] or skip8[0] <= i <= skip8[1] \
                or skip9[0] <= i <= skip9[1] or skip10[0] <= i <= skip10[1] \
                or skip11[0] <= i <= skip11[1] or skip12[0] <= i <= skip12[1] \
                or skip13[0] <= i <= skip13[1] or skip14[0] <= i <= skip14[1] \
                or skip15[0] <= i <= skip15[1]:
            print('skip')
            i = i + 1
            continue
        else:
            print('detect')
            detect(dec2Ip(i))
            time.sleep(0.03)
            i = i + 1


if __name__ == '__main__':
    main()
