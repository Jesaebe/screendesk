# Inventário do servidor — somente leitura

Não executar sem autorização específica. Nenhum comando deste levantamento deve alterar o host.

Servidor informado: `192.168.25.249`.

## Itens a registrar

- versão do Ubuntu, kernel e arquitetura;
- Docker e Compose existentes, sem instalação;
- containers, redes e volumes existentes;
- ocupação do disco raiz, `/srv/backups` e grupo LVM;
- portas TCP em uso, especialmente 80, 443 e 8123;
- memória, swap, carga e CPUs;
- DNS e conectividade de saída necessários;
- UID/GID operacional e permissões atuais de `/srv/backups`;
- serviços que não podem ser interrompidos.

## Containers existentes

O usuário informou que há aplicações Docker em execução e pretende removê-las. A remoção não está autorizada nesta etapa. Antes de qualquer ação destrutiva, registrar para cada recurso:

- nome e ID do container;
- imagem e versão;
- estado e política de reinício;
- portas publicadas;
- bind mounts e volumes nomeados;
- redes;
- dependências entre serviços;
- localização, tamanho e necessidade de preservação dos dados;
- Compose/project labels e diretório de origem, quando identificável;
- procedimento de backup ou exportação anterior à remoção.

A autorização futura deverá citar a lista exata de containers, volumes, redes e diretórios que poderão ser removidos. Volumes e dados não serão inferidos como descartáveis apenas porque o container será removido.

O script `scripts/inventory-server.sh` contém somente comandos de consulta, mas deve ser revisado antes de uso e não será enviado ou executado sem autorização.

## Resultado do inventário — 09/10/2026

Levantamento realizado por SSH com comandos somente leitura. A sessão foi encerrada sem alterações.

### Host

- Ubuntu 24.04.4 LTS, kernel `6.8.0-138-generic`, arquitetura amd64.
- 4 CPUs lógicas.
- Memória: 7,7 GiB; aproximadamente 6,9 GiB disponíveis durante a coleta.
- Swap: 4 GiB, sem uso durante a coleta.
- Docker Engine 29.4.0, storage driver `overlayfs`, logging `json-file`.
- Docker Compose v5.1.3.
- Docker root: `/var/lib/docker`.
- LVM: 20,52 GiB ainda livres no volume group.
- Raiz: 98 GiB, 78 GiB usados, 16 GiB disponíveis, **84% de uso**.
- `/srv/backups`: 98 GiB, 93 GiB disponíveis, 1% de uso.
- `/srv/backups`: proprietário `root:root`, modo `0755`; o usuário não-root planejado para o container ainda não terá escrita.
- Porta 8123: livre durante o levantamento.

### Serviços fora do Docker

- Nginx escuta na porta 80.
- Zabbix Agent 2 escuta na porta 10050.
- SSH escuta na porta 22.
- Esses serviços não fazem parte da autorização futura de remoção de aplicações Docker.

### Containers ativos

| Container | Projeto | Imagem | Porta | Persistência | Reinício |
|---|---|---|---|---|---|
| `rifa-da-iris` | `rifa` | `rifa-rifa-iris` | 5000 | bind `/home/cyrius/sistemas/jhonatas/rifa/data` → `/app/data` | unless-stopped |
| `cartorio-frontend-1` | `cartorio` | `cartorio-frontend` | 8080 | sem mount | unless-stopped |
| `cartorio-backend-1` | `cartorio` | `cartorio-backend` | 8000 | volume `cartorio_backend_uploads` → `/app/uploads` | unless-stopped |
| `cartorio-db-1` | `cartorio` | `postgres:11` | 5433→5432 | volume `sistema_db_test_data` → `/var/lib/postgresql/data` | unless-stopped |

Diretórios Compose:

- Rifa: `/home/cyrius/sistemas/jhonatas/rifa`, aproximadamente 11 MiB.
- Cartório: `/home/cyrius/sistemas/cartorio`, aproximadamente 2,6 MiB.

### Containers parados

| Container | Projeto | Imagem | Persistência |
|---|---|---|---|
| `hml_fejjb-backend-1` | `hml_fejjb` | `hml_fejjb-backend` | bind do diretório `backend` |
| `hml_fejjb-db-1` | `hml_fejjb` | `postgres:15` | `hml_fejjb_postgres_data` |
| `hml_fejjb-frontend-1` | `hml_fejjb` | `hml_fejjb-frontend` | bind `frontend` e volume anônimo de `node_modules` |
| `hml_fejjb-redis-1` | `hml_fejjb` | `redis:alpine` | nenhum mount listado |
| `gracious_hofstadter` | sem projeto | `hello-world` | nenhum mount |

Diretório Compose HML: `/home/cyrius/sistemas/fejjb/hml`, aproximadamente 42 MiB.

### Armazenamento Docker

- Imagens: 18, total 61,04 GB; estimativa recuperável 5,934 GB.
- Containers: 9, total gravável aproximado 23,99 MB.
- Volumes: 21, total 4,495 GB; estimativa recuperável 2,013 GB.
- Cache de build: 578 entradas, total 60,13 GB; estimativa recuperável **55,04 GB**.
- Volume `sistema_db_test_data`: aproximadamente 2,202 GB e ligado ao PostgreSQL ativo do Cartório.
- Volume `hml_fejjb_postgres_data`: aproximadamente 49,9 MB e ligado ao container HML parado.
- Volume anônimo do frontend HML: aproximadamente 230,5 MB e ligado ao container parado.
- Há volumes sem containers ativos associados aos projetos antigos `prd_fejjb` e `jiu_jitsu_system`, além de volumes anônimos. Eles não devem ser considerados descartáveis sem confirmação individual.

### Portas observadas

- 22: SSH.
- 80: Nginx do host.
- 5000: Rifa.
- 8000 e 8080: Cartório.
- 5433: PostgreSQL 11 do Cartório.
- 10050: Zabbix Agent 2.
- 8123: disponível.

### Inconsistências e riscos

- A raiz está a 84%, imediatamente abaixo do limite inicial de 85% proposto para alerta.
- O cache de build é o principal candidato de espaço recuperável, mas nenhuma limpeza foi autorizada.
- Maker foi confirmado como banco externo em outro servidor. Ele não corresponde ao PostgreSQL 11 do Cartório publicado na porta 5433 deste host.
- O volume `/srv/backups` precisa de estratégia de proprietário/ACL antes que o container não-root possa gravar.

## Resultado da desativação — 10/10/2026

O usuário executou a desativação conforme o plano aprovado. A validação posterior registrou zero containers, imagens, volumes locais e cache de build. Permaneceram apenas as redes padrão `bridge`, `host` e `none`.

- raiz: 10% de uso e 84 GB disponíveis;
- `/srv/backups`: 1% de uso e 93 GB disponíveis;
- Docker, Nginx e Zabbix Agent 2 ativos;
- portas 22, 80 e 10050 preservadas;
- porta 8123 livre.

O próximo ajuste de infraestrutura será planejar a escrita do UID 10001 do container de backup em `/srv/backups`, sem ampliar permissões para outros usuários.

## Decisão destrutiva encerrada

Não executar ainda. A confirmação deverá separar, no mínimo:

1. remoção dos quatro containers ativos e eventual parada de serviço;
2. remoção dos quatro containers HML parados e do `hello-world`;
3. preservação, exportação ou exclusão de cada volume de banco/upload;
4. preservação ou exclusão dos diretórios Compose e bind mounts;
5. limpeza do cache de build;
6. remoção de imagens sem containers;
7. preservação obrigatória de Nginx e Zabbix, salvo autorização separada.

## Decisões recebidas e executadas pelo usuário

- Não é necessário exportar ou preservar dados das aplicações Docker inventariadas.
- Banco e uploads do Cartório, dados da Rifa, banco HML e volumes antigos de `prd_fejjb`/`jiu_jitsu_system` podem ser apagados.
- O cache de build pode ser limpo.
- Imagens, volumes anônimos, diretórios antigos e cache de build também foram descartados.
- A remoção foi concluída pelo usuário em 10/10/2026 e validada conforme o resultado acima.
