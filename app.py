import requests
import json
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/home')
def Index():
    return render_template('index.html')


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
    #mangaCaps.reverse()

    return render_template('manga.html', mangaId=mangaId, titulo=titulo, sinopse=sinopse, capa=capa, mangaCaps=mangaCaps)


@app.route('/mangaCap/')
def MangaCap():
    # Pega o ID do capitulo manga passado na url
    capId = request.args.get('capId')

    # Base url é o url do servidor onde e pego as img, nao pode ser fixo pois o servidor pode ser diferente
    reqBaseUrl = requests.get('https://api.mangadex.org/at-home/server/' + capId)
    baseUrl = reqBaseUrl.json()['baseUrl']
    baseUrl.replace('\/', '/')

    # '/data/' é a qualidade full do arquivo, para compressado é '/data-saver/'
    baseUrl = baseUrl + '/data/'
    print(baseUrl)

    # Carrega o capitulo do manga pela API + ID do capitulo
    reqCap = requests.get('https://api.mangadex.org/chapter/' + capId)
    idManga = reqCap.json()['data']['attributes']['hash']
    capitulos = reqCap.json()['data']['attributes']['data']

    return render_template('mangaCap.html', baseUrl=baseUrl, idManga=idManga, capitulos=capitulos)


@app.route('/ping')
def Ping():
    req = requests.get('https://api.mangadex.org/ping').text
    return req


if __name__ == '__main__':
    app.run()
