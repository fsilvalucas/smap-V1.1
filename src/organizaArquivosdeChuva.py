import os
import datetime
from datetime import datetime, timedelta
from src.funcoes import searchBinary, escreve
import sys
import shutil

def tamanho(lista):
	return range(len(lista))

def organizaArquivosDeChuva(cxv,prec, metodologia): # Classe chuva x vazao, classe precipitacao
	
	cont = 0
	path_to_model = cxv.path
	path_to_prec = prec.path

	caso = prec.state
	
	iter_model_regioes = [path_to_model + '//' + x + '//ARQ_ENTRADA' for x in cxv.regioes]
	iter_model_bases = ['base//' + caso + '//' + x + '//Base.dat' for x in cxv.regioes]

	copia_a_chuva(iter_model_regioes, cxv.data, path_to_prec)

	for i in tamanho(iter_model_regioes):

		for j in os.listdir(iter_model_regioes[i]):  # para cada j em documento dentro de uma bacia

			if prec.nome in j:

				aplicado = metodologia(iter_model_regioes[i] + '//' + j)
				aplicado.sort(key=lambda x: (x[0],x[1]))
				base = metodologia(iter_model_bases[i])
				base.sort(key=lambda x: (x[0],x[1]))
				lista_auxiliar = []

				for k in base:

					cont += cont
					aux =  searchBinary(k[0:2], aplicado) # Para cada valor (x,y) dentro da base, procura a precipitação correspondente nos arquivos de chuva
					k[2] = aux
					lista_auxiliar.append(k) # com o valor achado, é feita a substituição criando uma nova lista

				for k in range(len(lista_auxiliar)): # Para cada iteração na lista, o valor é substituido por uma string = 'lat long  precipitacao'

					lista_auxiliar[k] = str(lista_auxiliar[k][0]) + ' ' + str(lista_auxiliar[k][1]) + '  ' + str(lista_auxiliar[k][2]) + '\n'

				escreve(iter_model_regioes[i] + '//' + j, lista_auxiliar) # Escrita da lista no lugar dos arquivos antigos

					# a ideia da busca binaria e da troca dos arquivos é melhorar o funcionamento do Chuva vazao. Assim só serão usados os arquivos referentes a propria bacia


def copia_a_chuva(lista_de_caminhos_das_bacias, data_do_modelo, path_to_prec):

	for i in lista_de_caminhos_das_bacias:

		for arquivo in os.listdir(i):
			
			if 'PMEDIA_ORIG_p' in arquivo: os.remove(i + "//" + arquivo)
	
		for j in os.listdir(path_to_prec): 
			
			if 'PMEDIA_p' in j: shutil.copy(path_to_prec + '//' + j, i + '//' + j.replace('PMEDIA_p', 'PMEDIA_ORIG_p'))




def mudar_nome(lista_de_caminhos_das_bacias, data_do_modelo, data_da_chuva):

	for caminhos in lista_de_caminhos_das_bacias:

		print('estou em: ', caminhos)

		for arquivo in os.listdir(caminhos):

			print('---- Agora sou: ', arquivo)

			if 'PMEDIA_ORIG_p' in arquivo:

				print('ACHEI UM HA')

				try:

					print('mudançaaaaaaaaaaaaaaaaaaaaaaaaaa')
					nome_velo = arquivo
					nome_novo = arquivo.replace(data_do_modelo.strftime('_p%d%m%ya'), (data_do_modelo + timedelta(days=1)).strftime('_p%d%m%ya'))

					os.rename(caminhos + "//" + nome_velo, caminhos + "//" + nome_novo)
				
				except Exception as e:

					print('FODEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEU', '       ', e)

					pass
