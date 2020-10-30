#!/usr/bin/env python
# coding: utf-8

# #  Jogo dos Rastros
# ## Projeto nº 2
# ### Introdução à Inteligência Artificial edição 2020/21
# 
# 
# ## Grupo: 52
# 
# ### Elementos do Grupo
# 
# Nome: António Fróis
# 
# Número: 51050
# 
# Nome: Rui Fartaria
# 
# Número: 18752
# 

# ### Explicação da função e sua lógica
# 
# Dado um jogador e o seu objectivo ("n(1,8)" ou "s(8,1)") devolve um *score* para a posição. O valor do *score* informa sobre o valor da posição para esse jogador, sendo que um valor maior indica que a posição é mais favorável à vitória desse jogador.
# 
# #### Heurísticas implementadas
# 
# ##### Vitória e derrota
# 
# Já vinham pré-implementadas e dão um *score* de +10 à vitória e -10 à  derrota. Funcionam detectando se a posição da branca se encontra num dos objectivos (N ou S).
# 
# ##### Distância ao objectivo
# 
# Melhor quanto menor for a distância ao objectivo. O valor foi normalizado para o intervalo [0,1]
# 
# ##### Existe linha até objectivo
# 
# Se existe uma linha completa com casas pretas a contar da coluna do objectivo até à coluna da branca, e numa linha entre a linha da branca e a linha do objectivo, então soma -1 ao *score*. Isto porque quer dizer que essa via está bloqueada e portanto é uma situação desfavorável para o jogador.
# 
# ##### Existe coluna até objectivo
# 
# Se existe uma coluna completa com casas pretas a contar da linha do objectivo até à linha da branca, e numa coluna entre a coluna da branca e a coluna do objectivo, então soma -1 ao *score*. Isto porque quer dizer que essa via está bloqueada e portanto é uma situação desfavorável para o jogador.
# 
# ##### Existe linha até objectivo do adversário
# 
# Se existe uma linha completa com casas pretas a contar da coluna do objectivo adversário até à coluna da branca, e numa linha entre a linha da branca e a linha do objectivo advesário, então soma 1 ao *score*. Isto porque quer dizer que essa via está bloqueada e portanto é uma situação favorável para o jogador.
# 
# ##### Existe coluna até objectivo do adversário
# 
# Se existe uma coluna completa com casas pretas a contar da linha do objectivo adversário até à linha da branca, e numa coluna entre a coluna da branca e a coluna do objectivo adversário, então soma 1 ao *score*. Isto porque quer dizer que essa via está bloqueada e portanto é uma situação favorável para o jogador.
# 
# ##### Número de casas pretas nas vertical, horizontal, e diagonal em direcção ao objectivo do adversário
# 
# O jogador deve jogar de forma a maximizar o número de pretas entre si o objectivo do adversário. Experimentámos também com o número total de pretas (e não apenas verticais e diagonais) mas os resultados não foram tão bons.
# Portanto o *score* é positivo e foi normalisado para o intervalo [0,1]. Foram consideradas as primeiras 3 camadas envolventes.
# 
# Tentamos também usar uma heuristica para minimizar o número de casas pretas na direcção do objectivo mas os resultados não foram favoráveis.
# 
# 
# ##### Número de casas pretas por camada envolvente
# 
# Para valorizar o tipo de finalização por inexistência de jogadas implementámos uma heurística em que:
# 1. Se as casas envolventes na primeira camada são pretas, então ganhou, e devolve o mesmo "score" que para a vitória.
# 2. Se as casas envolventes na segunda camada são pretas, então é favorável se o número de casas é ímpar. Ou seja, o jogador está encurralado, mas tem um número de casas disponíveis para terminar numa jogada em que é o adversário que fica sem jogadas.

# In[7]:



from rastros import *

def existe_linha_ate_destino(branca, pretas, objectivo):
    assert(objectivo in {(8,1),(1,8)})
    
    if (objectivo == (8,1)):
        for i in range(branca[0]+1, 9):
            line = True
            for j in range(1,branca[1]+1):
                if (i,j) not in pretas:
                    line = False
                    break
            if (line):
                return True;
    
    if (objectivo == (1,8)):
        for i in range(1, branca[0]):
            line = True
            for j in range(branca[1],9):
                if (i,j) not in pretas:
                    line = False
                    break
            if (line):
                return True
    
    return False


def existe_coluna_ate_destino(branca, pretas, objectivo):
    assert(objectivo in {(8,1),(1,8)})
    
    if (objectivo == (8,1)):
        for j in range(1, branca[1]):
            column = True
            for i in range(branca[0],9):
                if (i,j) not in pretas:
                    column = False
                    break
            if (column):
                return True;
    
    if (objectivo == (1,8)):
        for j in range(branca[1], 9):
            column = True
            for i in range(1,branca[0]):
                if (i,j) not in pretas:
                    column = False
                    break
            if (column):
                return True
    
    return False


def num_pretas_camadas(branca, pretas, fullboard, camadas):
    casas = []
    for c in camadas:
        for i in [branca[0]-c, branca[0]+c]:
            for j in range(branca[1]-c, branca[1]+c+1):
                casas.append((i,j))
        for j in [branca[1]-c, branca[1]+c]:
            for i in range(branca[0]-c, branca[0]+c+1):
                casas.append((i,j))
    casas = set(casas)
    return (len(casas & pretas), len(casas & fullboard))


# número pretas adjacentes em direcção ao objectivo
def pretas_vert_horiz_obliq_adjacentes(white, blacks, fullboard, obj, camadas):
    rowinc = 1 if obj==(8,1) else -1
    colinc = -1 if obj==(8,1) else 1
    alladjacent = [(white[0]+a, white[1]) for a in [rowinc*i for i in camadas]] +                   [(white[0], white[1]+a) for a in [rowinc*i for i in camadas]] +                   [(white[0]+a, white[1]+a) for a in [rowinc*i for i in camadas]]
    return len([p for p in alladjacent
                if p in blacks and p in fullboard])


def fun_aval_52(estado, jogador):
    if estado.terminou == 1:
        score = 10 if jogador == "S" else -10
        return score
    elif estado.terminou == -1:
        score = 10 if jogador == "N" else -10 
        return score
    else:
        obj = (8, 1) if jogador == "S" else (1, 8)
        obja = (8,1) if obj==(1,8) else (1,8)
        score = 0;
        
        d = distancia(estado.white, obj)
        score += (7 - d) / 7
        
        camadas = [1,2,3]
        v = pretas_vert_horiz_obliq_adjacentes(estado.white, estado.blacks, estado.fullboard, obja, camadas) / 12
        score += v
        
        if existe_linha_ate_destino(estado.white, estado.blacks, obj):
            score += -1
        if existe_coluna_ate_destino(estado.white, estado.blacks, obj):
            score += -1
        if existe_linha_ate_destino(estado.white, estado.blacks, obja):
            score += 1
        if existe_coluna_ate_destino(estado.white, estado.blacks, obja):
            score += 1

        npc1, nc1 = num_pretas_camadas(estado.white, estado.blacks, estado.fullboard, [1])
        v = 10 if nc1 == npc1 else 0
        score += v
        if nc1 != npc1:
            npc2, nc2 = num_pretas_camadas(estado.white, estado.blacks, estado.fullboard, [2])
            v = 1 if nc2 == npc2 and  nc1-npc1%2==1 else 0
            score += v
        return score


# ### Demonstração
# (Mostrem que o código está a funcionar, com exemplos adequados, executem um ou mais jogos, mostrem os seus resultados, exibam situações de jogo que demonstrem que a lógica da vossa função está correctamente implementada.)

# ## Demonstração 20 jogos: 10+10

# In[8]:


from datetime import datetime

def jogaRastros11com_timeout_posini(jog1, jog2, nsec, posini=None):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se S ganha
    game = Rastros()
    if posini!=None:
        game.initial = posini
    estado=game.initial
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
        try:
            ReturnedValue = func_timeout(nsec, proxjog.fun, args=(game, estado))
        except FunctionTimedOut:
            print("pim!", proxjog.nome)
            ReturnedValue = None    
        jogada = ReturnedValue
        if jogada == None:
            estado.terminou = 1 if proxjog==jog2 else -1 # se norte deu timeout ganha sul e vice-versa 
            return (lista_jogadas, estado.terminou)
        else:
            estado=game.result(estado,jogada)
            lista_jogadas.append((proxjog.nome, jogada))
            proxjog = jog2 if proxjog == jog1 else jog1
    return (lista_jogadas, estado.terminou)


def sample_jogaRastrosNN(jogadorA, jogadorB, nsec=1, njogos=10):
    ### devolve uma lista de tuplos da forma (j1, j2, (lista de jogadas, vencedor))
    lista_jogos=[]
    k = 0
    for i in range(njogos):
        k += 1
        dt0 = datetime.now()
        resultado_jogo = (jogadorA.nome, jogadorB.nome, jogaRastros11com_timeout_posini(jogadorA,jogadorB, nsec))
        lista_jogos.append(resultado_jogo)
        dt1 = datetime.now()
        print("jogo "+str(k)+": "+str(dt1-dt0)+"   "+str((resultado_jogo[0], resultado_jogo[1], resultado_jogo[2][1])))
    for i in range(njogos):
        k += 1
        dt0 = datetime.now()
        resultado_jogo = (jogadorB.nome, jogadorA.nome, jogaRastros11com_timeout_posini(jogadorB,jogadorA, nsec))
        lista_jogos.append(resultado_jogo)
        dt1 = datetime.now()
        print("jogo "+str(k)+": "+str(dt1-dt0)+"   "+str((resultado_jogo[0], resultado_jogo[1], resultado_jogo[2][1])))
    return lista_jogos


specialOne = Jogador("SpecialOne",
                  lambda game, state:
                  alphabeta_cutoff_search_new(state,game,depth_for_all,eval_fn=fun_aval_52))

random.seed()
campeonato = sample_jogaRastrosNN(basilio, specialOne, nsec=10, njogos=10)

print()
resultado_jogos = [(a,b,n) for (a,b,(x,n)) in campeonato]
tabela = dict([(jog.nome, 0) for jog in [basilio, specialOne]])
for jogo in resultado_jogos:
    if jogo[2] == 1:
        tabela[jogo[0]] += 1
    else:
        tabela[jogo[1]] += 1
classificacao = list(tabela.items())
classificacao.sort(key=lambda p: -p[1])
print("JOGADOR", "VITÓRIAS")
for jog in classificacao:
    print('{:11}'.format(jog[0]), '{:>4}'.format(jog[1]))


# #### Análise de casos específicos
# 
# Gostaríamos de referir que implementámos mais algumas funções para facilitar a análise de casos específicos, nomeadamente:
# 1. Converter string para tabuleiro
# 2. Mostrar caminho percorrido num só tabuleiro
# 3. Registar os scores individuais de cada heurística

# In[9]:


# -*- coding: utf-8 -*-
from rastros import *

def string_to_tabuleiro(strt):
    lines = strt.splitlines()
    blacks=[]
    i=0
    for line1 in lines:
        line = line1.strip('12345678 ')
        #print(line)
        if len(line) != 8:
            continue
        for j in range(len(line)):
            if (line[j] == 'o'):
                white = (i+1,j+1)
            if (line[j] == '@'):
                blacks += [(i+1,j+1)]
        i += 1
    return (white, set(blacks))


def tabuleiro_to_string(white, blacks):
    s = " 12345678\n"
    for i in range(1, 9):
        s += str(i)
        for j in range(1, 9):
            s += "@" if (i,j) in blacks else "o" if (i,j)==white else "."
        s += str(i)+"\n"
    s += " 12345678 "
    return s


def moves_to_string(iwhite, iblacks, moves):
    st = tabuleiro_to_string(iwhite, iblacks)
    lines = [[c for c in l] for l in st.splitlines()]
    n = 0
    for m in moves:
        c = "2" if n%2==0 else "5"
        lines[m[0]] = lines[m[0]][:m[1]] + ["\u001b[38;5;" + c + "m" + str(n) + "\u001b[0m"] + lines[m[0]][m[1]+1:]
        n = (n+1) % 10
    return "\n".join(["".join(l) for l in lines])




# maior é melhor!
# é a mesma que a definida anteriormente mas com possibilidade de registar os scores
def fun_aval_52(estado, jogador, dicScoresOut=None):
    if estado.terminou == 1:
        score = 10 if jogador == "S" else -10
        if dicScoresOut!=None: dicScoresOut['final'] = score
        return score
    elif estado.terminou == -1:
        score = 10 if jogador == "N" else -10 
        if dicScoresOut!=None: dicScoresOut['final'] = score
        return score
    else:
        obj = (8, 1) if jogador == "S" else (1, 8)
        obja = (8,1) if obj==(1,8) else (1,8)
        score = 0;
        
        d = distancia(estado.white, obj)
        score += (7 - d) / 7
        if dicScoresOut!=None: dicScoresOut['distancia'] = score
        
        camadas = [1,2,3]
        v = pretas_vert_horiz_obliq_adjacentes(estado.white, estado.blacks, estado.fullboard, obja, camadas) / 12
        if dicScoresOut!=None: dicScoresOut['pretas_vert_horiz_obliq_adjacentes'] = v
        score += v
        
        if existe_linha_ate_destino(estado.white, estado.blacks, obj):
            score += -1
            if dicScoresOut!=None: dicScoresOut['existe_linha_ate_destino'] = -1
        if existe_coluna_ate_destino(estado.white, estado.blacks, obj):
            score += -1
            if dicScoresOut!=None: dicScoresOut['existe_coluna_ate_destino'] = -1
        if existe_linha_ate_destino(estado.white, estado.blacks, obja):
            score += 1
            if dicScoresOut!=None: dicScoresOut['existe_linha_ate_destino a'] = 1
        if existe_coluna_ate_destino(estado.white, estado.blacks, obja):
            score += 1
            if dicScoresOut!=None: dicScoresOut['existe_coluna_ate_destino a'] = 1

        npc1, nc1 = num_pretas_camadas(estado.white, estado.blacks, estado.fullboard, [1])
        v = 10 if nc1 == npc1 else 0
        if dicScoresOut!=None: dicScoresOut['num_pretas_camadas 1'] = v
        score += v
        if nc1 != npc1:
            npc2, nc2 = num_pretas_camadas(estado.white, estado.blacks, estado.fullboard, [2])
            v = 1 if nc2 == npc2 and  nc1-npc1%2==1 else 0
            if dicScoresOut!=None: dicScoresOut['num_pretas_camadas 2'] = v
            score += v
        return score


specialOne = Jogador("SpecialOne",
                  lambda game, state:
                  alphabeta_cutoff_search_new(state,game,depth_for_all,eval_fn=fun_aval_52))

    
def mostraJogo52(inicial, listajog, verbose = False, step_by_step=False, show_scores=False):
    j = Rastros()
    j.initial = inicial
    estado = j.initial
    for jog in listajog:
        if verbose:
            j.display(estado)
            if show_scores:
                d = {}
                result = fun_aval_52(estado, estado.to_move, d)
                for k in d:
                    print(str(k) + ": " + str(d[k]))
        if step_by_step:
            input()
        estado=j.result(estado,jog[1])
        print(jog[0]+ "--> ", str(jog[1]))
    if verbose:
        j.display(estado)
    print('{}'.format("Ganhou S" if estado.terminou == 1 else "Ganhou N" if estado.terminou == -1 else "Empate"))


def jogo_a_partir_de_posicao():
    tabuleiro = string_to_tabuleiro(s)
    inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
    jogo = jogaRastros11com_timeout_posini(basilio, specialOne, 10, inicial)
    print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
    mostraJogo52(inicial, jogo[0], verbose = True, show_scores=True)
    


# ### Análise de existência de coluna até ao objetivo adversário
# 
# Neste caso existe uma coluna até ao caminho do objetivo adversário, ou seja, o objetivo do nosso jogador é afastar-se dessa coluna e preencher as outras casas restantes. É possível observar as 10 primeiras jogadas deste jogo. Somos o jogador **N** e o Basílio é o **S**.
# 
# O Basílio começa a jogar segundo a única heurística que tem, isto é, a distância até ao objetivo. De seguida começamos a jogar de forma a afastarmo-nos da coluna e de forma a preencher as casas vazias e isso vai acontecendo ao longo de várias jogadas até se preencher a parte inferior do tabuleiro. Quando esta está preenchida, começamos a jogar de forma a chegarmos ao objetivo.
# 

# In[10]:


s = """  12345678
        1........
        2.....o..
        3........
        4.@......
        5.@......
        6.@......
        7.@......
        8.@......"""

tabuleiro = string_to_tabuleiro(s)

inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
random.seed(1234567)
jogo = jogaRastros11com_timeout_posini(basilio, specialOne, 10, inicial)
print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
mostraJogo52(inicial, jogo[0][:10], verbose = True, show_scores=True)


# ### Análise de existência de coluna até ao objetivo
# 
# Neste caso existe uma coluna até ao caminho do nosso objetivo, ou seja, o objetivo do nosso jogador é exatamente o contrário do caso anterior, isto é, tentarmos passar a coluna e de seguida ao objetivo. É possível observar as 10 primeiras jogadas deste jogo. Somos o jogador **S** e o Basílio é o **N**.
# 
# Nós começamos a jogar. De seguida joga o Basílio, que como se pode reparar começa a jogar de forma a atinigir o seu objetivo considerando apenas a distância. À medida que o jogo se desenrola repara-se que nós tentamos chegar à coluna mas o Basílio corta todos os caminhos para lá chegar.

# In[11]:


s = """  12345678
        1........
        2.....o..
        3........
        4.@......
        5.@......
        6.@......
        7.@......
        8.@......"""

tabuleiro = string_to_tabuleiro(s)

inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
random.seed(1234567)
jogo = jogaRastros11com_timeout_posini(specialOne, basilio, 10, inicial)
print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
mostraJogo52(inicial, jogo[0][:10], verbose = True, show_scores=True)


# ### Análise de existência de linha até ao objetivo 
# 
# Neste caso nós somos o jogador **S** e o Basílio é o **N**. Aqui o que acontece é mesmo do que acontece na situação da coluna, ou seja, como o nosso objetivo é chegar à casa **S** então temos que contornar a linha. É possível observar 10 jogadas.
# 
# Ao longo do decorrer do jogo é possível verificar que no início estamos a tentar contornar a linha existente até ao nosso objetivo mas como o Basílio vai puxando a bola branca para o seu objetivo, então começamos a tentar preencher casas vazias no campo adversário. 
# 
# 

# In[12]:



 s = """  12345678
         1........
         2........
         3..o.....
         4........
         5@@@@....
         6........
         7........
         8........"""

tabuleiro = string_to_tabuleiro(s)

inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
random.seed(1234567)
jogo = jogaRastros11com_timeout_posini(specialOne, basilio, 10, inicial)
print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
mostraJogo52(inicial, jogo[0][:10], verbose = True, show_scores=True)


# ### Análise de existência de linha até ao objetivo adversário
# 
# Neste caso nós somos o jogador **N** e o Basílio é o **S**. Aqui o que acontece é mesmo do que acontece na situação da coluna até ao objetivo adversário, ou seja, como o nosso objetivo é chegar à casa **N** então temos que nos afastar da linha. É possível observar 10 jogadas.
# 
# Ao longo do decorrer do jogo é possível verificar que no início estamos a tentar afasatar-nos da linha mas ao fazê-lo criamos uma coluna até ao nosso objetivo então começamos a contornar a coluna que foi criada e de seguida começamos a tentar maximizar o número de casas pretas no objetivo adversário de forma a encurralá-lo até que o fazemos e ganhamos o jogo.
# 
# 

# In[13]:



 s = """  12345678
         1........
         2........
         3..o.....
         4........
         5@@@@....
         6........
         7........
         8........"""

tabuleiro = string_to_tabuleiro(s)

inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
random.seed(1234567)
jogo = jogaRastros11com_timeout_posini(basilio, specialOne, 10, inicial)
print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
mostraJogo52(inicial, jogo[0][:10], verbose = True, show_scores=True)


# ### Análise de maximização de casas pretas no lado adversário
# 
# Neste caso nós somos o jogador **N** e o Basílio é o **S**. É possível observar as 10 primeiras jogadas.
# 
# Nesta situação em que estamos quase a perder, ao longo do jogo verifica-se que as nossas prioridades neste caso são tanto afastarmo-nos do objetivo adversário como maximizar as casa pretas no lado adversário. Nestas 10 jogadas conseguimos fazê-lo de forma a bloquearmos o objetivo adversário.
# 
# 

# In[14]:


s = """  12345678
         1........
         2........
         3........
         4........
         5........
         6........
         7..o.....
         8........"""

tabuleiro = string_to_tabuleiro(s)

inicial = EstadoRastros(to_move="S", white=tabuleiro[0], blacks=tabuleiro[1])
random.seed(1234567)
jogo = jogaRastros11com_timeout_posini(basilio, specialOne, 10, inicial)
print(moves_to_string(tabuleiro[0],tabuleiro[1],[i[1] for i in jogo[0]]))
mostraJogo52(inicial, jogo[0][:10], verbose = True, show_scores=True)

