from src.classes import modelo_precipitacao
from src.classes import modelo_cxv
from src.classes import rodada
from datetime import date


print('Insira a o ano do modelo CxV:')
ano = int(input())
print('Insira a o mes do modelo CxV:')
mes = int(input())
print('Insira a o dia do modelo CxV:')
dia = int(input())

data = date(ano,mes,dia)

chuva = modelo_precipitacao()
cxv = modelo_cxv(data)

modelo = rodada(cxv, chuva)
print(modelo.state)
modelo.rodada()

