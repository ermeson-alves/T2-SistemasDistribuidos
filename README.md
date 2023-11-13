# T2-SisDistribuitos
Repositório base para o segundo trabalho da cadeira de TI0151- Sistemas Distribuídos (2023.2 - T01), da Universidade Federal do Ceará. 


## Grupo
Antonio Ermeson Pereira Alves - 511473<br>
Renan Ribeiro De Oliveira - 471870<br>
Carlos Victor Gonçalves Moura - 515016<br>

## Setup
Linguagem escolhida: Python (versão 3.10.12)
```code
pip install -r requirements.txt
```
#### Inicialização do RabbitMQ
```code
sudo docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
```


#### O uso do repositório envolve rodar cada arquivo .py em processos isolados:

1. Conjunto de funções que atendem as especificações para o *Home assistant*:
```code
python gateway.py
```
2. Gera uma aplicação de Menus com uso da lib simple-term-menu, do python (lado do Cliente):
```code
python clientDesktop.py
```
3. Funções para o sensor de fumaça e para o Controlador de Incêndio:
```code
python smokealarm.py
```
4. Funções para lâmpada e sensor de luminosidade:
```code
python lamp.py
```
5. Funções para o sensor de temperatura e ar condicionado:
```code
python airconditioner.py
```

- A lib protobuf é utilizada para implementação do formato de mensagem Protocol Buffers, onde o arquivo .proto é compilado para um arquivo python contendo os formatos de mensagem.

- A lib pika é iimportada para implementar a interação com o servidor RabbitMQ, servindo como um cliante do message broker do RabbitMQ. Provê um MiddleWare para desenvolvedores que lida com conecção, abstração de cnáis e métodos de publicação e consumo.

- A lib grpcio é utilizada para implementação do framework gRPC para as chamadas remotas de processo. Com ela é possível obter um segundo arquivo python resultante da compilação do arquivo proto, contendo as classes para chamada remota.

#### Aplicação cliente:
Existe um Menu principal em que os sub-menus, com opções dos Atuadores e Sensores, são disponíveis.

 

## Comunicação
- RabbitMQ (Sensores)
- gRPC (Atuadores)
- Socket TCP (Home Assistant - Client)

## gRPC
  O gRPC é um framework open source de Remote Procedure Call (RPC). Ele foi usado localmente para o gateway (home assistant) fazer chamadas de processo nos atuadores. As mensagens das chamadas de processo são estruturadas por Protocol Buffers, onde a chamada de processo para um atuador envia um booleano indicando se o atuador deve ser ligado ou desligado e (no caso do ar condicionado) também envia a temperatura do ar condicionado, para que o sensor consiga simular corretamente a mudança que o ar condicionado causa no ambiente. Além disso, é enviada uma resposta da chamada ao gateway contendo uma string, descrevendo a alção que foi tomada pelo atuador.

## RabbitMQ
  O RabbitMQ usa o protocolo AMQP (Advanced Message Queuing Protocol) tanto para publicar quanto para consumir mensagens das filas.
  Os sensores simulam um ambiente com as medições propostas no trablaho, essas medições, após geradas, são empacotadas em um corpo de uma mensagem e publicadas pelo RabbitMQ, o qual compõe o MiddleWare entre os Sensores e o Home Assistant. O corpo da mensagem que é enviada para o servidor RabbitMQ, publicado na fila correspondente, tem seu corpo formatadado em string. Esse corpo é extraído ao consumir da fila, dentro do Home Assistant, onde o conteúdo de interesse é reformatado de acordo. Por diante, o Home Assistant consome as mensagens da fila corespondente e chama, ao o fazer, a CallBackFunction que processa os dados recebidos, direcionando o fluxo do código de acordo. 

## Socket TCP
  As mensagens trocadas são strings codificadas em UTF-8. Como cada opção do menu acompanha um index, o Home Assistant faz um tratamento especial para tipo de mensagem do cliente. O Home Assistant possui uma thread para consumo dos dados dos sensores e chamadas remotas para os atuadores e outra thread para um servidor TCP que deve se comunicar com o cliente. Variaveis globais sao utilizadas para tornar viavel a interação entre os métodos de ambas as threads.
  
