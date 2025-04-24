import threading
import time
import random
from dataclasses import dataclass

@dataclass
class Filosofo:
    id: int
    nome: str
    garfo_esquerdo: int
    garfo_direito: int
    executou: int = 0
    thread: threading.Thread = None

    def pensar(self):
        print(f"{self.nome} pensando.")
        time.sleep(random.uniform(0.5, 1.5))

    def tentar_pegar_garfos(self, semaphor):
        primeiro, segundo = sorted([self.garfo_esquerdo, self.garfo_direito])
        print(f"{self.nome} tenta pegar os garfos {primeiro} e {segundo}.")

        if semaphor[primeiro].acquire(timeout=1):
            print(f"{self.nome} pegou o garfo {primeiro}.")
            if semaphor[segundo].acquire(timeout=1):
                print(f"{self.nome} pegou o garfo {segundo}.")
                return primeiro, segundo
            semaphor[primeiro].release()
        return None, None

    def comer(self):
        print(f"{self.nome} está comendo.")
        time.sleep(random.uniform(0.5, 1))
        self.executou += 1

    def devolver_garfos(self, semaphor, primeiro, segundo):
        semaphor[segundo].release()
        semaphor[primeiro].release()
        print(f"{self.nome} devolveu os garfos {primeiro} e {segundo}.")

def rotina_filosofo(filosofo: Filosofo, semaphor, parar_evento: threading.Event):
    while not parar_evento.is_set(): # só pra não ficar rodando o programa infinitamente
        filosofo.pensar()# o processo está ativo no momento aguardando semaphor

        # tenta fazer a ação de pegar os garfos
        primeiro, segundo = filosofo.tentar_pegar_garfos(semaphor)

        #se o filosofo consegui pegar o primeiro e o segundo ele tenta comer e depois devolve o garfo
        if primeiro is not None and segundo is not None:
            try:
                filosofo.comer()
            finally:
                filosofo.devolver_garfos(semaphor, primeiro, segundo)

def main():
    num_filosofos = int(input("Digite o número de filósofos: "))
    tempo_execucao = int(input("Digite o tempo de execução (segundos): "))

    # gerar semaforos
    semaphor = [threading.Semaphore(1) for _ in range(num_filosofos)]
    
    #criar filosofos
    filosofos = [
        Filosofo(i, f"Filósofo {i}", i, (i + 1) % num_filosofos)
        for i in range(num_filosofos)
    ]
    parar_evento = threading.Event()

    for f in filosofos:
        f.thread = threading.Thread(target=rotina_filosofo, args=(f, semaphor, parar_evento))
        f.thread.start()

    time.sleep(tempo_execucao)
    parar_evento.set()

    for f in filosofos:
        f.thread.join()

    print("\n=== Resultado ===")
    for f in filosofos:
        print(f"{f.nome} executou {f.executou} vezes.")

if __name__ == "__main__":
    main()
