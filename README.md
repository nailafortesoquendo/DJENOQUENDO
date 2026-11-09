# DJEN Oquendo

Monitoramento diário das publicações do Diário de Justiça Eletrônico Nacional (DJEN) para os advogados do escritório, em todos os tribunais.

| Advogado | OAB |
|---|---|
| Mauro Oquendo do Rêgo Monteiro | 5.935/PI |
| Gabriel Ataíde da Silva | 22.891/PI |
| Naila Fortes e Silva | 5.815/PI |

## Como funciona

1. `coletor.py` consulta a API pública do DJEN (`comunicaapi.pje.jus.br`) para cada OAB e grava o acumulado em `site/data/comunicacoes.json` (mantém 120 dias).
2. O coletor roda **no computador do escritório**, de segunda a sexta às 9h, pelo `coletor_local.bat` agendado no Windows. Ele faz commit do JSON e envia ao GitHub. Instruções em [INSTALACAO_WINDOWS.md](INSTALACAO_WINDOWS.md).
3. O workflow `.github/workflows/djen.yml` publica a pasta `site/` no GitHub Pages a cada envio.
4. `site/index.html` é a página pesquisável: mostra a coleta diária e, a pedido, consulta o DJEN ao vivo pelo navegador.

Por que a coleta não roda no GitHub Actions: a API do DJEN responde 403 (CloudFront) para servidores fora do Brasil. Do navegador e de computadores no Brasil ela responde normalmente.

Site: https://nailafortesoquendo.github.io/DJENOQUENDO/

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
