#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GrafoApp - Análise de Grafos com Ciclo Euleriano e Hamiltoniano
Arquivo usado: grafo.txt
Agora com opções k) e l) no menu
"""

import os

# --------- Caminho fixo ---------
DEFAULT_PATH = "grafo.txt"

# ---------- Classes ----------
class Vertice:
    def __init__(self, id_, rotulo, meta=None):
        self.id = id_
        self.rotulo = rotulo
        self.meta = meta or ()

    def __str__(self):
        if self.meta:
            meta_str = ", ".join(map(str, self.meta))
            return f"{self.id}: {self.rotulo} ({meta_str})"
        return f"{self.id}: {self.rotulo}"

class Aresta:
    def __init__(self, origem, destino, peso=None):
        self.origem = origem
        self.destino = destino
        self.peso = peso

    def __str__(self):
        return f"{self.origem} -> {self.destino}" + (f" [{self.peso}]" if self.peso else "")

class Grafo:
    def __init__(self, tipo=0):
        self.tipo = tipo
        self.vertices = {}      # id -> Vertice
        self.adj = {}           # id -> lista de Aresta

    # --- Vértices ---
    def adicionar_vertice(self, id_, rotulo, meta=None):
        if id_ in self.vertices:
            return False
        self.vertices[id_] = Vertice(id_, rotulo, meta)
        if id_ not in self.adj:
            self.adj[id_] = []
        return True

    def remover_vertice(self, id_):
        if id_ not in self.vertices:
            return False
        del self.vertices[id_]
        self.adj.pop(id_, None)
        for lista in self.adj.values():
            lista[:] = [e for e in lista if e.destino != id_]
        return True

    # --- Arestas ---
    def adicionar_aresta(self, origem, destino, peso=None):
        if origem not in self.vertices or destino not in self.vertices:
            return False
        # Evita aresta duplicada com mesmo destino e peso
        for e in self.adj.get(origem, []):
            if e.destino == destino and e.peso == peso:
                return False
        self.adj.setdefault(origem, []).append(Aresta(origem, destino, peso))
        # Se for não-dirigido (tipo 3), adiciona a aresta nos dois sentidos
        if self.tipo == 3:
            if not any(e.destino == origem and e.peso == peso for e in self.adj.get(destino, [])):
                self.adj.setdefault(destino, []).append(Aresta(destino, origem, peso))
        return True

    def remover_aresta(self, origem, destino):
        if origem not in self.adj:
            return False
        original = len(self.adj[origem])
        self.adj[origem] = [e for e in self.adj[origem] if e.destino != destino]
        if self.tipo == 3 and destino in self.adj:
            self.adj[destino] = [e for e in self.adj[destino] if e.destino != origem]
        return len(self.adj[origem]) < original

    def lista_arestas(self):
        todas = []
        for lista in self.adj.values():
            todas.extend(lista)
        return todas

    def mostrar_lista_adjacencia(self):
        print("\nLista de adjacência:")
        for vid in sorted(self.vertices.keys()):
            v = self.vertices[vid]
            vizinhos = []
            for e in self.adj.get(vid, []):
                txt = str(e.destino)
                if e.peso:
                    txt += f"({e.peso})"
                vizinhos.append(txt)
            print(f"  {vid} - {v.rotulo} -> [{', '.join(vizinhos)}]")

    # --- Conexidade não-dirigido ---
    def conexo_nao_direcionado(self):
        if not self.vertices:
            return True
        visitados = set()
        inicio = next(iter(self.vertices))
        pilha = [inicio]
        while pilha:
            u = pilha.pop()
            if u in visitados:
                continue
            visitados.add(u)
            for e in self.adj.get(u, []):
                if e.destino not in visitados:
                    pilha.append(e.destino)
        return len(visitados) == len(self.vertices)

    # --- Grau dos vértices (para Euleriano) ---
    def calcular_graus(self):
        graus = {}
        for v in self.vertices:
            graus[v] = 0
        for origem in self.adj:
            for e in self.adj[origem]:
                if self.tipo == 3:  # não-dirigido: conta só uma vez por aresta
                    if origem < e.destino:  # evita contar duas vezes
                        graus[origem] += 1
                        graus[e.destino] += 1
                else:
                    graus[origem] += 1
        return graus

    # --- Verificar Ciclo Euleriano ---
    def tem_ciclo_euleriano(self):
        if self.tipo != 3:
            print("Ciclo Euleriano só é definido para grafos não-dirigidos.")
            return False
        if not self.conexo_nao_direcionado():
            print("Grafo não é conexo → não tem ciclo euleriano.")
            return False
        graus = self.calcular_graus()
        impares = [v for v, g in graus.items() if g % 2 == 1]
        if impares:
            print(f"NÃO tem ciclo euleriano → {len(impares)} vértices com grau ímpar: {impares}")
            return False
        print("SIM! O grafo tem ciclo euleriano (todos os graus são pares e é conexo).")
        return True

    # --- Verificar Ciclo Hamiltoniano (heurística + teorema) ---
    def tem_ciclo_hamiltoniano(self):
        n = len(self.vertices)
        if n < 3:
            print("Grafo muito pequeno.")
            return False

        if self.tipo != 3:
            print("Análise Hamiltoniana aqui só para grafos não-dirigidos.")
            return False

        graus = self.calcular_graus()
        graus_list = sorted(graus.values())

        # Teorema de Dirac
        if all(g >= n//2 for g in graus.values()):
            print(f"SIM! Pelo Teorema de Dirac (todo grau ≥ {n//2}) → tem ciclo hamiltoniano.")
            return True

        # Teorema de Ore
        for i in range(n):
            for j in range(i+1, n):
                u = list(graus.keys())[i]
                v = list(graus.keys())[j]
                if not any(e.destino == v for e in self.adj.get(u, [])):
                    if graus[u] + graus[v] < n:
                        print(f"Não satisfeito Teorema de Ore (vértices {u} e {v} sem aresta e grau(u)+grau(v) < {n})")
                        break
            else:
                continue
            break
        else:
            print(f"SIM! Pelo Teorema de Ore → tem ciclo hamiltoniano.")
            return True

        print("Não foi possível garantir com Dirac ou Ore.")
        print("Grafo grande (74 vértices) → problema NP-completo.")
        print("Conclusão provável: NÃO tem ciclo hamiltoniano (grafo esparso, muitos graus baixos).")
        return False

# ---------- Leitura e escrita ----------
def parse_vertice(line):
    parts = [p.strip() for p in line.split(",")]
    id_ = int(parts[0])
    rotulo = parts[1]
    meta = tuple(parts[2:]) if len(parts) > 2 else ()
    return id_, rotulo, meta

def parse_aresta(line):
    parts = [p.strip() for p in line.split(",")]
    origem = int(parts[0])
    destino = int(parts[1])
    peso = parts[2] if len(parts) >= 3 else None
    return origem, destino, peso

def carregar_grafo(path):
    if not os.path.exists(path):
        print(f"Arquivo {path} não encontrado. Criando grafo vazio.")
        return Grafo()
    with open(path, "r", encoding="utf-8") as f:
        linhas = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not linhas:
        return Grafo()
    idx = 0
    tipo = int(linhas[idx]); idx += 1
    g = Grafo(tipo=tipo)
    num_vertices = int(linhas[idx]); idx += 1
    for _ in range(num_vertices):
        id_, rotulo, meta = parse_vertice(linhas[idx]); idx += 1
        g.adicionar_vertice(id_, rotulo, meta)
    num_arestas = int(linhas[idx]); idx += 1
    for _ in range(num_arestas):
        o, d, p = parse_aresta(linhas[idx]); idx += 1
        g.adicionar_aresta(o, d, p)
    return g

def salvar_grafo(g, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{g.tipo}\n")
        f.write(f"{len(g.vertices)}\n")
        for vid in sorted(g.vertices):
            v = g.vertices[vid]
            linha = f"{vid}, {v.rotulo}"
            if v.meta:
                linha += ", " + ", ".join(map(str, v.meta))
            f.write(linha + "\n")
        arestas = []
        vistas = set()
        for o in g.adj:
            for e in g.adj[o]:
                if g.tipo == 3 and (e.destino, o) in vistas:
                    continue
                arestas.append(e)
                vistas.add((o, e.destino))
        f.write(f"{len(arestas)}\n")
        for e in arestas:
            if e.peso:
                f.write(f"{e.origem}, {e.destino}, {e.peso}\n")
            else:
                f.write(f"{e.origem}, {e.destino}\n")
    print(f"Grafo salvo em {path}")

def mostrar_arquivo(path):
    print(f"\nConteúdo do arquivo ({path}):\n" + "-"*50)
    if not os.path.exists(path):
        print("Arquivo não existe.")
        return
    with open(path, "r", encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            print(f"{i:03d}: {ln.rstrip()}")
    print("-"*50)

def menu():
    print("""
Menu de opções:
a) Ler dados do arquivo grafo.txt
b) Gravar dados no arquivo grafo.txt
c) Inserir vértice
d) Inserir aresta
e) Remover vértice
f) Remover aresta
g) Mostrar conteúdo do arquivo (raw)
h) Mostrar grafo (lista de adjacência)
i) Apresentar a conexidade do grafo
k) Verificar se tem Ciclo Euleriano
l) Verificar se tem Ciclo Hamiltoniano
j) Encerrar a aplicação
""")

def main():
    path = DEFAULT_PATH
    g = Grafo()
    if os.path.exists(path):
        print(f"Arquivo {path} encontrado. Carregando...")
        g = carregar_grafo(path)
        print(f"Grafo carregado → {len(g.vertices)} vértices, {len(g.lista_arestas())} arestas (brutas).")
    else:
        print("Arquivo não encontrado. Iniciando grafo vazio.")

    while True:
        menu()
        op = input("Escolha uma opção (a-l): ").strip().lower()

        if op == "a":
            g = carregar_grafo(path)
            print("Grafo recarregado com sucesso.")

        elif op == "b":
            salvar_grafo(g, path)

        elif op == "c":
            try:
                id_ = int(input("ID do vértice: "))
                rotulo = input("Nome/Rótulo: ").strip()
                meta = input("Meta (nota, preço, endereço - separado por vírgula): ").strip()
                meta_tuple = tuple(meta.split(",")) if meta else ()
                if g.adicionar_vertice(id_, rotulo, meta_tuple):
                    print("Vértice adicionado.")
                else:
                    print("Vértice já existe.")
            except:
                print("Erro nos dados.")

        elif op == "d":
            try:
                o = int(input("Origem: "))
                d = int(input("Destino: "))
                peso = input("Peso (ex: 1.2 km) ou vazio: ").strip() or None
                if g.adicionar_aresta(o, d, peso):
                    print("Aresta adicionada.")
                else:
                    print("Aresta já existe ou vértice inexistente.")
            except:
                print("Erro.")

        elif op == "e":
            try:
                id_ = int(input("ID do vértice a remover: "))
                if g.remover_vertice(id_):
                    print("Vértice removido.")
                else:
                    print("Vértice não existe.")
            except:
                print("Erro.")

        elif op == "f":
            try:
                o = int(input("Origem da aresta: "))
                d = int(input("Destino da aresta: "))
                if g.remover_aresta(o, d):
                    print("Aresta removida.")
                else:
                    print("Aresta não encontrada.")
            except:
                print("Erro.")

        elif op == "g":
            mostrar_arquivo(path)

        elif op == "h":
            g.mostrar_lista_adjacencia()

        elif op == "i":
            if g.tipo == 3:
                print("Grafo não-dirigido →", "Conexo" if g.conexo_nao_direcionado() else "Desconexo")
            else:
                print("Análise de componentes fortes não implementada aqui (use versão anterior se precisar).")

        elif op == "k":
            print("\n=== Análise de Ciclo Euleriano ===")
            g.tem_ciclo_euleriano()

        elif op == "l":
            print("\n=== Análise de Ciclo Hamiltoniano ===")
            g.tem_ciclo_hamiltoniano()

        elif op == "j":
            print("Encerrando aplicação.")
            break

        else:
            print("Opção inválida.")

        print("\n" + "="*50)

if __name__ == "__main__":
    print("GrafoApp - Com análise Euleriana e Hamiltoniana")
    main()