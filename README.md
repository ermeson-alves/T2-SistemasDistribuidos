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

Falar das libs aqui.



## Comunicação
- RabbitMQ (Sensores)
    - AMQP (Advanced Queuing Protocol)
    - O corpo da mensagem que é enviada para o servidor RabbitMQ, publicado na fila correspondente, tem seu corpo formatadado em string. Esse corpo é extraído ao consumir da fila, dentro do gateway, onde o conteúdo de interesse é reformatado de acordo. 
- gRPC (Atuadores)
- Socket TCP (Home Assistant - Client)
