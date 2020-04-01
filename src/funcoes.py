def base_geral(file):  # File: ETA-GEFS geral (22mil linhas)
    b = open(file)
    t = b.readlines()
    i = 0
    test = []
    fest = []
    for lines in t:
        lines.replace('\n', '')

        if len(lines) >= 19:
            test.append(float(lines[0:6]))
            test.append(float(lines[7:12]))
            test.append(float(lines[13:18]))

        elif len(lines) == 18:
            test.append(float(lines[0:6]))
            test.append(float(lines[7:13]))
            test.append(float(lines[13:18]))

        elif len(lines) == 17:
            test.append(float(lines[0:6]))
            test.append(float(lines[7:12]))
            test.append(float(lines[12:16]))

        elif len(lines) == 16:
            test.append(float(lines[0:6]))
            test.append(float(lines[7:11]))
            test.append(float(lines[12:16]))
        try:
            fest.append(test[i:i + 3])
        except:
            pass

        i = i + 3

    return fest

def base_comun(file):  # File: Eta-Gefs de cada bacia
    b = open(file)
    t = b.readlines()
    i = 0
    test = []
    fest = []

    for lines in t:
        
        lines.replace('\n', '')
        test.append(float(lines[0:6]))
        test.append(float(lines[7:13]))
        test.append(float(lines[13:18]))
        fest.append(test[i:i + 3])

        i = i + 3

    return fest

def searchBinary(procurado, base): #  def buscaBinaria(procurado, base): 
        # busca no geral, o procurado (x, y) do ETA-GEFS bacia, e retorna o procurado do
        # geral
        cabeca = 0
        cauda = len(base) - 1
        meio = (cabeca + cauda) // 2

        if procurado == base[meio][0:2]:
            return base[meio][2]

        if procurado == base[cauda][0:2]:
            return base[cauda][2]  

        if procurado == base[cabeca][0:2]:
            return base[cabeca][2]     

        elif procurado < base[meio][0:2]:
            return searchBinary(procurado, base[cabeca:meio])
            
        else:
            return searchBinary(procurado, base[meio:cauda + 1])

def escreve(file, linhas):
    with open(file, 'w') as wd:
        for i in range(len(linhas)):
            wd.writelines(linhas[i])


