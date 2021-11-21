from time import sleep


class Casa:

    def __init__(self):
        self.comodos = ['Quarto casal', 'Quarto solteiro', 'Sala', 'Cozinha', 'Banheiro']
        self._convidados = []

    def __enter__(self):
        print(f'Bem vindo! A casa é sua!\n\n')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Até mais!\n')

    def convidados(self):
        def controle_de_acesso():
            while True:
                novo_convidado = yield self._convidados
                self._convidados.append(novo_convidado)

        corrotina = controle_de_acesso()
        next(corrotina)
        return corrotina


if __name__ == '__main__':
    with Casa() as casa:
        print('Você tem acesso aos cômodos:')
        print(*casa.comodos)

        sleep(5)

        for pessoa in casa.convidados():
            print(pessoa)


    print('Não vejo a hora de voltar :D')
