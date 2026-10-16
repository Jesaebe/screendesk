# Status — ScreenDeck Home

## 2026-10-16 — Duração individual dos backups

- Cada banco passa a iniciar seu próprio cronômetro somente quando sua execução começa.
- O horário compartilhado da rodada continua sendo usado apenas para identificar e deduplicar o agendamento.
- O indicador ao vivo, o card de backups realizados e o histórico deixam de acumular o tempo gasto pelos bancos processados anteriormente.
- Os registros exibidos no histórico permanecem persistidos em `history.jsonl` no volume nomeado `backup-status`, montado como `/status` no serviço de backup e como `/backup-status` no dashboard.
- A revisão `a8f3330` foi implantada no servidor pela rede local, reconstruindo somente `dashboard` e `backup` após confirmar que não havia backup em andamento.
- Os dois serviços ficaram saudáveis, `/healthz` respondeu com sucesso e o Home Assistant preservado não foi removido.

## 2026-10-15 — Inclusão de banco isolada da edição

- O botão “Novo” passa a iniciar explicitamente um cadastro sem identificador, mesmo após a edição de outra origem.
- Depois de salvar, o formulário abandona o modo de edição antes de recarregar a lista.
- Isso impede que uma inclusão reutilize o identificador oculto do último banco selecionado e o substitua.

## 2026-10-15 — Lista de bancos dimensionada para cinco cadastros

- O gerenciamento de bancos mostra até cinco cadastros completos antes de limitar a altura da lista.
- Quando existem mais de cinco bancos, todos continuam disponíveis por uma barra de rolagem vertical.
- O dimensionamento é recalculado ao abrir o diálogo, salvar um cadastro e redimensionar a janela.
- Os cadastros permanecem persistidos no arquivo protegido `secrets/sources.toml` do servidor.

## 2026-10-14 — Cadastro de bancos compactado e seleção reforçada

- O formulário usa quatro colunas em telas amplas, três em larguras intermediárias e reduz progressivamente em telas menores.
- A lista separa explicitamente bancos ativos e pausados, incluindo a contagem e um estado vazio para cada grupo.
- Cada botão recebe seu próprio manipulador de edição; a lista deixou de usar o gesto de arraste que podia cancelar cliques do mouse.
- O cadastro vigente no servidor contém quatro origens, todas ativas; não havia origem pausada no arquivo no momento da verificação.

## 2026-10-14 — Datas de tarefas, cadastro de bancos e duração corrigidos

- Datas de conclusão do Google Tasks são exibidas como datas civis, sem conversão de fuso ou horário deslocado.
- A seleção de bancos cadastrados voltou a preencher o formulário de edição de forma síncrona e destaca visualmente a origem selecionada.
- O modal de bancos foi reorganizado em uma lista lateral estável e formulário de duas colunas, com empilhamento responsivo para evitar sobreposições.
- Durações de backups concluídos e em andamento usam minutos e segundos e acrescentam horas quando chegam a 60 minutos.
- HTML, CSS e JavaScript passam a usar `Cache-Control: no-store`, garantindo que uma recarga mostre a versão recém-implantada.
- A suíte completa passou com 89 testes; a entrega foi autorizada para implantação integral no dashboard.

## 2026-10-13 — Botão de recarga do painel preparado

- Um botão de reload foi acrescentado imediatamente à direita do bloco de clima no cabeçalho.
- A ação recarrega o dashboard completo, atualizando clima, agenda, tarefas, backups e métricas.
- O controle possui rótulo acessível, tooltip e dimensões próprias para toque, inclusive em telas estreitas.
- A revisão `fdfa808` foi implantada reconstruindo somente o dashboard; dashboard e backup foram confirmados saudáveis e sem backup em andamento.
- O Firefox ESR do tablet foi encerrado isoladamente e reaberto pelo launcher em modo kiosk, passando do PID `4386` para `5201`.

## 2026-10-13 — Sobreposição no cadastro de bancos corrigida localmente

- O formulário de bancos passou de quatro para três colunas no layout amplo, dando largura útil aos campos ao lado da lista de origens.
- Labels, inputs e selects agora podem encolher dentro do grid sem invadir campos vizinhos.
- O modal ganhou altura máxima e rolagem própria; abaixo de 900 px o conteúdo é empilhado e abaixo de 520 px o formulário usa uma coluna.
- Os botões de ação agora quebram linha quando necessário, evitando sobreposição em telas estreitas.
- A suíte completa passou com 86 testes e o diff não apresentou erros de whitespace; a correção foi implantada junto da revisão `fdfa808`.

## 2026-10-13 — Cadastro de bancos reorganizado

- O modal de bancos foi dividido entre a lista de origens e o formulário de conexão, aproveitando a largura da tela e eliminando a rolagem no layout do tablet/desktop.
- O campo visível “Identificador” foi removido; novas origens recebem internamente um identificador derivado do nome, com sufixo automático para evitar duplicidade.
- Edições preservam o identificador existente, mantendo históricos, diretórios e referências de backup compatíveis.
- A revisão `1596052` foi implantada reconstruindo somente o dashboard; o Firefox foi reiniciado para carregar os arquivos novos.
- O layout servido foi confirmado, e dashboard e backup permaneceram saudáveis.

## 2026-10-13 — Atualização automática das tarefas implantada

- Agenda e tarefas do Google passam a sincronizar em segundo plano a cada 15 segundos e imediatamente ao retornar para a tela.
- Ao concluir uma tarefa no painel, o item e o contador são atualizados na hora e em seguida reconciliados com o Google.
- Atualizações silenciosas preservam o conteúdo visível durante falhas transitórias e evitam requisições Google simultâneas.
- A revisão `7c500ca` foi implantada reconstruindo somente o dashboard; o Firefox foi reiniciado pelo launcher para carregar o novo JavaScript.
- O container servido contém os novos gatilhos, dashboard e backup permaneceram saudáveis e não havia backup em andamento.

## 2026-10-13 — Sessão persistente e filtros do Google corrigidos

- A lista de eventos do calendário passa a mostrar somente eventos do dia atual em diante; a grade mensal continua completa.
- Tarefas voltaram a exibir todos os itens não concluídos, incluindo tarefas vencidas e sem data, com rolagem própria.
- O dashboard emite uma sessão assinada após a autenticação válida, sem armazenar a senha no navegador como URL, script ou arquivo do projeto.
- A revisão `f501de9` foi implantada reconstruindo somente o dashboard; a sessão foi validada com autenticação inicial e acesso posterior sem credenciais, e dashboard e backup permaneceram saudáveis.
- O Firefox do tablet abriu diretamente no painel após encerramento e reinício, sem repetir a solicitação de usuário e senha.
- O launcher foi corrigido para continuar ativo quando o Firefox encerra; o teste real confirmou novo processo kiosk iniciado automaticamente após cinco segundos.

## 2026-10-13 — Calendário e rolagem implantados; autostart do tablet preparado

- O dashboard passou a exibir somente tarefas com vencimento de hoje em diante, na data de `America/Bahia`; tarefas vencidas e sem data ficam ocultas.
- Agenda, tarefas e listas roláveis aceitam arraste por mouse/touch sem seleção acidental de texto; um arraste não conclui tarefas por engano.
- A revisão `ede797a` foi implantada no servidor, reconstruindo somente o dashboard; o backup permaneceu saudável e sem execução ativa.
- O container servido contém o filtro e a rolagem novos, `/healthz` respondeu 200 e a API sem credenciais permaneceu protegida com 401.
- O launcher do tablet foi adaptado para priorizar o Firefox ESR instalado, abrir em kiosk após o login automático e reiniciar após encerramento inesperado.
- O autostart foi instalado no perfil `painel`, com a credencial do dashboard salva diretamente no perfil persistente do Firefox, sem senha em URL, script ou Git.
- Após reinício real do tablet, o launcher iniciou automaticamente e abriu `firefox-esr --kiosk http://192.168.25.249:8123`; bloqueio e inatividade permaneceram desativados.

## 2026-10-12 — Legibilidade da lista de backups preparada

- A fonte dos cinco backups recentes foi ampliada, com maior destaque para a origem e ajuste específico para horário e metadados.
- O modal de histórico recebeu a mesma hierarquia visual, aumentando nome, detalhes e data sem alterar a quantidade de registros.
- O espaçamento compacto foi preservado para manter os cinco itens dentro do card e o dashboard sem rolagem geral.
- A revisão foi implantada pelo commit `2a3f082`, reconstruindo somente o dashboard; o backup não foi interrompido.
- O CSS servido contém a nova escala tipográfica e dashboard e backup permaneceram saudáveis.

## 2026-10-12 — Tamanho, duração e cores no histórico preparados

- Os cinco backups recentes passam a mostrar tamanho e duração ao lado da origem e do horário.
- O modal do histórico recebe os mesmos dados, com resultado traduzido para “Concluído” ou “Falhou”.
- Os pontos à esquerda ficam verdes para sucesso e vermelhos para falha, tanto no card quanto no modal; o motivo da falha permanece disponível no tooltip.
- A revisão foi implantada pelo commit `86913de`, reconstruindo somente o dashboard; o serviço de backup não foi interrompido.
- A versão servida contém tamanho, duração, renderizador do modal e estilos verde/vermelho; dashboard e backup permaneceram saudáveis.

## 2026-10-12 — Cinco backups recentes no card preparados

- O card passa a mostrar abaixo do resultado atual os cinco backups mais recentes, com origem, resultado, horário e detalhe disponível ao apontar.
- A lista se atualiza quando surge um novo relatório e também a cada 30 segundos, sem recarregar a página.
- Histórico completo e gerenciamento de bancos permanecem disponíveis em botões compactos com ícones, tooltip e rótulos acessíveis.
- O layout foi mantido dentro do card para preservar o dashboard sem rolagem geral.
- A revisão foi implantada pelo commit `26b6f55`, reconstruindo somente o dashboard; o backup não foi interrompido.
- A versão servida contém o novo bloco e o renderizador limitado a cinco itens; a API retornou 14 registros, com os cinco mais recentes disponíveis para o card.
- O backup mais recente da origem `camara` já aparece como `success`; dashboard e backup permaneceram saudáveis.

## 2026-10-12 — Causa detalhada das falhas de dump preparada

- O serviço de backup passa a registrar no relatório a primeira linha útil e sanitizada emitida pelo comando de dump, limitada a 300 caracteres.
- Para a falha atual e outros relatórios antigos, o dashboard recupera o detalhe do log sanitizado por um caminho validado e somente leitura, sem alterar o histórico.
- A saída completa continua apenas no log operacional e o código de saída permanece como fallback quando não houver detalhe reconhecível.
- A revisão foi implantada pelo commit `083de1c`, reconstruindo dashboard e backup após confirmar ausência de locks ativos.
- Sem executar novo backup, a API passou a devolver para a falha atual: `pg_dump: error: query failed: ERROR: permission denied for table cam_cidades`.
- Dashboard e backup permaneceram saudáveis após a implantação.

## 2026-10-12 — Motivo da falha no card de backup preparado

- Quando o último backup falha, o card troca o campo de tamanho por “Motivo” e mostra o erro sanitizado já presente no relatório.
- O horário passa a ser identificado como “Falhou em”; o layout continua com quatro campos para não aumentar a altura do dashboard.
- O relatório atual da origem `camara` foi confirmado com `status=failed` e motivo sanitizado disponível para exibição.
- A correção foi implantada pelo commit `05944ef`, reconstruindo somente o dashboard; o serviço de backup não foi recriado.
- A versão servida contém a leitura de `backup.error`, o relatório atual mantém o motivo disponível e dashboard e backup ficaram saudáveis.

## 2026-10-12 — Indicador de backup em andamento preparado

- O agendador publica no volume compartilhado a origem e o início da execução enquanto o pipeline está ativo, removendo o indicador ao concluir ou falhar.
- O card de backups consulta esse estado a cada segundo e exibe spinner, banco em processamento, horário inicial e duração ao vivo sem perder o último resultado concluído.
- A nova API é somente leitura e o estado ativo é limpo também na inicialização, evitando indicação obsoleta após reinício.
- A suíte completa passou com 75 testes e a validação local não executou infraestrutura nem um backup real.
- A revisão foi implantada pelo commit `471aaf1`, reconstruindo dashboard e backup após confirmar ausência de lock ou execução em andamento.
- Dashboard e backup ficaram saudáveis; a API manteve o último resultado `success` e uma simulação somente do marcador confirmou `running` sem gerar dump ou upload.
- O marcador sintético foi removido automaticamente ao final da validação, a rota sem credenciais respondeu 401 e o HTTPS público permaneceu protegido com 401.

## 2026-10-12 — Teste de conexão de bancos preparado

- O cadastro recebeu “Testar conexão”, com spinner e resultado de versão, latência ou falha sanitizada.
- A consulta roda no serviço de backup com `cyriusBackup` e o segredo existente, sem senha no navegador, argumentos ou resposta.
- A API de teste fica somente na rede interna do Compose e não publica porta no host.
- Uma origem nova, reativada ou com conexão alterada não pode ser ativada sem aprovação do teste para os mesmos dados.
- A revisão foi implantada pelo commit `9efc0c4`, reconstruindo dashboard e backup após confirmar ausência de execução em andamento.
- O novo fluxo testou Maker de ponta a ponta com sucesso: PostgreSQL `14.11`, latência de 861 ms, sem dump ou upload.
- A porta interna 8090 não ficou publicada no host; HTTPS respondeu 200 e dashboard e backup permaneceram saudáveis.

## 2026-10-12 — Cadastro de bancos preparado

- O dashboard recebeu gerenciamento de origens para criar, editar, pausar e remover bancos, com horários independentes e validação dos campos.
- Todas as origens são fixadas no usuário `cyriusBackup` e no segredo existente `maker-password`; nenhuma senha é enviada ao navegador ou gravada no cadastro.
- O serviço de backup passa a reler o cadastro antes de cada rodada, mantendo a configuração anterior se uma recarga falhar.
- Remoção exige pausa prévia e preserva dumps e históricos existentes.
- A revisão foi implantada pelo commit `aee968d`, reconstruindo dashboard e backup após confirmar ausência de execução em andamento.
- Um cadastro temporário desativado foi criado, relido e removido pelo endpoint; ele usou automaticamente `cyriusBackup` e `maker-password`, sem executar dump.
- O arquivo permaneceu `0600`, o cadastro final voltou a conter somente Maker ativo nos quatro horários, o último backup continuou `success` e ambos os containers ficaram saudáveis.
- HTTPS respondeu 200 e o endpoint de cadastro sem credenciais permaneceu protegido com HTTP 401.

## 2026-10-12 — Ícones ampliados e carregamento Google preparados

- Os ícones de CPU, memória, disco raiz, backups e carga foram ampliados e posicionados à esquerda dos respectivos dados.
- Agenda e tarefas passaram a exibir spinners com texto durante a carga inicial e a troca de mês, além de mensagens próprias para desconexão e erro.
- A revisão foi implantada pelo commit `e7a0c81`, reconstruindo somente o dashboard; dashboard e backup permaneceram saudáveis.
- Foram confirmados cinco ícones ampliados, dois estados de carregamento, animação do spinner, oito eventos, três tarefas e HTTPS com resposta 200.

## 2026-10-12 — Lista mensal e ícones de métricas preparados

- O espaço abaixo da grade mensal passou a exibir todos os eventos do mês com data, horário e título em uma lista com rolagem própria.
- Os cinco blocos internos de saúde receberam ícones específicos para CPU, memória, disco raiz, backups e carga.
- A página principal continua sem rolagem; somente a lista de eventos do mês pode rolar dentro do cartão.
- A revisão foi implantada pelo commit `bf5ab71`, reconstruindo somente o dashboard; dashboard e backup permaneceram saudáveis.
- A validação confirmou oito eventos e três tarefas no mês atual, a lista mensal servida, os cinco ícones internos e HTTPS com resposta 200.

## 2026-10-12 — Calendário mensal e leitura visual preparados

- O relógio passou a exibir segundos e os cartões receberam ícones de identificação.
- O cartão Google agora apresenta o mês completo, permite avançar e retroceder, destaca hoje e marca dias com eventos.
- A API aceita o mês selecionado e consulta seus limites completos, incluindo dias anteriores ao momento atual.
- O histórico de saúde recebeu título e legenda explícita, com barras separadas para CPU e memória.
- A revisão foi implantada pelo commit `d3b8ac5`, reconstruindo somente o dashboard; dashboard e backup permaneceram saudáveis.
- A conta Google autorizada retornou o mês solicitado, oito eventos e três tarefas sem expor conteúdo; HTTPS respondeu 200 e a API sem credenciais permaneceu em 401.

## 2026-10-12 — Tela única e métricas em tempo real preparadas

- O layout kiosk passou a organizar os quatro cartões principais em uma linha, compactar-se em telas baixas e ocupar uma única viewport sem rolagem a partir de 900 px de largura.
- CPU, memória e discos agora exibem capacidade total: CPUs lógicas, memória instalada e tamanho total da raiz e de `/srv/backups`.
- Valores atuais são coletados e consultados a cada segundo; o histórico permanece em uma amostra por minuto, preservando a janela de 24 horas com 1.440 registros.
- A revisão foi implantada no dashboard pelo commit `cd76288`; o backup não foi reiniciado e ambos os containers permaneceram saudáveis.
- O container confirmou intervalos de 1 e 60 segundos, duas leituras consecutivas de CPU variaram, capacidades totais foram retornadas, HTTPS respondeu 200 e a API sem credenciais respondeu 401.

## 2026-10-12 — Métricas do host implantadas

- O commit `fcaf766` foi aplicado ao servidor por bundle Git e fast-forward; o GitHub permanece em `12de150` por ausência de credencial de escrita neste ambiente.
- Dashboard e backup foram reconstruídos e recriados de forma direcionada; o Home Assistant preservado, o Nginx, os dados e os segredos não foram alterados.
- Os dois containers ficaram saudáveis; HTTP e HTTPS responderam 200 e o acesso à API sem credenciais permaneceu bloqueado com HTTP 401.
- A segunda amostra confirmou CPU, memória, discos raiz e de backups, disponibilidade de dashboard e backup e histórico persistente.
- O último backup do Maker permaneceu com `status=success`; não havia execução nem lock de backup durante a implantação.

## 2026-10-12 — Métricas do host preparadas localmente

- O dashboard passou a coletar CPU, carga, memória, swap, uptime, disco raiz e volume `/srv/backups` diretamente do host a cada minuto.
- Uma nova área de saúde apresenta os valores atuais, disponibilidade do dashboard e do backup e um histórico visual recente.
- O histórico persistente é limitado a 1.440 amostras; o backup publica heartbeat no volume de status compartilhado.
- A solução não usa socket Docker, modo privilegiado, pacotes adicionais nem exposição ampla de `/proc`; somente os quatro arquivos necessários e dois pontos de filesystem são montados como leitura.
- Validação local: 69 testes aprovados, configuração e sintaxe Python aprovadas e diff sem erros de whitespace.
- Nada foi implantado nesta etapa. A ativação exige reconstruir o dashboard e o backup de forma controlada, preservando dados e demais serviços.

## 2026-10-12 — Tema roxo implantado

- O dashboard passou a usar `#723ebe` como cor principal em uma paleta roxa escura.
- Verde foi preservado exclusivamente para estados de sucesso; alertas e falhas mantêm suas cores semânticas.
- Contraste validado: 8,72:1 nos botões principais e 17,76:1 no texto sobre o fundo.
- Somente o dashboard foi reconstruído; Google permaneceu autorizado e dashboard e backup continuam saudáveis.

## 2026-10-12 — Dashboard customizado implantado

- O commit `821694a` foi aplicado ao servidor por bundle Git e fast-forward; a publicação no GitHub continua pendente por ausência de credencial de escrita neste ambiente.
- O dashboard foi construído, validado e iniciado na porta 8123; Nginx e HTTPS permaneceram no mesmo endereço.
- O Home Assistant foi parado, mas seu container e dados foram preservados para rollback.
- O serviço de backup não foi recriado nem interrompido e continua saudável.
- Validação operacional: dashboard saudável, autenticação sem credenciais retorna HTTP 401, clima de Salvador respondeu, último backup possui `status=success` e logs não têm erros.
- A credencial OAuth Google está montada; Calendar e Tasks aguardam somente a autorização do usuário pelo botão “Conectar Google”. SmartThings permanece opcional e desconectado.

## 2026-10-12 — Credencial OAuth Google instalada

- O cliente OAuth Web foi validado sem expor `client_id` ou `client_secret`.
- Origem autorizada: `https://hml.cyrius.com.br`; callback: `https://hml.cyrius.com.br/oauth/google/callback`.
- O JSON foi instalado fora do Git em `secrets/dashboard/google-client.json`, proprietário `cyrius:cyrius`, modo `0600`.
- Próximos segredos: senha do dashboard e token SmartThings. A autorização da conta Google ocorrerá pelo navegador depois da implantação.

## 2026-10-12 — HTTPS ativado

- O Certbot emitiu e instalou um certificado Let's Encrypt para `hml.cyrius.com.br`, válido até 10/01/2027.
- O Nginx escuta em 443 e redireciona HTTP para HTTPS; configuração e resposta local com SNI foram aprovadas.
- O timer de renovação está ativo e `certbot renew --dry-run --no-random-sleep-on-renew` concluiu com sucesso.
- O bloco Nginx anterior foi preservado em `/etc/nginx/hml.before-tls-20261012`, fora de `sites-enabled`.
- O servidor não oferece NAT loopback para o próprio endereço público, mas DNS, certificado, listeners e proxy local foram validados.
- Próximo passo: criar as credenciais Google/SmartThings e a senha do dashboard antes da substituição do Home Assistant.

## 2026-10-12 — Dashboard customizado preparado

- A direção do produto foi simplificada: o Home Assistant será substituído por um dashboard próprio e pequeno.
- A base local apresenta data/hora, clima configurável via Open-Meteo, Google Calendar, Google Tasks, situação e histórico dos backups e controles SmartThings para o Samsung WindFree Connect.
- O dashboard usa somente a biblioteca padrão do Python no servidor e HTML/CSS/JavaScript no navegador.
- OAuth Google, token SmartThings e senha do painel ficam fora do Git.
- O Compose preserva o backup e o volume `backup-status`; a porta 8123 permanece para evitar alteração imediata no Nginx.
- A implantação parará o container antigo sem removê-lo, permitindo rollback. Nada desta versão foi implantado no servidor.
- Validação local: 67 testes aprovados, sintaxe Python e Bash aprovadas e diff sem erros de whitespace.
- Próximos passos: configurar HTTPS, criar credencial OAuth Google, instalar token SmartThings e senha do painel, validar o aparelho e executar a substituição controlada.

## 2026-10-11 — Home Assistant ativado no servidor

- O checkout do servidor recebeu por fast-forward os commits até `41d813e`; a publicação desse commit no GitHub permanece pendente porque nenhum dos ambientes possui credencial de escrita disponível.
- A pré-checagem de produção foi aprovada integralmente antes da mudança, incluindo host, Docker, Compose, porta 8123, armazenamento, segredos e configuração declarativa.
- A imagem fixada `ghcr.io/home-assistant/home-assistant:2026.10.1` foi baixada e a configuração foi aprovada pelo verificador da própria imagem.
- Somente o serviço `home-assistant` foi criado e iniciado; ele respondeu localmente e pela LAN em `http://192.168.25.249:8123`, com redirecionamento HTTP 302 para o onboarding.
- O container de backup não foi recriado, permaneceu ativo e saudável durante e após a implantação.
- Os logs iniciais do Home Assistant não apresentaram erro de configuração; houve apenas um `SyntaxWarning` interno de dependência durante a inicialização.
- Artefatos normais gerados na primeira execução (`.HA_VERSION`, `.ha_run.lock` e `blueprints/`) foram adicionados ao `.gitignore`.
- Próximo passo: o usuário deve abrir a URL LAN e concluir o onboarding criando a conta administradora individual; depois serão configuradas as integrações Google.

## 2026-10-11 — Ativação do Home Assistant preparada

- O deploy passou a executar uma ativação limitada ao serviço `home-assistant`, mantendo o backup em execução sem recriação.
- A rotina exige autorização explícita, repete a pré-checagem, baixa a imagem fixada, valida a configuração dentro da imagem, inicia o container e aguarda resposta HTTP por até 120 segundos.
- O rollback correspondente para somente o Home Assistant, com janela de 60 segundos, e preserva configuração, volumes e o serviço de backup.
- O Compose recebeu `stop_grace_period: 60s`, conforme a orientação oficial para encerramento limpo do banco interno do Home Assistant.
- Documentação operacional foi sincronizada com o estado real: backup ativo, `rclone` gravável para renovação OAuth e porta 8123 previamente aprovada.
- Validação local: 63 testes aprovados, sintaxe Bash aprovada, configuração aprovada e diff sem erros de whitespace.
- Nenhum Docker, SSH ou serviço foi executado; o Home Assistant permanece desligado.
- Próximo passo: publicar os artefatos e, mediante autorização explícita, executar a primeira ativação controlada no servidor.

## 2026-10-11 — Primeiro backup automático aprovado

- O slot automático das 00:00 em `America/Bahia` iniciou às 00:00:18 e terminou às 00:02:41 com `status=success`.
- O dump do Maker possui 12.433.797 bytes, pertence a `cyrius:cyrius` e usa modo `0600`.
- O upload criptografado foi concluído em `gdrive-crypt:screendeck-home/maker/`, que passou a conter dois objetos.
- O slot `2026-10-11T00:00` foi persistido no estado do agendador, protegendo contra repetição após reinício.
- O container permaneceu saudável e nenhum alerta de falha foi gerado.
- A cadeia de backup do Maker está operacional de ponta a ponta; próximas execuções previstas: 06:00, 12:00 e 18:00.
- Próximo passo: avançar para a implantação controlada do Home Assistant e das integrações funcionais pendentes.

## 2026-10-10 — Alertas Gmail ativados e testados

- A senha de app do Google foi instalada pelo usuário como arquivo protegido, com 16 bytes, proprietário `cyrius:cyrius` e modo `0600`; seu conteúdo não foi exibido.
- A negociação SMTP/STARTTLS com `smtp.gmail.com:587` foi validada e a autenticação com a senha de app funcionou.
- Um e-mail sintético de teste foi aceito pelo Gmail para `jesaebe@gmail.com`, sem provocar falha ou execução de backup.
- O usuário confirmou o recebimento da mensagem na caixa de entrada.
- O container de backup permaneceu saudável e o Maker continua com a agenda automática ativa.
- Próximo passo: acompanhar a primeira execução automática agendada.

## 2026-10-10 — Gmail preparado para alertas com segredo em arquivo

- Definido provisoriamente `jesaebe@gmail.com` como remetente e destinatário, até existir um e-mail corporativo.
- A senha SMTP deixou de ser aceita por variável de ambiente e passou a ser lida de `/run/secrets/smtp-password`.
- O Compose monta somente `/home/cyrius/.config/screendeck-home/smtp-password` como leitura, e o runbook orienta capturar uma senha de app do Google sem eco nem histórico.
- SMTP permanece desativado até o usuário criar a senha de app e instalar o arquivo protegido no servidor.
- Validação local: 62 testes aprovados, configuração aprovada e diff sem erros de whitespace.
- Próximo passo: publicar, instalar interativamente a senha de app e enviar um alerta de teste controlado.

## 2026-10-10 — Backup automático do Maker ativado

- Após autorização explícita, Maker foi alterado para `enabled = true` no `sources.toml` real do servidor.
- A agenda ativa é 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`, com retenção cloud de 15 dias.
- O arquivo permaneceu com modo `0600`, somente uma origem está habilitada e o container reiniciou saudável.
- As agendas são independentes por origem: bancos futuros podem ter quantidades e horários diferentes no próprio bloco `[[source]]`.
- Alterações de agenda exigem validação do TOML e reinício somente do serviço `backup`; não exigem reconstrução da imagem.
- SMTP ainda não está configurado, portanto falhas ficam registradas localmente, mas não geram e-mail.
- Próximo passo: acompanhar a primeira execução automática e configurar o canal de alertas SMTP.

## 2026-10-10 — Renovação OAuth do rclone validada

- O servidor foi atualizado para o commit `d4d54cd` e o `.env` migrou para `RCLONE_CONFIG=/run/rclone/rclone.conf` e `RCLONE_CONFIG_DIR_HOST=/home/cyrius/.config/rclone` sem expor valores secretos.
- O container foi recriado saudável com o diretório dedicado do rclone montado para leitura/escrita.
- Uma listagem pelo remote criptografado terminou com código zero e stderr vazio, confirmando a persistência OAuth sem o aviso anterior.
- O diretório montado contém somente `rclone.conf`; o arquivo permanece com modo `0600`, e um objeto do Maker foi confirmado no destino cloud.
- Maker continua com `enabled = false`; nenhum novo dump foi executado nesta validação.
- Próximo passo: obter autorização explícita para habilitar permanentemente os backups automáticos do Maker nos quatro horários aprovados.

## 2026-10-10 — Container de backup validado com origens desabilitadas

- O servidor foi atualizado para o commit `38a9526` e o build da imagem `screendeck-home-backup` foi concluído.
- Antes da inicialização, foi confirmado que o `sources.toml` real possui zero origens com `enabled = true`.
- Somente o serviço `backup` foi iniciado; o Home Assistant permanece desligado.
- O container está saudável e executa como usuário não-root `screendeck`, UID/GID `1000:1000`.
- `/status`, `/backups`, `sources.toml`, `maker-password` e `rclone.conf` ficaram acessíveis com os proprietários e modos esperados; nenhum conteúdo secreto foi exibido.
- Logs permaneceram vazios e não foram criados dumps, arquivos de estado, uploads ou relatórios, conforme esperado com todas as origens desabilitadas.
- Recursos criados: imagem de backup, rede interna, volume nomeado de status e o container `screendeck-home-backup-1` em execução.
- Próximo passo: mediante autorização específica, executar o primeiro backup controlado do Maker e validar dump local, upload criptografado e restauração antes da ativação permanente.

### Primeira execução controlada — falha segura antes do dump

- A primeira tentativa real parou na preparação do armazenamento, antes de chamar `pg_dump`, porque o volume contém o diretório de sistema `lost+found`, inacessível ao usuário do container.
- O mecanismo de proteção restaurou `enabled = false` e reiniciou o container saudável; nenhum dump ou upload foi criado.
- Foi gerado apenas um log sanitizado da falha abaixo de `/srv/backups/logs/maker/`.
- A varredura local foi corrigida para ignorar `lost+found` e pular de forma segura diretórios não gerenciados que não possam ser lidos.

### Segunda execução controlada — dump preservado, upload bloqueado

- O dump real do Maker foi concluído com 12.433.797 bytes e preservado localmente; o upload falhou antes de gravar a cópia cloud.
- A variável da aplicação `RCLONE_CRYPT_REMOTE` colidia com o namespace de configuração do próprio rclone e fazia o backend `crypt` apontar recursivamente para si mesmo, apesar do `rclone.conf` estar correto.
- A variável foi renomeada para `BACKUP_CLOUD_REMOTE`, removendo a colisão sem alterar o remote aprovado.
- O processo agora aplica `umask 077`; o dump e os logs já existentes foram corrigidos imediatamente para modo `0600`.
- Maker foi restaurado automaticamente para `enabled = false` e o container permanece saudável.

### Terceira execução controlada — pipeline e restauração aprovados

- O pipeline concluiu dump, upload criptografado e retenção cloud com `status=success`; o dump possui 12.433.797 bytes e modo `0600`.
- A cópia foi baixada novamente por `gdrive-crypt` para um arquivo temporário, teve SHA-256 idêntico ao dump local e catálogo validado por `pg_restore --list`; o temporário foi removido.
- Maker voltou automaticamente para `enabled = false` e o container permaneceu saudável.
- Durante o download, o rclone renovou o token, mas não conseguiu persistir a atualização porque o arquivo estava montado somente leitura. O mount individual de `rclone.conf` foi alterado para leitura/escrita, mantendo modo `0600`, UID 1000 e todos os demais segredos somente leitura.
- Próximo passo: publicar e aplicar o ajuste do token, validar que o rclone consegue persistir a configuração sem aviso e então decidir a ativação permanente do Maker.

### Ajuste do mount para renovação OAuth atômica

- O mount gravável do arquivo individual ainda não permitiu a renovação porque o rclone cria um temporário no diretório e substitui `rclone.conf` atomicamente.
- Confirmado que `/home/cyrius/.config/rclone` contém somente `rclone.conf`; o Compose passou a montar esse diretório dedicado em `/run/rclone`, com leitura/escrita.
- Maker permaneceu desabilitado, o container saudável e a listagem criptografada confirmou um objeto cloud; nenhum novo dump foi executado.

## 2026-10-10 — Entrypoint funcional do backup concluído

- O entrypoint agora carrega as origens TOML, monta o pipeline real e executa o laço contínuo do agendador.
- Dump, upload criptografado, retenção cloud, retenção local e notificação foram conectados aos adaptadores de produção sem shell.
- Os limites locais configuráveis de 85%/75% passaram a ser efetivamente repassados ao executor e são validados antes da inicialização.
- SMTP incompleto permanece explicitamente desabilitado e uma eventual tentativa de alerta registra a falha do canal sem derrubar o agendador.
- A imagem prepara `/status` com UID/GID do usuário não-root para persistir a deduplicação no volume nomeado.
- Maker continua com `enabled = false`; nenhum banco, rclone, container ou serviço real foi acessado ou iniciado nesta etapa.
- Validação local: 58 testes aprovados, configuração aprovada e diff sem erros de whitespace.
- Próximo passo: publicar o código e preparar um teste controlado do container de backup, ainda com Maker desabilitado, antes de autorizar a primeira execução real.

### Correção encontrada no primeiro build controlado

- O primeiro build no servidor parou antes de criar o container porque a imagem Debian já reserva o nome de usuário `backup`.
- O usuário interno foi renomeado para `screendeck`, preservando UID/GID `1000:1000` e todo o contrato de permissões do host.
- Nenhum container, dump ou upload foi iniciado durante a tentativa que revelou o conflito.

## 2026-10-10 — Pré-checagem do servidor aprovada

- Confirmados no servidor `.env`, `secrets/sources.toml`, o segredo do Maker e o `rclone.conf`, todos pertencentes a `cyrius:cyrius` e com modo `0600`; nenhum conteúdo secreto foi exibido ou copiado.
- `/srv/backups` foi atribuído a `cyrius:cyrius` (UID/GID `1000:1000`) e permanece com modo `0755`, atendendo ao contrato de escrita do serviço de backup.
- O usuário `cyrius` foi adicionado ao grupo `docker`, após autorização explícita, para acessar o socket do daemon; uma nova sessão confirmou a associação.
- `scripts/preflight-deploy.sh` foi aprovado integralmente: host, Ubuntu, Docker, Compose, porta 8123, armazenamento, segredos e configuração declarativa estão prontos.
- `docker ps` permaneceu vazio e nenhum container ou serviço do projeto foi iniciado.
- Próximo passo: concluir as decisões funcionais pendentes e habilitar o entrypoint real antes de qualquer implantação.

## 2026-10-10 — Repositório publicado e clonado no servidor

- Repositório privado/externo informado pelo usuário configurado como `origin`: `https://github.com/Jesaebe/screendesk.git`.
- A branch `main` foi publicada e validada no commit `d539366`.
- O projeto foi clonado via Git em `/home/cyrius/screendeck-home` no servidor acessado por SSH em `45.225.13.12:1522`.
- O checkout remoto ficou limpo e alinhado a `origin/main` no mesmo commit.
- Nenhum segredo foi transferido pelo Git; nenhum container ou serviço foi iniciado.
- Próximo passo: instalar interativamente o segredo do Maker, criar `.env` e `secrets/sources.toml` protegidos no servidor e corrigir, com autorização, a propriedade de `/srv/backups` antes da pré-checagem.

## 2026-10-10 — Acesso SSH externo confirmado

- Confirmado acesso ao servidor por `cyrius@45.225.13.12`, porta `1522`, usando autenticação não interativa já configurada.
- O host remoto se identifica como `cyrius`; o usuário operacional permanece UID/GID `1000:1000`.
- O `rclone.conf` continua presente com proprietário `cyrius:cyrius` e modo `0600`.
- `/srv/backups` continua `root:root` modo `0755` e ainda não atende ao contrato de escrita do container.
- O diretório novo `/home/cyrius/screendeck-home` não existia antes da tentativa de transferência; a estratégia foi alterada pelo usuário para distribuição via Git.
- Nenhum container ou serviço foi iniciado.

## 2026-10-10 — Segredo do Maker preparado como arquivo protegido

- O contrato deixou de transportar a senha do banco por variável de ambiente e passou a usar um arquivo exclusivo abaixo de `/run/secrets`.
- O Compose monta `/home/cyrius/.config/screendeck-home/maker-password` como `/run/secrets/maker-password`, somente leitura, sem incluir o valor no `.env`, no `sources.toml` ou nos argumentos do processo.
- O agendador lê o segredo somente no momento da execução, remove apenas a quebra de linha final e mantém sanitização de erros; arquivo ausente ou vazio resulta em `configuration_failed`.
- A pré-checagem passou a exigir o arquivo real e permissão `0600` ou mais restritiva, sem ler seu conteúdo.
- Foi adicionado um runbook de captura interativa sem eco nem histórico do shell; `secrets/` inteiro passou a ser ignorado pelo Git.
- Maker continua desabilitado e nenhum arquivo, segredo ou serviço foi alterado no servidor.
- Validação local: 52 testes aprovados, sintaxe Bash aprovada, validação de configuração aprovada e diff sem erros de whitespace.
- Próximo passo: mediante autorização explícita, instalar interativamente o segredo no servidor, preparar `secrets/sources.toml` ainda com Maker desabilitado e executar a pré-checagem somente leitura.

## 2026-10-10 — rclone.conf do servidor integrado ao Compose

- Confirmado por inspeção SSH somente leitura o arquivo já validado em `/home/cyrius/.config/rclone/rclone.conf`, pertencente a `cyrius:cyrius` e com modo `0600` no servidor definitivo.
- Confirmados sem revelar a configuração os remotes `gdrive` e `gdrive-crypt` no arquivo definitivo.
- O Compose passou a montar esse arquivo diretamente em `/run/secrets/rclone.conf`, somente leitura, sem refazer OAuth, recriar remotes ou copiar o segredo para o repositório.
- Como o arquivo `0600` pertence ao UID/GID `1000:1000`, o serviço de backup foi alinhado a esse mesmo usuário não-root; o servidor não possui ferramentas ACL instaladas e nenhuma permissão do segredo foi afrouxada.
- A configuração versionável das origens passou a ter montagem separada, evitando expor todo um diretório de segredos ao container.
- A pré-checagem valida existência e permissões do arquivo real no servidor sem ler seu conteúdo.
- Validação local: sintaxe Bash aprovada, 51 testes aprovados e `scripts/validate-config.sh` aprovado; nenhum acesso ou alteração foi feito no servidor.
- Próximo passo: instalar a senha de `cyriusBackup` como segredo protegido e preparar `sources.toml` no servidor antes de habilitar Maker.

## 2026-10-10 — Remotes rclone validados

- Os remotes `gdrive` e `gdrive-crypt` foram criados e testados pelo usuário.
- A configuração e os testes foram realizados no servidor definitivo; o `rclone.conf` permanece em `/home/cyrius/.config/rclone/rclone.conf` e não precisa ser copiado para a máquina de desenvolvimento.
- A pasta correta é `CyriusBackups`, com maiúsculas, diretamente na raiz do Google Drive.
- O remote criptografado grava dentro dessa pasta com nomes ilegíveis, conforme esperado.
- O usuário concluiu um teste de restauração: enviou uma pasta pelo remote criptografado e recuperou nomes e conteúdo originais por meio do `gdrive-crypt`.
- O remote base `gdrive` representa a raiz do Drive; portanto, caminhos informados depois de `gdrive:` são relativos à raiz e podem criar novas pastas.
- Nenhum token, senha ou conteúdo do `rclone.conf` foi registrado no repositório.
- Próximo passo: confirmar no servidor apenas o caminho e as permissões do `rclone.conf` já validado e instalar a senha de `cyriusBackup` como segredo protegido.

## 2026-10-10 — Destino Google Drive definido

- Conta aprovada: `jesaebe@gmail.com`.
- Pasta dedicada: `CyriusBackups`, diretamente na raiz do Drive.
- Planejados os remotes `gdrive` e `gdrive-crypt`, com a pasta aprovada como raiz visível e nomes/conteúdo abaixo dela criptografados.
- Adicionado runbook de OAuth, proteção do `rclone.conf` e teste de ida e volta sem dados sensíveis.
- Esta entrada registrava o planejamento inicial; a criação e a validação posteriores estão documentadas acima.

## 2026-10-10 — Conta de backup do Maker validada

- O usuário confirmou a criação bem-sucedida de `cyriusBackup` no PostgreSQL Maker.
- A autenticação e o `pg_dump` de validação também funcionaram.
- A origem permanece desabilitada até a senha ser instalada como segredo protegido no servidor e o remote `crypt` do Google Drive ser validado.
- Nenhuma senha foi recebida ou registrada no repositório.
- Próximo passo: definir a conta e a pasta do Google Drive para preparar a configuração criptografada do rclone.

## 2026-10-10 — Usuário de backup do Maker definido

- Nome escolhido: `cyriusBackup`, preservando maiúsculas e portanto citado em SQL como `"cyriusBackup"`.
- A configuração de exemplo deixou de usar o superusuário `postgres`, mas a origem continua desabilitada até criação e teste reais.
- Adicionado runbook SQL com `LOGIN`, sem privilégios administrativos, acesso ao banco `janus` e leitura dos schemas, tabelas e sequências existentes.
- Nenhuma senha foi criada ou registrada; o runbook orienta definição interativa pelo `psql`.
- Próximo passo: executar o runbook com acesso administrativo ao PostgreSQL Maker e validar `pg_dump`, mediante autorização e disponibilidade do acesso.

## 2026-10-10 — Pré-checagem de implantação preparada

- Adicionado `scripts/preflight-deploy.sh`, estritamente somente leitura, para validar o host esperado, Ubuntu, Docker/Compose, porta 8123, armazenamento, segredos, permissões e Compose antes do deploy.
- A escrita em `/srv/backups` é validada pelo contrato real do container: proprietário UID 10001 e permissão de escrita para o dono.
- Inventário e documentação de implantação foram sincronizados com a desativação Docker já concluída pelo usuário.
- `deploy.sh` e `rollback.sh` permanecem bloqueados e não executam mudanças; implantação continua sem autorização.
- Validação local: sintaxe Bash aprovada, 50 testes aprovados e `scripts/validate-config.sh` aprovado.
- Próximo passo: obter as definições funcionais e credenciais pendentes (usuário exclusivo de Maker, remote `crypt`, SMTP e integrações) antes de ligar o entrypoint real e preparar o deploy executável.

## 2026-10-10 — Desativação Docker concluída pelo usuário

- O usuário executou a remoção planejada das aplicações Docker antigas, seus dados, imagens, redes, volumes, diretórios e cache de build.
- Validação informada após a remoção: zero containers, imagens, volumes locais e cache de build.
- Permaneceram somente as redes padrão `bridge`, `host` e `none`.
- A raiz passou de 84% para 10% de uso, com 84 GB disponíveis.
- `/srv/backups` permanece com 1% de uso e 93 GB disponíveis.
- Docker, Nginx e Zabbix Agent 2 foram confirmados como ativos.
- SSH/22, Nginx/80 e Zabbix/10050 continuam escutando; a porta 8123 permanece livre.
- Próximo passo: fechar credenciais e parâmetros pendentes e preparar a implantação controlada do ScreenDeck.

## 2026-10-09 — Decisão preliminar de desativação Docker

- Maker confirmado como banco externo, sem relação com o PostgreSQL local do Cartório.
- Usuário confirmou descarte dos dados de Rifa, Cartório, HML, PRD FEJJB e Jiu-Jitsu System.
- Limpeza do cache de build autorizada em princípio.
- Plano exato documentado em `docs/docker-decommission.md`.
- Imagens, volumes anônimos e diretórios de código ainda exigem confirmação final.
- Nenhuma remoção foi executada.

## 2026-10-09 — Inventário somente leitura do servidor

- Acesso SSH autorizado e encerrado sem alterações.
- Confirmados Ubuntu 24.04.4, Docker 29.4.0, Compose 5.1.3 e porta 8123 livre.
- Encontrados 9 containers: 4 ativos e 5 parados, distribuídos entre Rifa, Cartório, HML e hello-world.
- Encontrados 21 volumes; bancos e uploads foram identificados como dados que exigem decisão específica.
- Raiz está em 84%; cache de build possui 60,13 GB, com 55,04 GB estimados como recuperáveis.
- `/srv/backups` possui 93 GB disponíveis, mas permissões atuais não permitem escrita pelo usuário não-root planejado.
- Nginx e Zabbix rodam fora do Docker e não estão incluídos em qualquer remoção implícita.
- Nenhum container, imagem, volume, cache, serviço ou arquivo foi alterado.

## 2026-10-09 — Endereço do servidor definido

- Servidor Ubuntu informado: `192.168.25.249`.
- URL LAN planejada do Home Assistant: `http://192.168.25.249:8123`.
- Disponibilidade da porta 8123 ainda precisa ser confirmada por inventário somente leitura.
- Usuário informou intenção de remover aplicações Docker existentes.
- Nenhum container ou dado foi alterado; remoção exige inventário e confirmação explícita dos recursos exatos.

## 2026-10-09 — Artefatos locais do kiosk

- Preparados launcher Chromium, autostart Cinnamon, instalador protegido e rollback direcionado.
- URL do Home Assistant é obrigatória por variável e não foi fixada no código.
- Launcher mantém DPMS/saver desativados durante a sessão e reinicia o Chromium após saída inesperada.
- Instalador captura preferências atuais antes de alterar bloqueio, inatividade e desligamento da tela.
- Nenhum artefato foi transferido ou executado no tablet.
- Validação local: sintaxe aprovada e 48 testes aprovados.

## 2026-10-09 — Inventário somente leitura do tablet

- Acesso SSH ao tablet autorizado pelo usuário e limitado a consultas.
- Confirmados Debian 12 i386, Cinnamon/X11, usuário `painel` com autologin e tela `1920x1200` horizontal.
- Chromium não está instalado, mas há pacote i386 nos repositórios Debian configurados.
- Não há autostart persistente do kiosk; o Firefox observado foi iniciado manualmente por SSH.
- A sessão atualmente bloqueia após 15 minutos e desliga a tela em AC após 30 minutos.
- Tablet possui aproximadamente 2 GiB de RAM e 19 GiB livres na raiz.
- Nenhum arquivo, pacote, serviço ou configuração do tablet foi alterado.
- Sessão SSH encerrada após o diagnóstico.

## 2026-10-09 — Agendador resiliente a reinício e falha SMTP

- Slots processados persistem atomicamente e impedem repetição após reinício.
- Estado é limitado aos 512 slots mais recentes.
- Resultado do canal de notificação é armazenado separadamente do backup.
- Falha SMTP é sanitizada e não interrompe o ciclo do agendador.
- Nenhum e-mail ou processo contínuo foi iniciado.
- Validação local: 44 testes aprovados.

## 2026-10-09 — Agendamento e notificações simuladas

- Agenda avaliada no fuso de cada origem e deduplicada por minuto durante a execução do processo.
- Origem desabilitada nunca chama o pipeline.
- Senha ausente gera `configuration_failed`; exceção inesperada gera `internal_failed` com sanitização.
- Falhas solicitam notificação por interface injetável.
- Adaptador SMTP com STARTTLS foi testado somente com cliente falso.
- Laço contínuo existe no código, mas não foi conectado ao entrypoint nem iniciado.
- Validação local: 40 testes aprovados.

## 2026-10-09 — Pipeline transacional simulado

- Dump local, upload criptografado e retenção cloud encadeados.
- Uma execução gera exatamente um registro final de histórico.
- Falhas locais, de upload e de retenção cloud possuem estados distintos.
- Falhas cloud preservam e continuam referenciando o dump local válido.
- Todos os comandos externos permanecem simulados nos testes.
- O relatório final mede a duração do pipeline completo.
- Validação local: 34 testes aprovados.

## 2026-10-09 — Adaptador cloud simulado

- Adaptador rclone criado sem uso de shell e sem execução real nos testes.
- Upload é destinado ao diretório exclusivo da origem no remote configurado.
- Retenção cloud usa 15 dias e permanece limitada ao diretório da origem.
- Saídas de erro passam por sanitização de segredos conhecidos.
- Remote real deverá ser confirmado como tipo `crypt` antes da implantação.
- Aviso sonoro por bell do terminal adicionado para final de etapa ou interação necessária.
- Validação local: 30 testes aprovados.

## 2026-10-09 — Proteção de espaço e retenção local

- Reserva prévia definida como duas vezes o tamanho estimado, com mínimo inicial de 64 MiB.
- Ao alcançar 85% de uso, a seleção remove apenas backups administrados e antigos até projetar 75%.
- O backup mais recente de cada origem é protegido.
- Se 75% não puder ser alcançado sem remover arquivos protegidos, o novo dump é recusado.
- Travas antigas são diagnosticadas, mas nunca removidas automaticamente.
- Validação local: 25 testes aprovados.

## 2026-10-09 — Executor local de dump

- Implementados bloqueio exclusivo por origem, arquivo parcial, validação não vazia e promoção atômica.
- Logs passam por sanitização antes de persistir.
- Cada tentativa publica relatório atual e acrescenta histórico JSONL.
- Execução externa é injetável; os testes usam simulação e não acessam banco ou rede.
- Agendamento, upload, retenção integrada e notificações continuam desabilitados.
- Maker continua com `enabled = false` até substituir o usuário administrativo.
- Validação local: 18 testes aprovados.

## 2026-10-09 — Primeira origem modelada

- Origem `Maker` registrada como PostgreSQL 14, banco `janus`, porta 5433 e tamanho estimado de 15 MB.
- Agenda definida para 00:00, 06:00, 12:00 e 18:00 em `America/Bahia`.
- SSL foi registrado como desabilitado conforme o ambiente informado.
- Senha permanece fora do repositório, referenciada por `BACKUP_MAKER_PASSWORD`.
- Origem mantida com `enabled = false`: o usuário atual `postgres` deve ser substituído por usuário exclusivo de backup antes do uso real.
- Modelo para inclusão de novas origens e validação TOML adicionados.
- Nenhuma conexão com o IP, banco ou servidor foi realizada.

## 2026-10-09 — Fundação local da Fase 1

- Estrutura inicial do repositório criada.
- Proteção de segredos e exemplo de variáveis adicionados.
- Compose declarativo preparado, sem execução.
- Esqueletos versionáveis do Home Assistant e do serviço de backup adicionados.
- Documentação inicial de arquitetura, segurança, inventário, implantação, rollback e operação criada.
- Testes locais de lógica adicionados sem dependências externas.
- Nenhum serviço, container ou acesso SSH foi realizado.

### Próxima etapa

Validar os artefatos locais, corrigir eventuais falhas e fechar a Fase 1. Depois, coletar as pendências funcionais e, mediante autorização específica, executar inventário somente leitura do servidor.
