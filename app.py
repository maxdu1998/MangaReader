import requests
from flask import Flask, render_template, request

app = Flask(__name__)

idioma = 'pt-br'


@app.route('/')
def Index():
    # Request para carregar os mangas em uma list e exibir
    mangaId = ['789642f8-ca89-4e4e-8f7b-eee4d17ea08b', 'c52b2ce3-7f95-469c-96b0-479524fb7a1a',
               '59b36734-f2d6-46d7-97c0-06cfd2380852', '304ceac3-8cdb-4fe7-acf7-2b6ff7a60613',
               'a77742b1-befd-49a4-bff5-1ad4e6b0ef7b', '46e9cae5-4407-4576-9b9e-4c517ae9298e',
               '4f3bcae4-2d96-4c9d-932c-90181d9c873e', '8f8b7cb0-7109-46e8-b12c-0448a6453dfa',
               'a1c7c817-4e59-43b7-9365-09675a149a6f']
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
def Pesquisa():
    mangaTitulo = request.args.get('titulo')
    reqPesquisa = requests.get('https://api.mangadex.org/manga?limit=9&title=' + mangaTitulo + '&order[relevance]=desc').json()
    resultPesquisa = reqPesquisa['data']

    for manga in resultPesquisa:
        for i in manga['relationships']:
            if i['type'] == 'cover_art':
                capaId = i['id']
                reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
                manga["capa"] = reqMangaCapa.json()['data']['attributes']['fileName']

    return render_template('pesquisa.html', resultPesquisa=resultPesquisa)


@app.route('/manga/')
def Manga():
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
    reqMangaCaps = requests.get('https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=' + idioma).json()
    mangaCaps = reqMangaCaps

    if not mangaCaps['volumes']:
        reqMangaCaps = requests.get('https://api.mangadex.org/manga/' + mangaId + '/aggregate/?translatedLanguage[]=en').json()
        mangaCaps = reqMangaCaps

    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa,
                           mangaCaps=mangaCaps)


@app.route('/mangaCap/')
def MangaCap():
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
    reqMangaCaps = requests.get('https://api.mangadex.org/manga/' + mangaId + '/aggregate').json()
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
def Ping():
    req = requests.get('https://api.mangadex.org/ping').text
    return req



if __name__ == '__main__':
    app.run()
