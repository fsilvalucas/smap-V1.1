import os
from datetime import datetime, timedelta
from src.classMongo import cmongo
import numpy as np
import sys
import time

def organizaArquivosDeSmap(cxv, nDias):

    path_to_model = cxv.path
    data = cxv.data
	
    # iter_model_regioes = [path_to_model + '//' + x + '//ARQ_ENTRADA' for x in cxv.regioes]
    # implementar:
    # talvez usar dask para atualizar cada dependencia ao mesmo tempo
    #for i in iter_model_regioes:
    for x in cxv.regioes:
        i = path_to_model + '//' + x + '//ARQ_ENTRADA'
        lista = caso(i)
        postos(lista, data, i, x)
        inicializacao(i, nDias)
        #precipitacao(i)
        postos_pluv(lista,data,i)

def escreve(file, linhas):

    with open(file, 'w') as txt:
        
        for i in range(len(linhas)):
            
            txt.writelines(linhas[i])

def caso(path): # Caso.txt contem as sub-bacias modeladas de cada BACIA SMAP
    
    lista = []
    
    with open(path + '\\CASO.txt', 'r') as txt:
        
        txt = txt.readlines()
        
        for i in range(len(txt)):
            
            txt[i] = txt[i].split()
        
        for i in range(1, len(txt), 1):

            if txt[i][0] == 'FUNIL': txt[i][0] = 'FUNIL MG'
            
            lista.append(txt[i][0])
    
    return lista

def postos(listaa, data, path, regiao):
    
    for i in listaa:

        if i.upper() + '.txt' in os.listdir(path):

            with open(path + '\\' + i + '.txt', 'r') as txt:

                lista = []
                txt = txt.readlines()

                for k in txt:

                    lista.append(k)

            data_modelo = lista[-1].split('|')[4]
            data_rodada = datetime.strptime(data_modelo, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)

            nova_linha = lista[-1].replace(data_modelo, data_rodada.strftime('%Y-%m-%d %H:%M:%S'))

            nova_linha = nova_linha.replace(nova_linha.split('|')[5], vazaoObservada(i, data_rodada, regiao))

            lista.append(nova_linha)

            with open(path + '\\' + i + '.txt', 'w') as wr:
                wr.writelines(lista)

def vazaoObservada(sub_bacia_modelada, data_procurada, regiao_smap):

    coll = cmongo('teste', 'vazao').collection
    valor = coll.find_one(  { 'BACIA' : regiao_smap }, {sub_bacia_modelada.upper() + '.' + data_procurada.strftime('%Y-%m-%d') : 1, '_id': 0}  )
    
    return str(valor[sub_bacia_modelada.upper()][data_procurada.strftime('%Y-%m-%d')])

def inicializacao(path, nDias):

    for i in os.listdir(path):

        if 'INICIALIZACAO' in i:

            with open(path + '\\' + i, 'r') as rd:

                rd = rd.readlines()
            rd[0] = rd[0].replace(rd[0][0:10], datetime.today().date().strftime('%d/%m/%Y'))
            rd[2] = rd[2].replace(rd[2][0:2], str(nDias))
            escreve(path + '\\' + i, rd)
            

def precipitacao(path):

    with open(path  + '\\MODELOS_PRECIPITACAO.txt', 'r') as modelo:

        textomodelo = '1\nPMEDIA_ORIG_\n'
        modelo.write(textomodelo)

def valor(k, data, bacia):

    # Limite usado para o $slice, Se a hora for maior que a hora atual, considerar a hora atual
    coll = cmongo('teste', 'teste').collection
    agora = datetime.now().hour
    
    if data.hour > agora: hora = 8
    else: hora = data.hour

    dat = data.replace(hour=0)#, day=8)

    aux = 12 # Prec obersava é um acumulado de 12 hrs
    d = 24 - (aux - hora) # logo, se hora for 8, deve buscar as outras 4hrs no dia anterior - [20:8]

    try:

        dicionario = coll.find_one({'data': dat}, { 'postos.' + bacia + '.' + k: 1, '_id': 0 }) # dia atual
        valor = np.sum(dicionario['postos'][bacia][k][0:hora])

        dicionario2 = coll.find_one({'data': dat - timedelta(days=1)}, { 'postos.' + bacia + '.' + k: 1, '_id': 0 }) # dia -1
        valor2 = np.sum(dicionario2['postos'][bacia][k][d:])
        
    
    except:
        
        if k == '0000A555':
            
            kk = '99990555'
            dicionario = coll.find_one({'data': dat}, { 'postos.' + bacia + '.' + kk: 1, '_id': 0 })
            valor = np.sum(dicionario['postos'][bacia][kk][0:hora])

            dicionario2 = coll.find_one({'data': dat - timedelta(days=1)}, { 'postos.' + bacia + '.' + kk: 1, '_id': 0 })
            valor2 = np.sum(dicionario2['postos'][bacia][kk][d:])
        
        elif k == '99990528':

            kk = '0000A528'
            dicionario = coll.find_one({'data': dat}, { 'postos.' + bacia + '.' + kk: 1, '_id': 0 })
            valor = np.sum(dicionario['postos'][bacia][kk][0:hora])

            dicionario2 = coll.find_one({'data': dat - timedelta(days=1)}, { 'postos.' + bacia + '.' + kk: 1, '_id': 0 })
            valor2 = np.sum(dicionario2['postos'][bacia][kk][d:])

        elif k == '99990823':
        
            dicionario = coll.find_one({'data': dat}, { 'postos.' + 'Iguacu' + '.' + k: 1, '_id': 0 })
            valor = np.sum(dicionario['postos']['Iguacu'][k][0:hora])

            dicionario2 = coll.find_one({'data': dat - timedelta(days=1)}, { 'postos.' + 'Iguacu' + '.' + k: 1, '_id': 0 })
            valor2 = np.sum(dicionario2['postos']['Iguacu'][k][d:])

        else:
            
            dicionario = coll.find_one({'data': dat}, { 'postos.' + 'Grande' + '.' + k: 1, '_id': 0 })
            valor = np.sum(dicionario['postos']['Grande'][k][0:hora])

            dicionario2 = coll.find_one({'data': dat - timedelta(days=1)}, { 'postos.' + 'Grande' + '.' + k: 1, '_id': 0 })
            valor2 = np.sum(dicionario2['postos']['Grande'][k][d:])

    return  str(valor + valor2)

def postos_pluv(listaa, data_rodada, path):

    for i in listaa:

        if i.upper() + '.txt' in os.listdir(path):
            
            with open(path + '\\' + i + '_POSTOS_PLU.txt', 'r') as txt:
                
                lista = []
                txt = txt.readlines()
                
                for k in txt:
                    
                    if len(k.split()) < 2: pass
                    
                    else: lista.append(k.split()[0])
            
            for k in lista:

                with open(path + '\\' + k + '_C.txt', 'r') as sla:

                    sla = sla.readlines()

                data = datetime.strptime(sla[-1].split()[1] + ' ' + sla[-1].split()[2], '%d/%m/%Y %H%M')
                
                if data.date() == datetime.today().date():
                    
                    pass
                
                else:

                    if sla[-1].split()[-1] == '-': sla.append(k + (data +timedelta(days=1)).strftime(' %d/%m/%Y %H%M ') + '-')
                    
                    else: sla.append(k + (data +timedelta(days=1)).strftime(' %d/%m/%Y %H%M ') + valor(k, data+timedelta(days=1), path.split('//')[1]))

                    with open(path + '\\' + k + '_C.txt', 'w') as wr:
                        wr.writelines(sla)




    #a= """dicionario = coll.find_one(
    #    {
    #        'data': datarodada
    #    }, 
    #    { 
    #        'postos.Grande.61880000': 1, '_id':0 # Example of the API application
    #    }
    #)
    #pass """