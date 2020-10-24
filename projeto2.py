# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from rastros import *
from threading import Thread
from datetime import datetime
import sys

def num_pretas_quadrado(branca, pretas, objectivo):
    blcorner = branca if distancia(branca, (8,1)) < distancia(objectivo, (8,1)) else objectivo
    trcorner = branca if blcorner == objectivo else objectivo
    #print(blcorner, trcorner)
    return len([b for b in pretas if (b[0] <= blcorner[0] and \
                                      b[0] >= trcorner[0] and \
                                      b[1] >= blcorner[1] and \
                                      b[1] <= trcorner[1])])


# maior é melhor!
def fun_aval_52(estado, jogador):
    if estado.terminou == 1:
        return 10 if jogador == "S" else -10
    elif estado.terminou == -1:
        return 10 if jogador == "N" else -10
    else:
        obj = (8, 1) if jogador == "S" else (1, 8)
        score = 0;
        score += 7 - distancia(estado.white, obj)
        #score += 64 - num_pretas_quadrado(estado.white, estado.blacks, obj)
        score += 100*num_pretas_quadrado(estado.white, estado.blacks, (8,1) if obj==(1,8) else (1,8))
        return score


specialOne = Jogador("SpecialOne",
                  lambda game, state:
                  alphabeta_cutoff_search_new(state,game,depth_for_all,eval_fn=fun_aval_52))

    
def sample_jogaRastrosNN(jogadorA, jogadorB, nsec=1):
    ### devolve uma lista de tuplos da forma (j1, j2, (lista de jogadas, vencedor))
    lista_jogos=[]
    for i in range(10):
        lista_jogos.append((jogadorA.nome, jogadorB.nome, jogaRastros11com_timeout(jogadorA,jogadorB, nsec)))
    for i in range(10):
        lista_jogos.append((jogadorB.nome, jogadorA.nome, jogaRastros11com_timeout(jogadorB,jogadorA, nsec)))
    return lista_jogos

lista_jogos = {};

def th_worker(name):
    lista_jogos[name]= sample_jogaRastrosNN(basilio, specialOne, nsec=10)

if __name__ == "__main__":
    # jogo1 = jogaRastros11(obtusoSW, bacoco)
    # print(jogo1)
    # print()
    # mostraJogo(jogo1[0])
    # print()
    # mostraJogo(jogo1[0], verbose = True)
    # print()
    #todosJog = [bacoco, obtusoSW, obtusoNE, arlivre, basilio]
    
    # print("pretas="+str(num_pretas_quadrado((4,5), [(7,1), (8,2), (2,6), (2,1)], (8,1))))
    # print("pretas="+str(num_pretas_quadrado((4,5), [(7,1), (8,2), (2,6), (2,1)], (1,8))))
    # print("pretas="+str(num_pretas_quadrado((1,1), [(7,1), (8,2), (2,6), (2,1)], (8,1))))
    # print("pretas="+str(num_pretas_quadrado((8,1), [(7,1), (8,2), (2,6), (2,1)], (1,8))))
    # sys.exit(0)
    
    # dt0 = datetime.now();
    # th1 = Thread(target=th_worker, args=(1,))
    # #th2 = Thread(target=th_worker, args=(2,))
    # th1.start()
    # #th2.start()
    # th1.join();
    # #th2.join();
    # dt1 = datetime.now();
    # print(dt1-dt0);
    
    # campeonato = [item for sublist in lista_jogos for item in sublist];
    
    campeonato = sample_jogaRastrosNN(basilio, specialOne, nsec=10)
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
