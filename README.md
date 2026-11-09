# DJEN Oquendo

Monitoramento diário das publicações do Diário de Justiça Eletrônico Nacional (DJEN) para os advogados do escritório, em todos os tribunais.

| Advogado | OAB |
|---|---|
| Mauro Oquendo do Rêgo Monteiro | 5.935/PI |
| Gabriel Ataíde da Silva | 22.891/PI |
| Naila Fortes e Silva | 5.815/PI |

## Estado atual

- **Consulta ao vivo pelo navegador: funciona.** A página chama a API do DJEN diretamente e mostra as publicações do período escolhido.
- **Coleta automática pelo GitHub Actions: bloqueada pelo DJEN.** A API responde 403 (CloudFront, "The request could not be satisfied") para os servidores do GitHub, que ficam fora do Brasil. O workflow continua publicando o site, mas o histórico em `site/data/` fica vazio. Para acumular histórico, rode `coletor.py` em um computador no Brasil e faça commit do JSON.

## Como funciona

1. `coletor.py` consulta a API pública do DJEN (`comunicaapi.pje.jus.br`) para cada OAB e grava o acumulado em `site/data/comunicacoes.json` (mantém 120 dias).
2. O workflow `.github/workflows/djen.yml` roda o coletor nos dias úteis às 9h40 de Brasília, faz commit do JSON e publica a pasta `site/` no GitHub Pages.
3. `site/index.html` é a página pesquisável: lê a coleta diária e, se você pedir, consulta o DJEN ao vivo para qualquer período.

## Ativar o GitHub Pages (uma vez)

1. No repositório, abra **Settings → Pages**.
2. Em **Build and deployment → Source**, escolha **GitHub Actions**. Salve.
3. Vá em **Actions → Radar DJEN → Run workflow**, informe `30` em "dias" e execute. A primeira rodada preenche o histórico e publica o site.

Endereço do site depois da primeira publicação: `https://nailafortesoquendo.github.io/djenoquendo/`


## Rodar localmente

```bash
python coletor.py --dias 7
python -m http.server -d site 8000   # abra http://localhost:8000
```

## Alterar advogados

Edite a lista `ADVOGADOS` em `coletor.py`. A página lê a lista a partir do JSON gerado; as cores dos três primeiros estão em `CORES` no `index.html`.

## Limites

- A API do DJEN é pública e limita requisições por IP; o coletor pausa um segundo entre chamadas.
- A página é publicada na internet (o DJEN já é público). Para restringir, mantenha o repositório privado e use Pages com visibilidade restrita (recurso de planos pagos do GitHub).
- A consulta não substitui a intimação eletrônica nem o controle de prazos pelo Domicílio Judicial Eletrônico.
