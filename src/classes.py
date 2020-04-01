from src.un import name
import sys
import os
import datetime
import shutil
from datetime import datetime, timedelta
from src.funcoes import base_geral as b1
from src.funcoes import base_comun as b2
from src.funcoes import searchBinary, escreve
from src.grava_smap import main as escreveResultadoSMap
from src.organizaArquivosdeChuva import organizaArquivosDeChuva
from src.organizaArquivosdeChuva2 import organizaArquivosDeSmap
from src.smapPreliminar import organizaArquivosdeSmap as organizaArquivosDeSmap_preliminar
import time
import subprocess

class modelo_precipitacao(object):

	GERAL = '0'  # Modelo padrão 22 mil linhas de grade
	COMUN = '1'  # Modelo resumido ONS, 52 linhas de grade

	def __init__(self, nome='PMEDIA_ORIG'):
		
		self.__nome = nome
		self.__path = r'Arq_entrada\Precipitacao' 
		self.__data = self.findData()
		self.__nDias = len(os.listdir(self.path))
		self.state = modelo_precipitacao.COMUN
		
	@property
	def nDias(self):
		return self.__nDias

	@property
	def data(self):
		return self.__data

	@property
	def nome(self):
		return self.__nome

	@property
	def path(self):
		return self.__path
	

	def findData(self):
		aux = os.listdir(self.path)[0]
		first = aux.find('p')
		last = aux.find('a')

		return datetime.strptime(aux[first+1: last],'%d%m%y')

	def diasPrevisao(self):
		return len(os.listdir(self.path))
	
	def defineState(self):
		# implementar
		pass


class modelo_cxv(object):

	def __init__(self, data):
		
		self.__data = data
		self.__path =self.getPath()
		self.__regioes = ['Grande', 'Iguacu', 'Itaipu', 'Paranaiba', 'Paranapanema', 'SaoFrancisco', 'Tiete', 'Tocantins',
          'Uruguai']

	@property
	def data(self):
		return self.__data

	@property
	def path(self):
		return self.__path

	@property
	def regioes(self):
		return self.__regioes

	@property
	def dataString(self):
		return datetime.strftime(self.data,'%Y%m%d')
	

	def getPath(self):
		path = r'Arq_entrada\Modelo'
			
		models = os.listdir(path)

		if 'Modelos_Chuva_Vazao_' + self.dataString in models:
			path += r'\Modelos_Chuva_Vazao_' + datetime.strftime(self.data,'%Y%m%d') + r'\Modelos_Chuva_Vazao\SMAP'
			return path

		else:
			raise Exception('O arquivo solicitado não se encontra na pasta')
			
class rodada(object):

	OFICIAL = 0
	DEFINITIVO = 1
	PRELIMINAR = 2


	def __init__(self, cxv, precipitacao = None):

		self.cxv = cxv
		self.precipitacao = precipitacao
		self.state = None
		self.rodada = self.defineRodada() # A rodada é definida via passagem da precipitacao ou não

	def defineRodada(self):
		
		if self.precipitacao is None:
			self.state = rodada.OFICIAL
			return self.oficial

		else:
			if datetime.now().hour < 13:
				self.state = rodada.PRELIMINAR
				return self.preliminar
			else:
				self.state = rodada.DEFINITIVO
				return self.definitivo
	
	def preliminar(self):
		organizaArquivosDeChuva(cxv=self.cxv, prec=self.precipitacao, metodologia=b2)
		organizaArquivosDeSmap_preliminar(cxv=self.cxv, nDias=self.precipitacao.nDias, nome=self.precipitacao.nome)

	def oficial(self): # Se for o definitvo ons, apenas escreve o resultado
		escreveResultadoSMap(path=self.cxv.path,data=self.cxv.data,dias_previsao=12)

	def definitivo(self):
		# Implement: Organiza os Arquivos de chuva, aplica SMAP e escreve a planilha resultados.
		organizaArquivosDeChuva(cxv=self.cxv,prec=self.precipitacao,metodologia=b2)
		print('arquivos de chuva organizados')
		organizaArquivosDeSmap(cxv=self.cxv, nDias=self.precipitacao.nDias)
		print('ARQUIVOS DE SMAP ATUALIZADOS')
		# Cada Bacia será instanciada como um novo objeto, que assim será copiada as dependencias do SMAP
		#eachBacia(self.cxv).copy_depencies().aplica_smap()
		escreveResultadoSMap(path=self.cxv.path,data=self.precipitacao.data,dias_previsao=self.precipitacao.nDias)

class eachBacia(object):

	def __init__(self, bacia_cxv): # Modelo cxv

		self.__path = bacia_cxv
		self.__dependency = r'base\smap'

	def copy_depencies(self):

		try:
			
			shutil.copy(self.__dependency + r'\batsmap-desktop.exe', self.__path)
			shutil.copytree(self.__dependency + r'\bin', self.__path + '\\bin')
			shutil.copytree(self.__dependency + r'\logs', self.__path + '\\logs')
		
		except Exception as e:
			
			print(e)
			pass

		return self

	def aplica_smap(self):  # modificar

		os.chdir(self.__path)
		p = subprocess.Popen(self.__path + '\\batsmap-desktop.exe')
		time.sleep(1)
		tempo = 0
		
		while tempo < 600:

			with open(self.__path + '\\logs\\desktop_bat.log', 'r') as log:
				
				txt = log.readlines()
				ultimaLinha = txt[-1]

				if 'A rotina BAT-SMAP nao sera executada' in ultimaLinha:
					
					break

				if 'Finalizando programa' in ultimaLinha:
					
					print('tudo ok na regiao: ' + regiao)
					time.sleep(2)
					break
				
				else:
                    
					time.sleep(10)
					tempo = tempo + 10
					
					if tempo > 600:
						
						print('overtime na regiao: ' + regiao)
						break
		p.kill()




class novaIteracao(object):

	GERAL = 0
	COMUN = 1

	def __init__(self, cxv, precipitacao):

		self.__cxv = cxv
		self.__precipitacao = precipitacao
		self.erroDeltaData()
		self.state = novaIteracao.COMUN

	@property
	def cxv(self):
		return self.__cxv

	@property
	def precipitacao(self):
		return self.__precipitacao

	def prec_metodologia(self, arquivo):
		modo = self.get_metodologia()
		return modo(arquivo)
	
	def erroDeltaData(self): # Se as datas não forem compativeis(Chuva dia x e modelo x-1, lança uma Excecção)
		if self.precipitacao.data - timedelta(days=1) != self.cxv.data:
			raise Exception('Insira um modelo de Chuva vazao compativel com no máximo, um dia a menos a previsao de precipitacao, para melhores resultados!')

	def get_metodologia(self):
		aux = self.precipitacao.path + '//' + os.listdir(self.precipitacao.path)[0]
		
		if len(open(aux).readlines()) > 55:
			novaIteracao.GERAL
			return b1
		
		else:
			return b2

	def iterPathRegions(self):
			caminhos_entrada =  [self.cxv.path + '//' + x + '//ARQ_ENTRADA' for x in self.cxv.regioes]
			caminhos_base = ['base//' + str(self.state) + '//' + j + '//Base.dat' for j in self.cxv.regioes]
			# Retorna duas listas de caminhos, a primeira com o caminho até o ARQ_ENTRADA a segunda com o caminho até os modelos de base.
			return caminhos_entrada, caminhos_base

class calculadora(novaIteracao):

	def __init__(self, cxv, prec):
		
		novaIteracao.__init__(cxv,prec)
		self.entrda, self.base = self.iterPathRegions()

	def main(self):
		
		for i in range(len(self.entrda)):

			for j in os.listdir(self.entrda[i]):
		
				if 'PMEDIA_ORIG' in j:

					aplicado = self.prec_metodologia(caminhos_entrada[i] + '//' + j)
					aplicado.sort(key=lambda x: (x[0],x[1]))
					base = self.prec_metodologia(caminhos_base[i])
					base.sort(key=lambda x: (x[0],x[1]))
					lista_auxiliar = []	





	


	
		
