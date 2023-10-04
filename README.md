<img align="right" alt="Bandeira de Brasília" width="30%" height="auto" src="https://old.gabrf.com/imgs/bsbdf.jpg">

# [BsbDF](https://t.me/BsbDF)

## Scripts

Este repositório reúne os scripts usados no canal [@BsbDF](https://t.me/BsbDF) no Telegram. O foco do canal é reunir informações e notícias sobre a capital federal. 

### base.py

Funções de base para outros scripts, como adicionar link ao histórico de enviados e verificar no histórico se um link já foi enviado ao canal.

### aeroportobsb.py

Notícias do [Aeroporto de Brasília](https://www.bsb.aero/passageiros/noticias) formatadas para funcionar em modo Leitura Rápida.

### agenciabrasilia.py

Este arquivo não é executado em uma ação do GitHub por falhar demais quando o servidor fica fora do Brasil. Roda localmente buscando novas notícias do site da [Agência Brasília](https://www.agenciabrasilia.df.gov.br/noticias/).

### caesb.py

Crawler das [notícias da CAESB](https://caesb.df.gov.br/noticias). Funciona testando se o inteiro identificador da notícia é válido. Sendo, abre a notícia e cria a postagem.

### cbmdf.py

Script que verifica as notícias postadas pela página do [Corpo de Bombeiros](https://cbm.df.gov.br/noticias). 

### inmet.py

Verifica se os alertas do INMET disponibilizados via API dizem respeito ao Distrito Federal. Caso positivo, abre o alerta e formata a informação.

### neoenergia.py

Monitora as [notícias da Neoenergia Brasília](https://www.neoenergia.com/web/brasilia/noticias) e repassa-as no canal.

### Alertas de Trânsito

Verifique o repositório [TrafficStatus2Telegram](https://github.com/GabrielRF/TrafficStatus2Telegram).
