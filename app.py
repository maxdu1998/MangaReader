import requests
import json
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/home')
def Index():
    # Request para carregar os mangas em uma list e exibir
    mangaId = ['789642f8-ca89-4e4e-8f7b-eee4d17ea08b', 'c52b2ce3-7f95-469c-96b0-479524fb7a1a',
               '59b36734-f2d6-46d7-97c0-06cfd2380852', '304ceac3-8cdb-4fe7-acf7-2b6ff7a60613',
               'a77742b1-befd-49a4-bff5-1ad4e6b0ef7b', '46e9cae5-4407-4576-9b9e-4c517ae9298e',
               '4f3bcae4-2d96-4c9d-932c-90181d9c873e', '8f8b7cb0-7109-46e8-b12c-0448a6453dfa',
               'a1c7c817-4e59-43b7-9365-09675a149a6f']
    mangasReqResult = []
    for manga in mangaId:
        reqManga = requests.get('https://api.mangadex.org/manga/' + manga)
        reqManga = reqManga.json()
        mangasReqResult.append(reqManga)
    print(reqManga)
    return render_template('index.html', mangasList=mangasReqResult)


@app.route('/manga/')
def Manga():
    # Pega o ID do Manga passado na url
    mangaId = request.args.get('mangaId')

    # Carrega o manga pela API + ID do Manga / carrega as infos para passar para a info page do Manga
    reqManga = requests.get('https://api.mangadex.org/manga/' + mangaId)
    titulo = reqManga.json()['data']['attributes']['title']['en']
    sinopse = reqManga.json()['data']['attributes']['description']['en']
    capaId = reqManga.json()['data']['relationships'][2]['id']

    # Req da capa (cover) do Manga
    reqMangaCapa = requests.get('https://api.mangadex.org/cover/' + capaId)
    capa = reqMangaCapa.json()['data']['attributes']['fileName']

    # Req da lista de capitulos e volumes pelo ID do Manga,
    reqMangaCaps = requests.get('https://api.mangadex.org/manga/' + mangaId + '/aggregate')
    mangaCaps = reqMangaCaps.json()

    # Organiza os volumes em ordem crescente
    # mangaCaps.reverse()

    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa,
                           mangaCaps=mangaCaps)


@app.route('/mangaCap/')
def MangaCap():
    # Pega o ID do capitulo manga passado na url
    mangaId = request.args.get('mangaId')
    capId = request.args.get('capId')

    # Base url é o url do servidor onde e pego as img, nao pode ser fixo pois o servidor pode ser diferente
    reqBaseUrl = requests.get('https://api.mangadex.org/at-home/server/' + capId)
    baseUrl = reqBaseUrl.json()['baseUrl']
    baseUrl.replace('\/', '/')

    # '/data/' é a qualidade full do arquivo, para compressado é '/data-saver/'
    baseUrl = baseUrl + '/data/'

    # Carrega o capitulo do manga pela API + ID do capitulo
    reqCap = requests.get('https://api.mangadex.org/chapter/' + capId)
    hash = reqCap.json()['data']['attributes']['hash']
    paginas = reqCap.json()['data']['attributes']['data']
    volume = reqCap.json()['data']['attributes']['volume']
    capitulo = reqCap.json()['data']['attributes']['chapter']

    # Estrutura para pegar o capitulo anterior e o proximo para botoes na pagina de leitura, nao consegui pegar o item em x posicao do json
    reqMangaCaps = requests.get('https://api.mangadex.org/manga/' + mangaId + '/aggregate')
    cap = []
    nextCap = ''
    prevCap = ''

    for item in reqMangaCaps.json()['volumes'][volume]['chapters']:
        cap.append(reqMangaCaps.json()['volumes'][volume]['chapters'][item]['id'])

    for index in range(len(cap)):

        if cap[index] == capId:
            if index + 1 < len(cap):
                prevCap = (cap[index + 1])
            if index - 1 >= 0:
                nextCap = (cap[index - 1])
            print(nextCap, prevCap)
            break

    return render_template('mangaCap.html', baseUrl=baseUrl, mangaId=mangaId, hash=hash, paginas=paginas,
                           nextCap=nextCap, prevCap=prevCap)


@app.route('/ping')
def Ping():
    req = requests.get('https://api.mangadex.org/ping').text
    return req


if __name__ == '__main__':
    app.run()
