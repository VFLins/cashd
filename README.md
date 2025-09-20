![banner](https://raw.githubusercontent.com/VFLins/cashd/refs/heads/main/cashd-server/src/cashd/assets/gh_banner-cashd.png)

## Sobre

O **Cashd** é um software simples e poderoso para o dono de pequenas lojas que pretendem
aceitar o fiado como forma de pagamento, mas não querem ter que registrar tudo em papel.
O Cahsd permite que você ofereça o fiado sem as dores de cabeça de ter que gastar tempo
procurando por um nome no "caderninho das dívidas", com menos propensão à erros, e
armazenando seus dados virtualmente, onde estarão mais seguros.

Você pode dizer o nome dos seus clientes que estão a mais tempo sem te visitar? Ou
aqueles que possuem os maiores saldos devedores? Com o Cashd você consegue ter acesso à
estas e outras informações rapidamente, que podem te ajudar a tomar as melhores decisões
para não deixar o fiado virar um problema.

## A duas edições de Cashd

O cashd vem em duas edições, que possuem a mesma funcionalidade, mas que são pensadas
para atender casos de uso diferentes:

- O [`cashd-local`](https://github.com/VFLins/cashd/tree/main/cashd-local) é pensado para
o caso em que ele só precisa ser instalado em um dispositivo, o mesmo dispositivo que
recebe a instalação será usado para o controle das dívidas;

- Já o [`cashd-server`](https://github.com/VFLins/cashd/tree/main/cashd-server) também é
capaz de agir como o `cashd-local`, executando apenas localmente em um computador, mas é
indicado para casos em que um computador hospedará o programa, servindo para outros
dispositivos conectados na mesma rede, assim todos os diferentes dispositivos podem ter
acesso ao mesmo banco de dados simultaneamente.

É caso deseje usar o `cashd-server` da maneira indicada, é recomendado que tenha algum
nível de conhecimento em computadores, e seguir as instruções de instalação com cuidado.
Caso não tenha conhecimento procure um profissional técnico de confiança para fazer isso
por você.

> [!WARNING]
> Na versão atual **0.3.1**, a possibilidade de usar o `cashd-server` como serviço ainda
> é meramente planejada, esta funcionalidade deve ser implementada na futura versão
> **0.4.0**.

Para mais informações sobre as diferentes edições do Cashd, clique no link correspondente
acima e acesse a documentação de seu interesse.

