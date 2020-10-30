# -*- coding: utf-8 -*-

from rastros import *
from threading import Thread
from datetime import datetime
from searchPlus import *
import sys


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


def astar_search_limited(problem, h=None, depth=5, maxNodes=1000000):
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search_limited(problem, lambda n: n.path_cost + h(n), depth, maxNodes)


def best_first_graph_search_limited(problem, f, depth, maxNodes):
    f = memoize(f, 'f')
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(min, f)
    frontier.append(node)
    explored = list()
    maxDepthNode = node
    while frontier:
        node = frontier.pop()
        if (maxDepthNode.depth < node.depth):
            maxDepthNode = node
        if problem.goal_test(node.state) or node.depth >= depth or len(explored) > maxNodes:
            return node
        explored.append(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                incumbent = frontier[child]
                if f(child) < f(incumbent):
                    del frontier[incumbent]
                    frontier.append(child)
    return maxDepthNode


class ProblemaRastros(Problem) :

    def __init__(self,initial = None, final = None):
        assert(final is not None)
        super().__init__(initial,final)
        
    def actions(self,estado) :
        return estado.moves()

    def result(self, state, move):
        blacks = state.blacks.copy() # Sim, temos de duplicar o conjunto de blacks
        blacks.add(state.white) ## marca a antiga white como black
        return EstadoRastros(to_move=('N' if state.to_move == 'S' else 'S'),
                         white=move,blacks=blacks) 
    
    def path_cost(self, c, state1, action, state2):
        return c + 1

    def goal_test(self, state):
        # if (len(state.moves()) == 0):
        #     print(state.white)
        #     return True
        return True if state.white == self.goal else False

    def h1(self,no):
        score = 0
        score += distancia(no.state.white, self.goal)
        if (existe_linha_ate_destino(no.state.white, no.state.blacks, self.goal)):
            score += abs((8-self.goal[1])-no.state.white[1])
        if (existe_coluna_ate_destino(no.state.white, no.state.blacks, self.goal)):
            score += abs((8-self.goal[0])-no.state.white[0])
        return score


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


def num_pretas_quadrado(branca, pretas, objectivo):
    blcorner = branca if distancia(branca, (8,1)) < distancia(objectivo, (8,1)) else objectivo
    trcorner = branca if blcorner == objectivo else objectivo
    #print(blcorner, trcorner)
    return len([b for b in pretas if (b[0] <= blcorner[0] and \
                                      b[0] >= trcorner[0] and \
                                      b[1] >= blcorner[1] and \
                                      b[1] <= trcorner[1])])

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



def num_pretas_em_linha_quadrado(branca, pretas, objectivo):
    blcorner = branca if distancia(branca, (8,1)) < distancia(objectivo, (8,1)) else objectivo
    trcorner = branca if blcorner == objectivo else objectivo
    counting = False
    maxnl = 0;
    #linhas
    for i in range(trcorner[0], blcorner[0]+1):
        nl = 0
        for j in range(blcorner[1], trcorner[1]):
            if counting:
                nl += 1
            if (i,j) in pretas:
                counting = True
            else:
                counting = False
                maxnl = nl if nl > maxnl else maxnl
                nl = 0
    # colunas
    for j in range(blcorner[1], trcorner[1]+1):
        nl = 0
        for i in range(trcorner[0], blcorner[0]):
            if counting:
                nl += 1
            if (i,j) in pretas:
                counting = True
            else:
                counting = False
                maxnl = nl if nl > maxnl else maxnl
                nl = 0
    return maxnl
    

def pretas_vert_horiz_adjacentes(white, blacks, fullboard):
    alladjacent = [(white[0]+a, white[1]) for a in [-2,-1,1,2]] + \
                  [(white[0], white[1]+a) for a in [-2,-1,1,2]]
    return len([p for p in alladjacent
                if p in blacks and p in fullboard])
        
# número pretas adjacentes em direcção ao objectivo
def pretas_vert_horiz_obliq_adjacentes(white, blacks, fullboard, obj, camadas):
    rowinc = 1 if obj==(8,1) else -1
    colinc = -1 if obj==(8,1) else 1
    alladjacent = [(white[0]+a, white[1]) for a in [rowinc*i for i in camadas]] + \
                  [(white[0], white[1]+a) for a in [rowinc*i for i in camadas]] + \
                  [(white[0]+a, white[1]+a) for a in [rowinc*i for i in camadas]]
    return len([p for p in alladjacent
                if p in blacks and p in fullboard])


# maior é melhor!
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


# maior é melhor!
def fun_aval_52_completa(estado, jogador, dicScoresOut=None):
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
        
        # p = ProblemaRastros(initial=estado, final=obj)
        # res_astar = astar_search_limited(problem=p,h=p.h1, depth=7, maxNodes=25)
        # score += (64 - max(res_astar.path_cost))
        #score += 64 - num_pretas_quadrado(estado.white, estado.blacks, obj)
        #score += num_pretas_quadrado(estado.white, estado.blacks, obja)
        #score += 64 - num_pretas_em_linha_quadrado(estado.white, estado.blacks, obj)
        #score += num_pretas_em_linha_quadrado(estado.white, estado.blacks, obja)
        #score += pretas_vert_horiz_adjacentes(estado.white, estado.blacks, estado.fullboard)
        
        camadas = [1,2,3]
        v = pretas_vert_horiz_obliq_adjacentes(estado.white, estado.blacks, estado.fullboard, obja, camadas) / 12
        if dicScoresOut!=None: dicScoresOut['pretas_vert_horiz_obliq_adjacentes'] = v
        score += v
        
        #score -= pretas_vert_horiz_obliq_adjacentes(estado.white, estado.blacks, estado.fullboard, obj, camadas) / 12
        
        if existe_linha_ate_destino(estado.white, estado.blacks, obj):
            score += -1
            if dicScoresOut!=None: dicScoresOut['existe_linha_ate_destino'] = -1
            # score += abs(estado.white[1]-obj[1])/7
        if existe_coluna_ate_destino(estado.white, estado.blacks, obj):
            score += -1
            if dicScoresOut!=None: dicScoresOut['existe_coluna_ate_destino'] = -1
            # score += abs(estado.white[0]-obj[0])/7
        if existe_linha_ate_destino(estado.white, estado.blacks, obja):
            score += 1
            if dicScoresOut!=None: dicScoresOut['existe_linha_ate_destino a'] = 1
            # score += (7-abs(estado.white[1]-obja[1]))/7
        if existe_coluna_ate_destino(estado.white, estado.blacks, obja):
            score += 1
            if dicScoresOut!=None: dicScoresOut['existe_coluna_ate_destino a'] = 1
            # score += (7-abs(estado.white[0]-obja[0]))/7

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


    
def sample_jogaRastrosNN(jogadorA, jogadorB, nsec=1, njogos=10):
    ### devolve uma lista de tuplos da forma (j1, j2, (lista de jogadas, vencedor))
    lista_jogos=[]
    k = 0
    for i in range(njogos):
        k += 1
        dt0 = datetime.now()
        resultado_jogo = (jogadorA.nome, jogadorB.nome, jogaRastros11com_timeout(jogadorA,jogadorB, nsec))
        lista_jogos.append(resultado_jogo)
        dt1 = datetime.now()
        print("jogo "+str(k)+": "+str(dt1-dt0)+"   "+str((resultado_jogo[0], resultado_jogo[1], resultado_jogo[2][1])))
    for i in range(njogos):
        k += 1
        dt0 = datetime.now()
        resultado_jogo = (jogadorB.nome, jogadorA.nome, jogaRastros11com_timeout(jogadorB,jogadorA, nsec))
        lista_jogos.append(resultado_jogo)
        dt1 = datetime.now()
        print("jogo "+str(k)+": "+str(dt1-dt0)+"   "+str((resultado_jogo[0], resultado_jogo[1], resultado_jogo[2][1])))
    return lista_jogos


def jogaRastros11com_timeout_posini(jog1, jog2, nsec, posini):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se S ganha
    game = Rastros()
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


# para threads
ljogos = {};

def th_worker(name):
    print("starting thread "+str(name))
    ljogos[name]= sample_jogaRastrosNN(basilio, specialOne, nsec=10)
    print("ending thread "+str(name))

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
    
    # print("pretas="+str(num_pretas_em_linha_quadrado((4,5), [(7,1), (7,2), (8,2), (2,6), (2,1)], (8,1))))
    # print("pretas="+str(num_pretas_em_linha_quadrado((4,5), [(7,1), (7,2), (8,2), (2,6), (2,1)], (1,8))))
    # print("pretas="+str(num_pretas_em_linha_quadrado((1,1), [(7,1), (7,2), (8,2), (2,6), (2,1)], (8,1))))
    # print("pretas="+str(num_pretas_em_linha_quadrado((8,1), [(7,1), (7,2), (8,2), (2,6), (2,1)], (1,8))))
    # sys.exit(0)
    
    
    ############# Tabuleiros ##########
    
    # random.seed(1234567)
    # s = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5..o.....
    #         6.@@.....
    #         7........
    #         8........"""
    # jogo_a_partir_de_posicao()
    # sys.exit(0)
    
    
    # s1 = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5........
    #         6........
    #         7..o.....
    #         8........"""
    
    # s2 = """  12345678
    #         1........
    #         2.....o..
    #         3........
    #         4.@......
    #         5.@......
    #         6.@......
    #         7.@......
    #         8.@......"""
    
    # s3 = """  12345678
    #         1........
    #         2........
    #         3..o.....
    #         4........
    #         5@@@@....
    #         6........
    #         7........
    #         8........"""
    
    # s4 = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5..@@....
    #         6...@....
    #         7...@....
    #         8...@...o"""
    
    # s5 = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5........
    #         6........
    #         7........
    #         8..o....."""
    
    # s6 = """  12345678
    #         1....o...
    #         2........
    #         3........
    #         4........
    #         5....@@..
    #         6....@@..
    #         7....@@..
    #         8....@@.."""
    
    # s7 = """  12345678
    #         1o.......
    #         2........
    #         3@@@.@@@.
    #         4........
    #         5........
    #         6........
    #         7........
    #         8........"""
    
    # s8 = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5........
    #         6..@o....
    #         7..@@@@@@
    #         8...@...."""
    
    # s9 = """  12345678
    #         1........
    #         2........
    #         3........
    #         4........
    #         5........
    #         6...o....
    #         7...@@@@@
    #         8...@@@@@"""
    
    # s10 = """  12345678
    #         1.....o..
    #         2......@.
    #         3.....@..
    #         4....@...
    #         5...@....
    #         6....@...
    #         7.....@@@
    #         8........"""
    
    # print(string_to_tabuleiro(s))
    # sys.exit(0)
    
    # dt0 = datetime.now();
    # white = (6,3)
    # blacks = (set([(i,j) for i in range(6,8) for j in range(1,6)]) - set(white)) | \
    #     set([(5,4),(5,5),(4,5)])
    # print(existe_linha_ate_destino(white, blacks, (8,1)))
    # print(existe_coluna_ate_destino(white, blacks, (8,1)))
    # #sys.exit(0)
    # state = EstadoRastros("S", white, blacks);
    # state.display()
    # p = ProblemaRastros(initial=state, final=(8,1))
    # res_astar = astar_search_limited(problem=p,h=p.h1,depth=5,maxNodes=50)
    # dt1 = datetime.now()
    # print(dt1-dt0);
    # sys.exit(0)
    
    dt0 = datetime.now();
    
    # th1 = Thread(target=th_worker, args=(1,))
    # th2 = Thread(target=th_worker, args=(2,))
    # th1.start()
    # th2.start()
    # th1.join();
    # th2.join();
    # campeonato = [item for key in ljogos for item in ljogos[key]];
    
    random.seed()
    campeonato = sample_jogaRastrosNN(basilio, specialOne, nsec=10, njogos=50)

    dt1 = datetime.now()        
    print(dt1-dt0);
    
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
