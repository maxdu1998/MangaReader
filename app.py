import requests
from flask import Flask, render_template, request, redirect, session, url_for
import json
import hashlib
import urllib.request
import os
import OCR
from Methods import saveUser, getUser, getFavMangas, addFavMangas


app = Flask(__name__)
app.secret_key = 'any random string'

language = ['pt-br', 'en']




@app.route('/')
def home():
    if 'username' in session:
        return redirect('home')
    return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])
def login():  # put application's code here
    if request.method == 'POST':
        user = request.form['user']
        password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        log = getUser(user, password)
        if len(log) <= 0:
            return redirect('/')
        if log['name'] == user and log['pswd'] == password:
            session['username'] = log["userId"]
            return redirect('/home')

    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/registration')
def registration():  # put application's code here
    return render_template('cadastro.html')


@app.route('/registration', methods=['POST', 'GET'])
def register():  # put application's code here
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password1 = request.form['password1']
        password2 = request.form['password2']

        save = saveUser(email, name, password1, password2)

        if not save:  # ja existe esse usuário
            return redirect('/registration')
        return redirect('/home')

    return render_template('cadastro.html')


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
        reqManga = requests.get('https://api.mangadex.org/manga/' + manga[0]).json()
        mangasReqResult.append([reqManga['data'], manga[1]])

    for manga in mangasReqResult:
        for i in manga[0]['relationships']:
            if i['type'] == 'cover_art':
                capaId = i['id']
                reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
                manga[0]["capa"] = reqMangaCapa.json()['data']['attributes']['fileName']

    return render_template('index.html', mangasList=mangasReqResult)


@app.route('/pesquisa/')
def pesquisa():
    mangaTitulo = request.args.get('titulo')
    opt1 = request.args.get('options')

    print('options '+str(opt1))
    languageId = int(opt1)
    #reqPesquisa = requests.get('https://api.mangadex.org/manga?limit=9&title=' + mangaTitulo + '&order[relevance]=desc').json()
    reqPesquisa = requests.get('https://api.mangadex.org/manga?limit=9&title=' + mangaTitulo + '&availableTranslatedLanguage[]='+language[languageId]+'&order[relevance]=desc').json()
    resultPesquisa = reqPesquisa['data']

    for manga in resultPesquisa:
        for i in manga['relationships']:
            if i['type'] == 'cover_art':
                capaId = i['id']
                reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
                manga["capa"] = reqMangaCapa.json()['data']['attributes']['fileName']

    return render_template('pesquisa.html', resultPesquisa=resultPesquisa, languageId=languageId)


@app.route('/manga/')
def manga():
    # Pega o ID do Manga passado na url
    userId = session['username']
    mangaId = request.args.get('mangaId')

    # Carrega o manga pela API + ID do Manga / carrega as infos para passar para a info page do Manga
    reqManga = requests.get('https://api.mangadex.org/manga/' + mangaId).json()
    titulo = reqManga['data']['attributes']['title']['en']
    sinopse = reqManga['data']['attributes']['description']['en']
    languageId = int(request.args.get('languageId'))

    # Req da capa (cover) do Manga
    for i in reqManga['data']['relationships']:
        if i['type'] == 'cover_art':
            capaId = i['id']
            reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId).json()
            capa = reqMangaCapa['data']['attributes']['fileName']

    # Req da lista de capitulos e volumes pelo ID do Manga, 1º pt-br, 2ºen
    mangaCaps = ''
    reqMangaCaps = requests.get(
        'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=' + language[languageId]).json()
    mangaCaps = reqMangaCaps
    if not mangaCaps['volumes']:
        reqMangaCaps = requests.get(
            'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=en').json()
        mangaCaps = reqMangaCaps
        languageId = 1
    c = getFavMangas(userId).__contains__([mangaId, str(languageId)])
    print(c)
    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa,
                           mangaCaps=mangaCaps, favorito=c, languageId=languageId)


@app.route('/mangaCap/')
def mangacap():
    # Pega o ID do capitulo manga passado na url
    mangaId = request.args.get('mangaId')
    capId = request.args.get('capId')
    languageId = int(request.args.get('languageId'))

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
        'https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=' + language[languageId]).json()
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
                           nextCap=nextCap, prevCap=prevCap, languageId=languageId)


@app.route('/translate/')
def translate():
    imglink = request.args.get('imgLink')
    # imglink = 'https://uploads.mangadex.org/data/8f2f527acba633986898597123264070/E2-3ddedac792ac92d674d97db6b91079a123f8df8e60c0404855d5417ef6574032.jpg'
    print(imglink)
    ocr = OCR.TranslateOCR(imglink)
    render = render_template('translate.html', img=ocr)

    return render


@app.route('/ping')
def ping():
    req = requests.get('https://api.mangadex.org/ping').text
    return req


@app.route('/fav', methods=['POST'])
def fav():
    j = request.data
    favorite = json.loads(j)
    addFavMangas(session['username'], favorite)
    return '200'


if __name__ == '__main__':
    app.run()