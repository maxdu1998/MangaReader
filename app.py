import requests
from flask import Flask, render_template, request, redirect, session, url_for
import json
import hashlib

app = Flask(__name__)
app.secret_key = 'any random string'

idioma = 'pt-br'
setCookieUrl = "https://httpbin.org/cookies/set"
getCookieUrl = "https://httpbin.org/cookies"

def cookies(userId):
    print(userId , "COOKIES")
    r = ""
    s = requests.Session()
    if userId:
        ui = {"userId": userId}
        print(ui , "UI")
        s.get(setCookieUrl, params=ui)
        r = s.get(getCookieUrl)
        print(r.json())

    else:
        r = s.get(getCookieUrl)
        print(r.json())

    return r


def saveUser(name, pswd):
    dicUsers = {}
    try:
        arq = open('login.json', mode='r')
        dicUsers = json.load(arq)
    except:
        print('error')

    print(type(dicUsers))
    res = buscaDic(name, dicUsers)
    if res > -1:
        return False
    id = len(dicUsers) + 1
    pswd = hashlib.md5(pswd.encode('utf-8')).hexdigest()
    dicUsers[id] = {'name': name, 'pswd': pswd}
    j = json.dumps(dicUsers)
    arq = open('login.json', mode='w')
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


def getUser(name, pswd):
    dicUsers = {}
    try:
        arq = open('login.json', mode='r')
        dicUsers = json.load(arq)
        print('Carregado')
    except:
        print('error')
    res = buscaDic(name, dicUsers)
    if res <= -1:
        return {}
    return {'userId':res, 'name':dicUsers[str(res)]['name'], 'pswd':dicUsers[str(res)]['pswd']}


def getFavMangas(userId):
    favMangas = []
    try:
        arq = open('favoritos.json', mode='r')
        favMangas = json.load(arq)[str(userId)]
        print('Carregado')
    except:
        print('error')
    return favMangas


def addFavMangas(userId, mangaId):
    favMangas = []
    dicFavMangas = {}
    try:
        arq = open('favoritos.json', mode='r')
        dicFavMangas = json.load(arq)
        try:
            favMangas = dicFavMangas[str(userId)]
        except:
            print('error2')
        arq.close()
        print('Carregado')
    except:
        print('error')

    if not favMangas.__contains__(mangaId):
        favMangas.append(mangaId)
    else:
        favMangas.remove(mangaId)
    dicFavMangas[str(userId)] = favMangas
    j = json.dumps(dicFavMangas)
    arq = open('favoritos.json', mode='w')
    arq.write(j)
    arq.close()
    return favMangas


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():  # put application's code here
    user = request.form['user']
    password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()

    log = getUser(user, password)
    if len(log) <= 0:
        return redirect('/')

    if log['name'] == user and log['pswd'] == password:
        session['username'] = log["userId"]
        return redirect('/home')

    return redirect('/')


@app.route('/registration')
def registration():  # put application's code here
    return render_template('cadastro.html')


@app.route('/registration', methods=['POST'])
def register():  # put application's code here
    email = request.form['email']
    name = request.form['name']
    password1 = request.form['password1']
    password2 = request.form['password2']

    save = saveUser(name, password1)

    if not save:  # ja existe esse usuário
        return redirect('/registration')
    return redirect('/home')


@app.route('/home')
def index():
    # Criação da list da home page - favoritos
    c = "-1"
    if 'username' in session:
        c = session['username']
        print(session)
    else:
        return redirect('/')
    print(c)
    mangaId = getFavMangas(c)
    mangasReqResult = []
    for manga in mangaId:
        reqManga = requests.get('https://api.mangadex.org/manga/' + manga).json()
        mangasReqResult.append(reqManga['data'])

    for manga in mangasReqResult:
        for i in manga['relationships']:
            if i['type'] == 'cover_art':
                capaId = i['id']
                reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
                manga["capa"] = reqMangaCapa.json()['data']['attributes']['fileName']

    return render_template('index.html', mangasList=mangasReqResult)


@app.route('/pesquisa/')
def pesquisa():
    mangaTitulo = request.args.get('titulo')
    reqPesquisa = requests.get(
        'https://api.mangadex.org/manga?limit=9&title=' + mangaTitulo + '&order[relevance]=desc').json()
    resultPesquisa = reqPesquisa['data']

    for manga in resultPesquisa:
        for i in manga['relationships']:
            if i['type'] == 'cover_art':
                capaId = i['id']
                reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
                manga["capa"] = reqMangaCapa.json()['data']['attributes']['fileName']

    return render_template('pesquisa.html', resultPesquisa=resultPesquisa)


@app.route('/manga/')
def manga():
    # Pega o ID do Manga passado na url
    userId = 2
    mangaId = request.args.get('mangaId')

    # Carrega o manga pela API + ID do Manga / carrega as infos para passar para a info page do Manga
    reqManga = requests.get('https://api.mangadex.org/manga/' + mangaId).json()
    titulo = reqManga['data']['attributes']['title']['en']
    sinopse = reqManga['data']['attributes']['description']['en']

    # Req da capa (cover) do Manga
    for i in reqManga['data']['relationships']:
        if i['type'] == 'cover_art':
            capaId = i['id']
            reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId).json()
            capa = reqMangaCapa['data']['attributes']['fileName']

    # Req da lista de capitulos e volumes pelo ID do Manga, 1º pt-br, 2ºen
    mangaCaps = ''
    reqMangaCaps = requests.get(
        'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=' + idioma).json()
    mangaCaps = reqMangaCaps

    if not mangaCaps['volumes']:
        reqMangaCaps = requests.get(
            'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=en').json()
        mangaCaps = reqMangaCaps
    c = getFavMangas(userId).__contains__(mangaId)
    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa,
                           mangaCaps=mangaCaps, favorito=c)


@app.route('/mangaCap/')
def mangacap():
    # Pega o ID do capitulo manga passado na url
    mangaId = request.args.get('mangaId')
    capId = request.args.get('capId')

    # Base url é o url do servidor onde e pego as img, nao pode ser fixo pois o servidor pode ser diferente
    reqBaseUrl = requests.get('https://api.mangadex.org/at-home/server/' + capId).json()
    baseUrl = reqBaseUrl['baseUrl']
    baseUrl.replace('\/', '/')

    # '/data/' é a qualidade full do arquivo, para compressado é '/data-saver/'
    baseUrl = baseUrl + '/data/'

    # Carrega o capitulo do manga pela API + ID do capitulo
    reqCap = requests.get('https://api.mangadex.org/chapter/' + capId).json()
    hash = reqCap['data']['attributes']['hash']
    paginas = reqCap['data']['attributes']['data']
    volume = reqCap['data']['attributes']['volume']
    capitulo = reqCap['data']['attributes']['chapter']

    # Estrutura para pegar o capitulo anterior e o proximo para botoes na pagina de leitura, nao consegui pegar o item em x posicao do json
    reqMangaCaps = requests.get(
        'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=' + idioma).json()
    if not reqMangaCaps['volumes']:
        reqMangaCaps = requests.get(
            'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=en').json()

    cap = []
    nextCap = ''
    prevCap = ''

    for item in reqMangaCaps['volumes'][volume]['chapters']:
        cap.append(reqMangaCaps['volumes'][volume]['chapters'][item]['id'])

    for index in range(len(cap)):
        if cap[index] == capId:
            if index + 1 < len(cap):
                prevCap = (cap[index + 1])
            if index - 1 >= 0:
                nextCap = (cap[index - 1])
            break
    return render_template('mangaCap.html', baseUrl=baseUrl, mangaId=mangaId, hash=hash, paginas=paginas,
                           nextCap=nextCap, prevCap=prevCap)


@app.route('/ping')
def ping():
    req = requests.get('https://api.mangadex.org/ping').text
    return req


@app.route('/fav', methods=['POST'])
def fav():
    j = request.data
    favorite = json.loads(j)
    addFavMangas(favorite['userId'], favorite['id'])
    return '200'


if __name__ == '__main__':
    app.run()
