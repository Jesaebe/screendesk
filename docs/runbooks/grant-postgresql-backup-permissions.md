# Permissões de backup em PostgreSQL

Use este procedimento ao cadastrar um banco PostgreSQL novo ou quando o `pg_dump` falhar com `permission denied for table ...`. O script concede ao usuário de backup acesso de conexão, uso dos schemas de aplicação e leitura das tabelas e sequências existentes. Ele também configura privilégios padrão para objetos futuros criados pelos atuais proprietários dos schemas e objetos.

O procedimento não cria o usuário, não altera senhas e não recebe senha pela linha de comando. Execute-o com uma conta administrativa do PostgreSQL ou com uma role autorizada a conceder privilégios em nome dos proprietários encontrados.

## Passo a passo

1. No host que possui o cliente `psql`, torne o script executável, se necessário:

   ```sh
   chmod u+x scripts/grant-postgresql-backup-permissions.sh
   ```

2. Execute-o para cada banco cadastrado. A senha administrativa deve ser fornecida pelo prompt do `psql`, por um `~/.pgpass` protegido ou por `PGPASSFILE`; nunca a coloque no comando:

   ```sh
   scripts/grant-postgresql-backup-permissions.sh \
     --host banco.exemplo.local \
     --port 5432 \
     --database nome_do_banco \
     --admin-user postgres
   ```

   O usuário de backup padrão é `cyriusBackup`. Para outro nome, acrescente `--backup-role nome_da_role`.

3. Confira a tabela exibida ao final. `objetos_sem_select` deve ser `0` em todos os schemas listados. Uma falha em `ALTER DEFAULT PRIVILEGES` indica que a conta administrativa não pode atuar em nome de algum proprietário; nesse caso, execute o procedimento como superusuário do cluster ou peça que o proprietário correspondente conceda os privilégios padrão.

4. No dashboard, use **Testar conexão**. Esse teste confirma credenciais e conectividade, mas não lê todas as tabelas.

5. Faça um dump de validação antes de ativar a origem. No ambiente do serviço, execute o backup controlado conforme o runbook operacional e confirme que não há novo erro de permissão, que o arquivo não está vazio e que o catálogo pode ser lido por `pg_restore --list`.

6. Somente após a validação, ative a origem e acompanhe a primeira execução agendada no histórico do dashboard.

## Quando reaplicar

Reaplique o script ao adicionar um banco ou schema, trocar proprietários ou introduzir uma nova role que crie tabelas/sequências. Os privilégios padrão são associados ao criador do objeto: se uma role nova passar a criar objetos, ela também precisa ser abrangida por uma nova execução.

Schemas criados depois da execução precisam receber `USAGE`; por isso, reaplique o procedimento após criar um schema novo. Schemas internos (`pg_*` e `information_schema`) são deliberadamente ignorados.

Para MySQL/MariaDB, este script não se aplica. Use uma conta administrativa desse servidor para conceder, no mínimo, leitura no banco específico e valide com `mariadb-dump` antes de ativar a origem.
