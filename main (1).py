#!/usr/bin/env python3
"""
Aplicação de manipulação de grafo com menu (somente usa 'grafo.txt').
"""

from typing import Dict, List, Tuple, Optional
import os

# --------- Caminho fixo ---------
DEFAULT_PATH = "grafo.txt"   # só permite esse arquivo

# ---------- Classes ----------
class Vertice:
    def __init__(self, id_: int, rotulo: str, meta: Optional[Tuple]=None):
        self.id = id_
        self.rotulo = rotulo
        self.meta = meta  # info extra (nota, categoria, endereço)

    def __str__(self):
        meta_str = ""
        if self.meta:
            meta_str = ", ".join(map(str, self.meta))
            return f"{self.id}: {self.rotulo} ({meta_str})"
        return f"{self.id}: {self.rotulo}"


class Aresta:
    def __init__(self, origem: int, destino: int, peso: Optional[str]=None):
        self.origem = origem
        self.destino = destino
        self.peso = peso

    def __str__(self):
        return f"{self.origem} -> {self.destino}" + (f" [{self.peso}]" if self.peso else "")


class Grafo:
    def __init__(self, tipo: int = 0):
        self.tipo = tipo
        self.vertices: Dict[int, Vertice] = {}
        self.adj: Dict[int, List[Aresta]] = {}

    # vértices
    def adicionar_vertice(self, id_: int, rotulo: str, meta: Optional[Tuple]=None) -> bool:
        if id_ in self.vertices:
            return False
        v = Vertice(id_, rotulo, meta)
        self.vertices[id_] = v
        self.adj.setdefault(id_, [])
        return True

    def remover_vertice(self, id_: int) -> bool:
        if id_ not in self.vertices:
            return False
        del self.vertices[id_]
        if id_ in self.adj:
            del self.adj[id_]
        for src, lst in list(self.adj.items()):
            self.adj[src] = [e for e in lst if e.destino != id_]
        return True

    # arestas
    def adicionar_aresta(self, origem: int, destino: int, peso: Optional[str]=None) -> bool:
        if origem not in self.vertices or destino not in self.vertices:
            return False
        for e in self.adj.get(origem, []):
            if e.destino == destino and e.peso == peso:
                return False
        self.adj.setdefault(origem, []).append(Aresta(origem, destino, peso))
        return True

    def remover_aresta(self, origem: int, destino: int) -> bool:
        if origem not in self.adj:
            return False
        original_len = len(self.adj[origem])
        self.adj[origem] = [e for e in self.adj[origem] if e.destino != destino]
        return len(self.adj[origem]) < original_len

    def lista_arestas(self) -> List[Aresta]:
        todas = []
        for src in self.adj:
            todas.extend(self.adj[src])
        return todas

    def mostrar_lista_adjacencia(self):
        print("Lista de adjacência:")
        for vid in sorted(self.vertices.keys()):
            v = self.vertices[vid]
            l = self.adj.get(vid, [])
            edges = ", ".join([f"{e.destino}({e.peso})" if e.peso else str(e.destino) for e in l])
            print(f" {vid} - {v.rotulo} -> [{edges}]")

    # conexidade para não direcionado
    def conexo_nao_direcionado(self) -> bool:
        if not self.vertices:
            return True
        inicio = next(iter(self.vertices))
        visitados = set()
        pilha = [inicio]
        while pilha:
            u = pilha.pop()
            if u in visitados:
                continue
            visitados.add(u)
            for e in self.adj.get(u, []):
                if e.destino not in visitados:
                    pilha.append(e.destino)
            for src, lst in self.adj.items():
                for e in lst:
                    if e.destino == u and src not in visitados:
                        pilha.append(src)
        return len(visitados) == len(self.vertices)

    # Componentes Fortemente Conexas (Kosaraju)
    def componentes_fortemente_conexas(self) -> List[List[int]]:
        visitados = set()
        ordem = []

        def dfs1(u):
            visitados.add(u)
            for e in self.adj.get(u, []):
                if e.destino not in visitados:
                    dfs1(e.destino)
            ordem.append(u)

        for v in self.vertices:
            if v not in visitados:
                dfs1(v)

        transposto = {v: [] for v in self.vertices}
        for src in self.adj:
            for e in self.adj[src]:
                transposto[e.destino].append(src)

        visitados.clear()
        componentes = []

        def dfs2(u, comp):
            visitados.add(u)
            comp.append(u)
            for w in transposto.get(u, []):
                if w not in visitados:
                    dfs2(w, comp)

        while ordem:
            v = ordem.pop()
            if v not in visitados:
                comp = []
                dfs2(v, comp)
                componentes.append(comp)
        return componentes

    def grafo_reduzido(self):
        comps = self.componentes_fortemente_conexas()
        comp_de = {}
        for idx, comp in enumerate(comps):
            for v in comp:
                comp_de[v] = idx
        reduzido = {}
        for u in self.adj:
            for e in self.adj[u]:
                cu = comp_de[u]
                cv = comp_de[e.destino]
                if cu != cv:
                    reduzido.setdefault(cu, set()).add(cv)
        return comps, reduzido

    def categoria_direcionado(self) -> str:
        if not self.vertices:
            return "C0"
        arestas = self.lista_arestas()
        if not arestas:
            return "C0"
        comps = self.componentes_fortemente_conexas()
        if len(comps) == 1 and len(comps[0]) == len(self.vertices):
            return "C3"
        unitarios = [c for c in comps if len(c) == 1]
        if unitarios and len(comps) > 1:
            return "C1"
        return "C2"


# ---------- Leitura e escrita ----------
def parse_vertice(line: str) -> Tuple[int, str, Tuple]:
    parts = [p.strip() for p in line.split(",")]
    id_ = int(parts[0])
    rotulo = parts[1] if len(parts) > 1 else f"V{id_}"
    meta = tuple(parts[2:]) if len(parts) > 2 else ()
    return id_, rotulo, meta


def parse_aresta(line: str) -> Tuple[int, int, Optional[str]]:
    parts = [p.strip() for p in line.split(",")]
    origem = int(parts[0])
    destino = int(parts[1])
    peso = parts[2] if len(parts) >= 3 else None
    return origem, destino, peso


def carregar_grafo(path: str) -> Grafo:
    if not os.path.exists(path):
        print(f"Atenção: arquivo {path} não encontrado. Criando grafo vazio.")
        return Grafo()
    with open(path, "r", encoding="utf-8") as f:
        linhas = [ln.rstrip("\n") for ln in f if ln.strip() != ""]
    idx = 0
    tipo = int(linhas[idx]); idx += 1
    g = Grafo(tipo=tipo)
    num_vertices = int(linhas[idx]); idx += 1
    for _ in range(num_vertices):
        id_, rotulo, meta = parse_vertice(linhas[idx]); idx += 1
        g.adicionar_vertice(id_, rotulo, meta)
    num_arestas = int(linhas[idx]); idx += 1
    for _ in range(num_arestas):
        origem, destino, peso = parse_aresta(linhas[idx]); idx += 1
        if origem not in g.vertices:
            g.adicionar_vertice(origem, f"V{origem}")
        if destino not in g.vertices:
            g.adicionar_vertice(destino, f"V{destino}")
        g.adicionar_aresta(origem, destino, peso)
    return g


def salvar_grafo(g: Grafo, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{g.tipo}\n")
        f.write(f"{len(g.vertices)}\n")
        for vid in sorted(g.vertices.keys()):
            v = g.vertices[vid]
            meta_part = ", ".join(map(str, v.meta)) if v.meta else ""
            linha = f"{v.id}, {v.rotulo}"
            if meta_part:
                linha += f", {meta_part}"
            f.write(linha + "\n")
        arestas = g.lista_arestas()
        f.write(f"{len(arestas)}\n")
        for e in arestas:
            if e.peso:
                f.write(f"{e.origem}, {e.destino}, {e.peso}\n")
            else:
                f.write(f"{e.origem}, {e.destino}\n")
    print(f"Grafo salvo em {path}")


def mostrar_arquivo(path: str):
    print(f"\nConteúdo do arquivo ({path}):\n" + "-"*40)
    if not os.path.exists(path):
        print("Arquivo não existe.")
        return
    with open(path, "r", encoding="utf-8") as f:
        for i, ln in enumerate(f, start=1):
            print(f"{i:03d}: {ln.rstrip()}")
    print("-"*40)


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
i) Apresentar a conexidade do grafo e o grafo reduzido (se direcionado)
j) Encerrar a aplicação
""")


def main():
    path = DEFAULT_PATH
    g = Grafo()
    if os.path.exists(path):
        print(f"Atenção: detectado arquivo {path}.")
        g = carregar_grafo(path)
        print(f"Grafo carregado (tipo={g.tipo}). Vértices: {len(g.vertices)}. Arestas: {len(g.lista_arestas())}.")
    else:
        print("Arquivo grafo.txt não encontrado. Criando grafo vazio.")

    while True:
        menu()
        op = input("Escolha uma opção (a-j): ").strip().lower()
        if op == "a":
            g = carregar_grafo(path)
            print(f"Grafo carregado. Vértices: {len(g.vertices)}. Arestas: {len(g.lista_arestas())}.")
        elif op == "b":
            salvar_grafo(g, path)
        elif op == "c":
            try:
                id_ = int(input("ID do vértice (int): ").strip())
            except ValueError:
                print("ID inválido.")
                continue
            rotulo = input("Rótulo/nome: ").strip()
            meta_raw = input("Meta (separar por vírgula, ou vazio): ").strip()
            meta = tuple([m.strip() for m in meta_raw.split(",")]) if meta_raw else ()
            ok = g.adicionar_vertice(id_, rotulo, meta)
            print("Vértice adicionado." if ok else "Vértice já existe.")
        elif op == "d":
            try:
                origem = int(input("Origem (ID): ").strip())
                destino = int(input("Destino (ID): ").strip())
            except ValueError:
                print("IDs inválidos.")
                continue
            peso = input("Peso (ex: '1.2 km') ou vazio: ").strip() or None
            if origem not in g.vertices or destino not in g.vertices:
                print("Um dos vértices não existe.")
                continue
            ok = g.adicionar_aresta(origem, destino, peso)
            print("Aresta adicionada." if ok else "Aresta já existe.")
        elif op == "e":
            try:
                vid = int(input("ID do vértice a remover: ").strip())
            except ValueError:
                print("ID inválido.")
                continue
            if vid not in g.vertices:
                print("Vértice não existe.")
                continue
            g.remover_vertice(vid)
            print("Vértice removido (e arestas incidentes também).")
        elif op == "f":
            try:
                origem = int(input("Origem da aresta a remover: ").strip())
                destino = int(input("Destino da aresta a remover: ").strip())
            except ValueError:
                print("IDs inválidos.")
                continue
            ok = g.remover_aresta(origem, destino)
            print("Aresta removida." if ok else "Aresta não encontrada.")
        elif op == "g":
            mostrar_arquivo(path)
        elif op == "h":
            g.mostrar_lista_adjacencia()
        elif op == "i":
            eh_dirigido = input("O grafo atual é dirigido? (s/n): ").strip().lower() == "s"
            if not eh_dirigido:
                conectado = g.conexo_nao_direcionado()
                print("Grafo não-direcionado => " + ("Conexo" if conectado else "Desconexo"))
            else:
                comps = g.componentes_fortemente_conexas()
                print(f"Grafo direcionado. Número de Componentes Fortemente Conexas: {len(comps)}")
                for i, comp in enumerate(comps):
                    print(f"  Componente {i}: {sorted(comp)}")
                cat = g.categoria_direcionado()
                print(f"Categoria: {cat}")
                comps, reduzido = g.grafo_reduzido()
                print("\nGrafo reduzido:")
                for k in sorted(reduzido.keys()):
                    dests = ", ".join(map(str, sorted(reduzido[k])))
                    print(f"  Comp{k} -> [{dests}]")
        elif op == "j":
            print("Encerrando aplicação.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    print("Iniciando GrafoApp. Usando sempre o arquivo 'grafo.txt'")
    main()
