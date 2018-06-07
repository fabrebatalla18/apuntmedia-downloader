# -*- coding: utf-8 -*-
# Module: Apuntmedia Downloader
# Created on: 06-06-2018
# Authors: Fabrebatalla18
# Version: 1.0

import requests
import json
import re
import subprocess
import argparse
import os
import base64
import sys
from subprocess import call
from collections import defaultdict
import subprocess as sp


parser = argparse.ArgumentParser()
parser.add_argument('--url', dest='url_season', help='url')
parser.add_argument('--carpeta', dest='carpeta', help='Carpeta de descargas.')
parser.add_argument('--pagina-inicial', dest='pagina_inicial', help='Pagina inicial por donde empezar a buscar.')
parser.add_argument('--pagina-final', dest='pagina_final', help='Pagina final hasta donde buscar.')
parser.add_argument('--no-descargar', dest='no_descargar', help="Activar el comando para no descargar.", action="store_true")
args = parser.parse_args()


def ReplaceDontLikeWord(X):
	try:
		X = X.replace(":", "-").replace("&", "and").replace("+", "").replace(";", "").replace("ÃƒÂ³", "o").\
			replace("[", "").replace("]", "").replace("/", "").replace("//", "").\
			replace("’", "'").replace("*", "x").replace("<", "").replace(">", "").replace("|", "").\
			replace("~", "").replace("#", "").replace("%", "").replace("{", "").replace("}", "").replace(",", "").\
			replace("?","").encode('latin-1').decode('latin-1')
	except Exception:
		X = X.decode('utf-8').replace(":", "-").replace("&", "and").replace("+", "").replace(";", "").\
			replace("ÃƒÂ³", "o").replace("[", "").replace("]", "").replace("/", "").\
			replace("//", "").replace("’", "'").replace("*", "x").replace("<", "").replace(">", "").replace("|", "").\
			replace("~", "").replace("#", "").replace("%", "").replace("{", "").replace("}", "").replace(",", "").\
			replace("?","").encode('latin-1').decode('latin-1')
	return X


def downloadFile(link, file_name):
	print("\n" + file_name)
	aria_command = [aria2cexe, link,
					'--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"',
					'--header="Range: bytes=0-"',
					'--header="DNT: 1"',
					'--async-dns=false',
					'--enable-color=false',
					'--allow-overwrite=true',
					'--auto-file-renaming=false',
					'--file-allocation=none',
					'--summary-interval=0',
					'--retry-wait=5',
					'--uri-selector=inorder',
					'--console-log-level=warn',
					'-x16', '-j16', '-s16',
					'-o', file_name]
						
	if sys.version_info >= (3, 5):
		aria_out = subprocess.run(aria_command)
		aria_out.check_returncode
	else:
		aria_out = subprocess.call(aria_command)
		if aria_out != 0:
			raise ValueError("aria failed with exit code {}".format(aria_out))

def downloadFile2(link, file_name):
	with open(file_name, "wb") as f:
		print("Descargando: %s" % file_name)
		response = requests.get(link, stream=True)
		total_length = response.headers.get('content-length')

		if total_length is None:  # no content length header
			f.write(response.content)
		else:
			dl = 0
			total_length = int(total_length)
			for data in response.iter_content(chunk_size=4096):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / total_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
				sys.stdout.flush()	

def find_str(s, char):
	index = 0

	if char in s:
		c = char[0]
		for ch in s:
			if ch == c:
				if s[index:index+len(char)] == char:
					return index

			index += 1

	return -1

def alphanumericSort(l): 
	convert = lambda text: int(text) if text.isdigit() else text 
	alphanum_key = lambda key: [ convert(c) for c in re.split("([0-9]+)", key) ] 
	return sorted(l, key = alphanum_key)	







currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)

'''
mkvmergeexe = dirPath + "/binaries/mkvmerge.exe"
ffmpegpath = dirPath + "/binaries/ffmpeg.exe"
ffprobepath = dirPath + "/binaries/ffprobe.exe"
aria2cexe = dirPath + "/binaries/aria2c.exe"
'''

Base_de_datos = dirPath + "/Base de datos"

if not os.path.exists(Base_de_datos):
	os.makedirs(Base_de_datos)


log_file = dirPath + "/apuntmedia.json"
TMP_FILE = log_file

def load_json():
	try:
		json_file = open(TMP_FILE, "r").read()
		j = json.loads(json_file)
		#print("Usando la antigua lista temporal.")
	except:
		#print("Creando nueva lista temporal.")
		j = []
	return j


def create_json(jin):
	j = json.loads(json.dumps(jin))
	#print("Reescriviendo la lista temporal.")
	try:
		with open(TMP_FILE, 'w') as outfile:
			json.dump(j, outfile)
		#print("Reescritura de la lista temporal completada.")
	except:
		#print("No se pudo escribir la lista temporal.")
		sys.exit(1)


if args.carpeta:
	if not os.path.exists(args.carpeta): os.makedirs(args.carpeta)
	os.chdir(args.carpeta)








custom_headers_season = {
							'Host': 'www.apuntmedia.es',
							'Connection': 'keep-alive',
							'Pragma': 'no-cache',
							'Cache-Control': 'no-cache',
							'Upgrade-Insecure-Requests': '1',
							'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
							'Accept-Encoding': 'gzip, deflate, br',
							'Accept-Language': 'es,ca;q=0.9,en;q=0.8'
						}




ID_lista=[]
if not args.pagina_inicial:
	contador = 0
	numero_paginas = 0
else:
	contador = int(args.pagina_inicial)
	if args.pagina_final:
		numero_paginas = int(args.pagina_final)
	else:
		numero_paginas = int(input("¿Hasta que página quieres buscar? "))

print("\nBuscando IDs en la página web...")
while contador <= numero_paginas:
	if args.url_season:
		url_season = str(args.url_season) + '/' + str(contador)
	else:
		url_season = input("Introduce la URL de una serie de Apuntmedia: ")
		url_season = url_season + '/' + str(contador)
	
	
	html_data = requests.get(url_season, headers=custom_headers_season)
	html_data = html_data.text

	A=find_str(html_data, '<div id="content" class="home-dest">')
	B=find_str(html_data, '<div class="pagination">')
	lista_ID_all=html_data[A+16:B]
	lista_ID_all = re.split("<ul>", lista_ID_all)


	for x in lista_ID_all:
		if '<h2 class="title"><span class="programas"></span>' in x:
			A=find_str(str(x), '<h2 class="title"><span class="programas"></span>')
			B=find_str(str(x), '</h2>')
			Titulo_Programa = ReplaceDontLikeWord(x[A+49:B])

		if '<img src=' in x:
			A=find_str(str(x), '<img src="')
			B=find_str(str(x), '" alt="" />')
			URL_FOTO = x[A+10:B]
			URL_FOTO = re.split("(/)", URL_FOTO)
			ID_UNICO = URL_FOTO[-3]
			js = load_json()
			if ID_UNICO not in js and ID_UNICO != "body>\n<":
				ID_lista.append(ID_UNICO)
	
	
	contador = contador + 1
create_json(js+list(set(ID_lista)))

ID_lista = list(set(ID_lista))

custom_headers_api = {
							'Host': 'player.ooyala.com',
							'Connection': 'keep-alive',
							'Pragma': 'no-cache',
							'Cache-Control': 'no-cache',
							'Accept': 'application/json, text/javascript, */*; q=0.01',
							'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
							'Accept-Encoding': 'gzip, deflate, br',
							'Accept-Language': 'es,ca;q=0.9,en;q=0.8'
						}

if ID_lista != "[]":
	for z in ID_lista:
		ID = z
		api_metadata = 'https://player.ooyala.com/player_api/v1/metadata/embed_code/5942b9f2cb974ee6a447c5023269ab51/' + ID
		api_content_tree = 'https://player.ooyala.com/player_api/v1/content_tree/embed_code/F0OWwyOo4T6H27--qop_GKi9c_ea/' + ID
		api_authorization = 'https://player.ooyala.com/sas/player_api/v2/authorization/embed_code/F0OWwyOo4T6H27--qop_GKi9c_ea/' + ID + '?domain=www.apuntmedia.es'

		print("\nBuscando metadatos...")
		resp = requests.get(api_metadata, headers=custom_headers_api)
		json_api_metada = resp.content
		json_api_metada = json.loads(json_api_metada.decode())
		
		try:
			FechaExpiracion = json_api_metada['metadata'][ID]['base']['FechaExpiracion']
		except Exception:
			FechaExpiracion = "NA"
		
		try:	
			FechaPublicacion = json_api_metada['metadata'][ID]['base']['FechaPublicacion']
		except Exception:
			FechaExpiracion = "NA"

		try:
			Idioma = json_api_metada['metadata'][ID]['base']['Idioma']
		except Exception:
			FechaExpiracion = "NA"
		
		#try:
			#Titulo_Programa = ReplaceDontLikeWord(json_api_metada['metadata'][ID]['base']['Keyword'])
		#except Exception:
			#Titulo_Programa = "Desconocido"
		Tipo = json_api_metada['metadata'][ID]['base']['Tipo']

		print("Buscando otros datos...")
		resp = requests.get(api_content_tree, headers=custom_headers_api)
		json_api_content_tree = resp.content
		json_api_content_tree = json.loads(json_api_content_tree.decode())
		
		#asset_pcode = json_api_content_tree['content_tree'][ID]['asset_pcode']
		#content_type = json_api_content_tree['content_tree'][ID]['content_type']
		#created_at = json_api_content_tree['content_tree'][ID]['created_at']
		try:
			description = json_api_content_tree['content_tree'][ID]['description']
		except Exception:
			FechaExpiracion = "NA"

		try:
			duration = json_api_content_tree['content_tree'][ID]['duration']
		except Exception:
			FechaExpiracion = "NA"

		#embed_code = json_api_content_tree['content_tree'][ID]['embed_code']
		#promo_image = json_api_content_tree['content_tree'][ID]['promo_image']
		#thumbnail_image = json_api_content_tree['content_tree'][ID]['thumbnail_image']
		
		try:
			title = ReplaceDontLikeWord(json_api_content_tree['content_tree'][ID]['title'])
		except Exception:
			FechaExpiracion = "NA"

		print("Buscando enlace de descarga...")
		resp = requests.get(api_authorization, headers=custom_headers_api)
		json_api_authorization = resp.content
		json_api_authorization = json.loads(json_api_authorization.decode())
		
		URL_List = []
		for y in json_api_authorization['authorization_data'][ID]['streams']:		
			if y['delivery_type'] == 'mp4':
				URL_Dict = (int(y['video_bitrate']), base64.b64decode(y['url']['data']).decode('utf8'))
				URL_List.append(URL_Dict)

		quality_list = []
		for a, b in URL_List:
			quality_list.append(a)

		maxquality = sorted(quality_list)[-1]
		for a, b in URL_List:
			if a == maxquality:
				maxquality_link = b
		

		print("Guardando datos en el txt...")		
		with open(Base_de_datos + '/' + Titulo_Programa + '.txt', 'a', encoding='utf-8') as file:
				file.write("Titulo: " + title)
				file.write("\nFecha de publicación: " + FechaPublicacion)
				file.write("\nFecha de expiración: " + FechaExpiracion)
				file.write("\nIdioma: " + Idioma)
				file.write("\nTipo de medio: " + Tipo) 
				file.write("\nDescripción: " + description)
				file.write("\nEnlace: " + maxquality_link)
				file.write("\n\n\n")

		if not args.no_descargar:
			inputVideo = title + '.mp4'
			if not os.path.exists(Titulo_Programa): 
				os.makedirs(Titulo_Programa)
			os.chdir(Titulo_Programa)
			if os.path.isfile(inputVideo) and not os.path.isfile(inputVideo + ".aria2"):
				print("Ya descargaste anteriormente el archivo: " + inputVideo)
			else:
				#print("Descargando...")
				downloadFile2(maxquality_link, inputVideo)
				os.chdir(dirPath)
				if args.carpeta:
					os.chdir(args.carpeta)