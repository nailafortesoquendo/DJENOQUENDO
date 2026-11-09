# Instalar o coletor no computador do escritório (Windows)

O coletor roda de segunda a sexta às 9h, consulta o DJEN para as três OABs, grava o resultado e envia ao GitHub. O envio atualiza o site automaticamente. Precisa de um computador ligado e conectado à internet no horário; se estiver desligado, a próxima execução cobre os últimos 3 dias.

Tempo estimado: 15 minutos, uma única vez.

## 1. Instalar o Python

1. Abra https://www.python.org/downloads/windows/ e baixe a versão mais recente do **Python 3** (instalador de 64 bits).
2. Na primeira tela do instalador, marque **Add python.exe to PATH** e clique em **Install Now**.

## 2. Instalar o Git

1. Abra https://git-scm.com/download/win e baixe o instalador de 64 bits.
2. Avance com as opções padrão até o fim. O **Git Credential Manager** vem incluído e cuida do login no GitHub.

## 3. Baixar o repositório

1. Abra o menu Iniciar, digite `cmd` e abra o **Prompt de Comando**.
2. Cole os comandos abaixo, um por vez, e pressione Enter:

```bat
cd %USERPROFILE%\Documents
git clone https://github.com/nailafortesoquendo/DJENOQUENDO.git
cd DJENOQUENDO
```

A pasta `Documentos\DJENOQUENDO` passa a conter o coletor.

## 4. Fazer login no GitHub (uma vez)

Ainda no Prompt de Comando, dentro da pasta `DJENOQUENDO`, rode uma coleta de teste que já tenta enviar o resultado:

```bat
coletor_local.bat --dias 30
```

Na primeira vez, o Git abre o navegador pedindo login no GitHub. Entre com a conta `nailafortesoquendo` e autorize. O login fica salvo no Windows e não é pedido de novo.

Para conferir o que aconteceu, abra o arquivo `coletor.log` na mesma pasta. Deve terminar com `Enviado ao GitHub.` ou `Sem novidades para enviar.`. Um ou dois minutos depois, o site em https://nailafortesoquendo.github.io/DJENOQUENDO/ passa a mostrar os últimos 30 dias na coleta diária.

## 5. Agendar a execução diária

1. Na pasta `DJENOQUENDO`, clique duas vezes em **instalar_tarefa.bat**. Se o Windows recusar, clique com o botão direito e escolha **Executar como administrador**.
2. A janela confirma: `Tarefa "Radar DJEN" criada: segunda a sexta, 09:00.`

Pronto. A tarefa aparece no **Agendador de Tarefas** do Windows com o nome **Radar DJEN**. Lá dá para mudar o horário em **Propriedades → Disparadores**.

A tarefa roda enquanto o usuário estiver conectado ao Windows, mesmo com a tela bloqueada. Para rodar com o usuário desconectado, abra a tarefa no Agendador, aba **Geral**, e marque **Executar estando o usuário conectado ou não**; o Windows pedirá a senha do usuário.

## Verificar se está funcionando

- `coletor.log` na pasta: uma seção por execução, com a quantidade por advogado.
- https://github.com/nailafortesoquendo/DJENOQUENDO/commits : um commit "DJEN: coleta local de ..." por dia com novidade.
- No site, a linha de status mostra "Coleta diária de <data e hora>".

## Problemas comuns

| Sintoma no `coletor.log` | Causa provável | O que fazer |
|---|---|---|
| `'py' não é reconhecido` ou `'python' não é reconhecido` | Python instalado sem a opção **Add to PATH** | Reinstale o Python marcando a opção, ou repare a instalação |
| `'git' não é reconhecido` | Git não instalado ou Prompt aberto antes da instalação | Instale o Git e abra um novo Prompt |
| `HTTP 403 Forbidden` | O DJEN recusou o acesso deste computador ou rede | Teste abrir https://comunica.pje.jus.br no navegador. Se abrir, aguarde e rode de novo; se persistir, me avise |
| `ERRO: nao foi possivel enviar ao GitHub` | Login não feito ou sem permissão no repositório | Rode `coletor_local.bat` no Prompt para o navegador pedir o login |
| `Sem novidades para enviar.` todo dia | Nenhuma publicação nova, ou o período pedido já estava coletado | Normal em dias sem intimação. Confira no site com "Consultar DJEN ao vivo" |

## Rodar manualmente

Na pasta, clique duas vezes em `coletor_local.bat` para coletar os últimos 3 dias. Para um período específico, no Prompt de Comando:

```bat
coletor_local.bat 2026-10-01 2026-10-31
```
