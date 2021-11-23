import requests
from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

idioma = 'pt-br'


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
    return dicUsers[str(res)]



@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():  # put application's code here
    user = request.form['user']
    password = request.form['password']

    log = getUser(user, password)
    if len(log) <= 0:
        print('Saiu aqui 1')
        return redirect('/')
    if log['name'] == user and log['pswd'] == password:
        return redirect('/home')
    print('Saiu aqui 2')
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
    # Criação da list da home page - mais vendidos
    mangaId = ['a1c7c817-4e59-43b7-9365-09675a149a6f']
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

    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa,
                           mangaCaps=mangaCaps)


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


if __name__ == '__main__':
    app.run()

