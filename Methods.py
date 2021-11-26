import json
import hashlib

def saveUser(email, name, pswd1, pswd2):
    dicUsers = {}
    try:
        arq = open('temps/Jsons/login.json', mode='r')
        dicUsers = json.load(arq)
    except:
        print('error')

    print(type(dicUsers))
    res = buscaDic(name, dicUsers)
    if res > -1:
        return False
    pswd1 = hashlib.md5(pswd1.encode('utf-8')).hexdigest()
    pswd2 = hashlib.md5(pswd2.encode('utf-8')).hexdigest()
    if pswd1 != pswd2:
        return False
    id = len(dicUsers) + 1
    dicUsers[id] = {'email': email, 'name': name, 'pswd': pswd1}
    j = json.dumps(dicUsers)
    arq = open('temps/Jsons/login.json', mode='w')
    arq.write(j)
    arq.close()
    return True


def buscaDic(name, dic):
    if len(dic) == 0:
        return -1
    for k, v in dic.items():
        if v['name'] == name:
            return int(k)
    return -1


def getUser(name):
    dicUsers = {}
    try:
        arq = open('temps/Jsons/login.json', mode='r')
        dicUsers = json.load(arq)
        print('Carregado')
    except:
        print('error')
    res = buscaDic(name, dicUsers)
    if res <= -1:
        return {}
    return {'userId': res, 'name': dicUsers[str(res)]['name'], 'pswd': dicUsers[str(res)]['pswd']}


def getFavMangas(userId):
    favMangas = []
    try:
        arq = open('temps/Jsons/favoritos.json', mode='r')
        favMangas = json.load(arq)[str(userId)]
        print('Carregado')
    except:
        print('error')
    return favMangas


def addFavMangas(userId, favorite):
    mangaId = favorite['id']
    languageId = favorite['languageId']
    favMangas = []
    dicFavMangas = {}
    try:
        arq = open('temps/Jsons/favoritos.json', mode='r')
        dicFavMangas = json.load(arq)
        try:
            favMangas = dicFavMangas[str(userId)]
        except:
            print('error2')
        arq.close()
        print('Carregado')
    except:
        print('error')
    favManga = [mangaId, str(languageId)]
    if not favMangas.__contains__(favManga):
        favMangas.append(favManga)
    else:
        favMangas.remove(favManga)
    dicFavMangas[str(userId)] = favMangas
    j = json.dumps(dicFavMangas)
    arq = open('temps/Jsons/favoritos.json', mode='w')
    arq.write(j)
    arq.close()
    return favMangas
