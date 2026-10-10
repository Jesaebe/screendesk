# PRD — ScreenDeck Home

**Status:** Planejamento aprovado
**Versão:** 1.0
**Data:** 09/10/2026

## 1. Visão do produto

Criar uma ScreenDeck residencial: um painel touch dedicado, exibido em um PC tablet Linux, para centralizar informações pessoais e controles de automação. A plataforma de automação, integrações e backups será hospedada em um servidor Linux separado, sempre ligado.

O objetivo é ter uma experiência semelhante a um smart display: ao olhar para o tablet, o usuário vê data, hora, calendário e tarefas; ao tocar, executa comandos como controlar o ar-condicionado. O assistente de voz em português será implementado somente em fase posterior.

## 2. Objetivos

- Exibir um painel visual em tela cheia no tablet.
- Mostrar data, hora, calendário e tarefas do Google Tasks.
- Controlar dispositivos e executar automações, começando pelo ar-condicionado.
- Manter backups automáticos de bancos de dados remotos, com cópia local e cópia criptografada em nuvem.
- Manter uma base extensível para incluir voz, novos dispositivos, câmeras e alertas futuramente.

## 3. Fora do escopo inicial

- Assistente de voz com palavra de ativação contínua.
- Controle de câmeras, alarmes, Zigbee, Z-Wave, Thread ou Matter.
- Aplicativo mobile próprio.
- Acesso público direto pela internet.
- Backup de arquivos de banco de dados em uso; backups serão lógicos e consistentes por ferramenta nativa de cada banco.

## 4. Arquitetura aprovada

```text
PC Tablet Linux (cliente)
  └─ Chromium em modo kiosk
       └─ Dashboard do Home Assistant via rede local

Servidor Ubuntu 24.04 (serviços)
  ├─ Docker Compose
  │    ├─ Home Assistant Container
  │    └─ Serviço de backup independente
  ├─ /srv/backups (volume LVM dedicado)
  └─ Futuro: serviços locais de voz

Nuvem
  └─ Google Drive com cópia criptografada de backups
```

### 4.1 Tablet ScreenDeck

- Sistema atual: Debian 12, arquitetura i686 (32 bits), 2 GB de RAM.
- Papel exclusivo: exibir o dashboard via navegador e oferecer interação touch.
- Não executará Home Assistant, Docker, automações nem backups.
- Áudio de captura e reprodução foi identificado pelo sistema; será validado presencialmente quando a fase de voz iniciar.

### 4.2 Servidor

- Sistema: Ubuntu 24.04.4 LTS, x86_64.
- CPU: Intel Core i3-7100U, 4 CPUs lógicas.
- Memória: 8 GB RAM e 4 GB swap.
- Disco físico: 223,6 GB em LVM.
- Volume raiz atual: 100 GB.
- Volume dedicado a backup: `backups-lv`, ext4, 100 GB, montado em `/srv/backups`.
- Espaço livre restante no grupo LVM: aproximadamente 20 GB.

## 5. Funcionalidades

### 5.1 Dashboard — fase inicial

- Relógio e data atual, com visual legível à distância.
- Calendário Google.
- Lista de tarefas do Google Tasks, permitindo visualizar e concluir itens.
- Botões de automação por ambiente/dispositivo.
- Indicador de disponibilidade do Home Assistant e status do último backup.

### 5.2 Automação

- Controle inicial do ar-condicionado: ligar, desligar, definir modo/temperatura quando a integração do aparelho permitir.
- Criação de cenas e rotinas por botão no painel.
- Todas as automações devem poder ser acionadas pela interface do Home Assistant.
- A integração exata do ar-condicionado será definida após identificar marca, modelo e forma de controle (Wi-Fi, infravermelho ou outro).

### 5.3 Google

- Conectar Google Calendar e Google Tasks via OAuth.
- Exibir as listas/tarefas relevantes no dashboard.
- Não salvar senha da conta Google no servidor; utilizar autorização OAuth e segredos fora do repositório.

### 5.4 Backups

- Executar backups agendados de bancos de dados remotos.
- PostgreSQL: `pg_dump` ou ferramenta equivalente adequada ao ambiente.
- MySQL/MariaDB: `mariadb-dump`/`mysqldump` ou equivalente.
- Gravar cada execução inicialmente em `/srv/backups`.
- Compactar e criptografar o conteúdo antes do envio à nuvem.
- Enviar uma segunda cópia para uma pasta dedicada no Google Drive.
- Usar criptografia do lado do servidor antes do envio; os arquivos no Google Drive não devem ficar legíveis fora da ferramenta de backup.
- Registrar data, resultado, tamanho e erros de cada execução.
- Produzir relatório consultável de cada execução, contendo: identificador, banco/origem, início, fim, duração, tamanho final, destino local/cloud, status, mensagem de erro e arquivo de log.
- Exibir no dashboard: último backup concluído, data/hora, destino, tamanho, duração e falhas.
- Exibir histórico dos backups recentes, com filtros por origem e status.
- Em caso de falha, criar alerta persistente no Home Assistant e enviar e-mail com a origem afetada, data/hora e resumo do erro.
- Reter no Google Drive somente os últimos 15 dias de backup; remover automaticamente versões mais antigas.
- No armazenamento local, manter backups até atingir o limite de segurança de espaço. Ao atingir o limite, remover os mais antigos até restaurar uma margem livre segura; nunca deixar o volume chegar a 100% de uso.
- Limite inicial sugerido para a limpeza local: iniciar ao alcançar 85% de uso e limpar até voltar a 75%, preservando espaço para o próximo dump.
- Testar restauração periodicamente; backup sem teste de restauração não é considerado validado.

## 6. Requisitos não funcionais

- Operação preferencialmente local na rede residencial/empresa.
- Serviços reiniciam automaticamente após reboot ou falha.
- Credenciais e chaves não entram no Git: usar `.env` com permissões restritas ou mecanismo de secrets.
- Dashboard não deve expor controles sem autenticação fora da rede local.
- Backups precisam de criptografia em repouso e em trânsito.
- O dashboard deve conter uma área de saúde do servidor com uso atual e histórico básico de CPU, memória, disco raiz, volume `/srv/backups`, carga do sistema e disponibilidade dos containers do projeto.
- Definir limiares de alerta para CPU sustentada, memória insuficiente, disco raiz com pouco espaço, volume de backups próximo do limite e indisponibilidade do Home Assistant.
- Alterações de infraestrutura devem ser documentadas neste projeto antes ou logo após a execução.
- Antes de mudanças que afetem serviços existentes, verificar portas, containers e consumo de disco.

## 7. Tecnologias

| Camada | Tecnologia |
|---|---|
| Automação e dashboard | Home Assistant Container |
| Orquestração | Docker Compose |
| Host do servidor | Ubuntu 24.04 LTS |
| Tela dedicada | Chromium em modo kiosk no Debian 12 do tablet |
| Tarefas e calendário | Integrações oficiais Google Tasks e Google Calendar |
| Backup lógico | pg_dump / mariadb-dump ou equivalente |
| Repositório cloud | Google Drive, com backup criptografado via rclone/solução equivalente |
| Agendamento | systemd timer ou serviço de backup com agendamento próprio |
| Voz futura | Home Assistant Assist + serviços de STT/TTS locais ou compatíveis |

## 8. Segurança

- Home Assistant acessível inicialmente apenas na LAN.
- Criar usuário administrador individual, senha forte e MFA quando disponível.
- Usar conta de banco exclusiva para backup, com o menor privilégio necessário para realizar dumps.
- Utilizar credenciais OAuth do Google Drive com acesso restrito à pasta dedicada de backup e mantê-las fora do repositório.
- Não abrir portas no roteador nesta fase.
- Não armazenar tokens, senhas, chaves de recuperação ou arquivos `.env` no repositório.

## 9. Fluxo de desenvolvimento e implantação

- Todo código, Docker Compose, scripts, documentação e testes serão criados inicialmente na máquina local de desenvolvimento.
- A máquina local não deve sofrer alterações de infraestrutura, instalações de serviços, execução de containers do projeto ou mudanças de sistema para este projeto.
- O servidor é ambiente de produção e não deve receber alterações durante o desenvolvimento da primeira versão.
- Durante o desenvolvimento, é permitido conectar ao servidor por SSH somente para coleta de informações e testes estritamente não destrutivos (por exemplo: versões, disponibilidade de portas, recursos, conectividade e leitura de logs autorizados).
- Alterações no servidor — instalação, criação/edição de arquivos, containers, credenciais, serviços, agendamentos, firewall ou deploy — só poderão ocorrer após a primeira versão estar pronta e mediante confirmação explícita do usuário.
- A implantação será realizada posteriormente por SSH, a partir dos artefatos versionados e validados localmente.
- O repositório deve conter instruções reprodutíveis de implantação, arquivo de exemplo de variáveis (`.env.example`) e nenhum segredo real.

## 10. Plano de implantação

1. **Inventário do servidor:** verificar Docker, Compose, containers existentes, portas 80/443/8123 e utilização de disco.
2. **Preparar estrutura do projeto:** repositório Git, diretórios, `.gitignore`, documentação e secrets locais.
3. **Instalar Home Assistant Container:** criar Compose isolado, persistência, política de reinício e acesso na rede local.
4. **Criar dashboard inicial:** data/hora e layout otimizado para a resolução do tablet.
5. **Configurar o tablet:** Chromium em modo kiosk, inicialização automática e economia de tela adequada.
6. **Conectar Google:** OAuth para Calendar e Tasks.
7. **Integrar ar-condicionado:** identificar o modelo e configurar entidade, cartões e automações.
8. **Implementar backup local:** dumps, logs, relatório por execução, retenção, alertas no painel e e-mail de falha.
9. **Implementar backup em nuvem:** Google Drive, autenticação OAuth, criptografia, retenção de 15 dias e teste de restauração.
10. **Adicionar voz:** somente após o painel, automações e backups estarem estáveis.

## 11. Critérios de aceite da primeira versão

- Tablet abre automaticamente o dashboard em tela cheia após reiniciar.
- Dashboard apresenta data, hora, calendário e tarefas.
- Ao menos uma ação do ar-condicionado é controlável pelo painel.
- Backup de teste é criado em `/srv/backups`, aparece no relatório e é enviado criptografado à nuvem.
- Uma falha de backup simulada gera alerta persistente no dashboard e e-mail.
- Dashboard exibe CPU, memória, disco do sistema, disco de backups e disponibilidade dos serviços.
- Uma restauração de teste é documentada e concluída com sucesso.

## 12. Pendências para levantamento

- Confirmar quais bancos serão copiados, seus hosts, tipos, tamanhos e horários permitidos para backup.
- Confirmar a conta Google e a pasta dedicada do Google Drive a ser usada.
- Identificar marca/modelo do ar-condicionado e método de integração.
- Definir resolução, orientação e comportamento de tela do tablet.
- Levantar quais listas do Google Tasks e calendários devem aparecer.
- Definir frequência e retenção final dos backups.
- Definir conta remetente e destinatários dos e-mails de alerta.
- Definir limiares finais de alerta de CPU, memória e armazenamento.

## 13. Instruções para o Codex

- Leia este PRD antes de alterar qualquer arquivo ou executar instalação.
- Trabalhe por etapas e apresente o plano antes de mudanças relevantes.
- Preserve serviços, containers e configurações já existentes no servidor.
- Não realizar alterações no servidor durante o desenvolvimento; conexões SSH nesta fase são somente de leitura e diagnóstico não destrutivo.
- Preparar a primeira versão localmente e aguardar autorização explícita antes de qualquer implantação no servidor.
- Não execute comandos destrutivos, formatações, remoções ou alterações de firewall sem confirmação explícita.
- Após cada etapa, atualize esta documentação ou um arquivo `STATUS.md` com decisões, comandos aplicados, verificações e pendências.
- Use Docker Compose para os serviços do projeto, com volumes nomeados ou diretórios persistentes claramente documentados.
- Não inclua segredos no Git, nos logs ou em arquivos compartilhados.
