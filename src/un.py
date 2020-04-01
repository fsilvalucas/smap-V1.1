from datetime import date, timedelta, datetime
import os
import shutil
import zipfile
import subprocess
import time

def name(delta = 0):
	#Modelos_Chuva_Vazao_20200101.zip
	data = date.today() - timedelta(days=delta)
	return 'Modelos_Chuva_Vazao_' + data.strftime('%Y%m%d') + '.zip'

def ons(name):
	return "https://sintegre.ons.org.br/sites/9/13/82/_layouts/download.aspx?sourceUrl=https://sintegre.ons.org.br" \
            "/sites/9/13/82/Produtos/238/Modelos_Chuva_Vazao_" + name

def zipToFile(name, data):
	path = r'C:\Users\Lucas\Downloads' + '\\'
	file = zipfile.ZipFile(path + 'Modelos_Chuva_Vazao_' + datetime.strftime(data, "%Y%m%d") + '.zip')
	file.extractall(path + name)
	file.close()

def escreve(file, linhas):
    with open(file, 'w') as wd:
        for i in range(len(linhas)):
            wd.writelines(linhas[i])


def inicializacao(path_new, date_in_string, previsao):
    lista = []
    for i in os.listdir(path_new):
        if 'INICIALIZACAO' in i:
            lista.append(i)
    for i in lista:
        with open(path_new  + '\\' + i, 'r') as rd:
            rd = rd.readlines()
            rd[0] = rd[0].replace(rd[0][0:10], date_in_string)
            rd[2] = rd[2].replace(rd[2][0:2], previsao)
            escreve(path_new + '\\' + i, rd)


def precipitacao(path_new, modelo_precipitacao):
    # lista = []
    with open(path_new + '\\ARQ_ENTRADA' + '\\MODELOS_PRECIPITACAO.txt', 'w') as modelo:
    	textoModelos = '1\n' + modelo_precipitacao + '\n' 
    	modelo.write(textoModelos)

def executa_smap(path):
	p = subprocess.Popen(path + '\\batsmap-desktop.exe')
	aux = 0
	
	while aux < 100:
		with open(path + '\\logs\\desktop_bat.log', 'r') as log:
			txt = log.readlines()
			ultimaLinha = txt[-1]

			if 'A rotina BAT-SMAP nao sera executada' in ultimaLinha:
				break

			if 'Finalizando programa' in ultimaLinha:
				print('Realizado com sucesso')
				break

			else:
				time.sleep(10)
				aux += 10

				if aux > 100:
					print('Overtime')
					break
	p.kill()

def parser(valor, format): 
	return date.strftime(date.today() - timedelta(days=valor), format)
