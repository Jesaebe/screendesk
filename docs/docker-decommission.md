# Desativação do ambiente Docker anterior

Estado: **concluída pelo usuário em 10/10/2026**.

Validação posterior:

- zero containers, imagens, volumes locais e cache de build;
- somente redes padrão `bridge`, `host` e `none`;
- raiz com 10% de uso e 84 GB disponíveis;
- `/srv/backups` com 1% de uso e 93 GB disponíveis;
- Docker, Nginx e Zabbix Agent 2 ativos;
- portas 22, 80 e 10050 preservadas e porta 8123 livre.

## Preservar obrigatoriamente

- Docker Engine e Docker Compose.
- Nginx do host e sua porta 80.
- Zabbix Agent 2 e sua porta 10050.
- SSH e configurações do Ubuntu.
- LVM, volume raiz e `/srv/backups`.
- Artefatos do ScreenDeck neste repositório.

## Recursos Docker identificados para remoção

Containers:

- `rifa-da-iris`;
- `cartorio-frontend-1`;
- `cartorio-backend-1`;
- `cartorio-db-1`;
- `hml_fejjb-backend-1`;
- `hml_fejjb-db-1`;
- `hml_fejjb-frontend-1`;
- `hml_fejjb-redis-1`;
- `gracious_hofstadter`.

Redes de projeto:

- `rifa_default`;
- `cartorio_default`;
- `hml_fejjb_default`.

Volumes nomeados com decisão de descarte:

- `cartorio_backend_uploads`;
- `sistema_db_test_data`;
- `hml_fejjb_postgres_data`;
- `prd_fejjb_media_volume`;
- `prd_fejjb_postgres_data`;
- `prd_fejjb_static_volume`;
- `jiu_jitsu_system_media_volume`;
- `jiu_jitsu_system_postgres_data`;
- `jiu_jitsu_system_static_volume`.

Também foi autorizada a limpeza do cache de build, estimado em 55,04 GB recuperáveis.

## Recursos cuja remoção foi confirmada e executada

- Remover as 18 imagens Docker, inclusive imagens sem container atual.
- Remover os 12 volumes anônimos identificados.
- Excluir ou preservar os diretórios:
  - `/home/cyrius/sistemas/jhonatas/rifa`;
  - `/home/cyrius/sistemas/fejjb/hml`;
  - `/home/cyrius/sistemas/cartorio`.

## Sequência segura utilizada

1. repetir inventário imediatamente antes da remoção e comparar IDs/nome/estado;
2. interromper somente os containers listados;
3. remover containers;
4. remover apenas volumes e redes explicitamente confirmados;
5. remover imagens confirmadas;
6. limpar cache de build;
7. tratar diretórios bind/source conforme decisão separada;
8. verificar portas, Docker, Nginx, Zabbix e ocupação da raiz;
9. registrar espaço recuperado e recursos restantes.

Não usar limpeza global sem antes resolver a confirmação dos volumes anônimos e das imagens.
