#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Uso:
  grant-postgresql-backup-permissions.sh \
    --host HOST --database BANCO --admin-user USUARIO [opcoes]

Opcoes:
  --port PORTA          Porta do PostgreSQL (padrao: 5432)
  --backup-role ROLE    Usuario/role de backup (padrao: cyriusBackup)
  --admin-user USUARIO  Administrador ou role com permissao para conceder acessos
  -h, --help            Exibe esta ajuda

A senha administrativa nao e aceita por argumento. Use ~/.pgpass, PGPASSFILE ou
deixe o psql solicita-la interativamente.
EOF
}

host=""
port="5432"
database=""
admin_user=""
backup_role="cyriusBackup"

while (($#)); do
  case "$1" in
    --host) host="${2:-}"; shift 2 ;;
    --port) port="${2:-}"; shift 2 ;;
    --database) database="${2:-}"; shift 2 ;;
    --admin-user) admin_user="${2:-}"; shift 2 ;;
    --backup-role) backup_role="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Erro: opcao desconhecida: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$host" || -z "$database" || -z "$admin_user" || -z "$backup_role" ]]; then
  echo "Erro: --host, --database, --admin-user e --backup-role nao podem ser vazios." >&2
  usage >&2
  exit 2
fi

if [[ ! "$port" =~ ^[0-9]+$ ]] || ((port < 1 || port > 65535)); then
  echo "Erro: porta invalida: $port" >&2
  exit 2
fi

command -v psql >/dev/null 2>&1 || {
  echo "Erro: psql nao encontrado." >&2
  exit 1
}

echo "Concedendo acesso de leitura a '$backup_role' no banco '$database' em '$host:$port'..."

psql \
  --host "$host" \
  --port "$port" \
  --username "$admin_user" \
  --dbname "$database" \
  --variable ON_ERROR_STOP=1 \
  --variable backup_role="$backup_role" <<'SQL'
SELECT set_config('screendeck.backup_role', :'backup_role', false);

DO $block$
DECLARE
  target_role text := current_setting('screendeck.backup_role');
  schema_name text;
  owner_name text;
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = target_role) THEN
    RAISE EXCEPTION 'role de backup % nao existe', target_role;
  END IF;

  EXECUTE format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), target_role);

  FOR schema_name IN
    SELECT nspname
      FROM pg_namespace
     WHERE nspname <> 'information_schema'
       AND nspname NOT LIKE 'pg\_%' ESCAPE '\'
  LOOP
    EXECUTE format('GRANT USAGE ON SCHEMA %I TO %I', schema_name, target_role);
    EXECUTE format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO %I', schema_name, target_role);
    EXECUTE format('GRANT SELECT ON ALL SEQUENCES IN SCHEMA %I TO %I', schema_name, target_role);
  END LOOP;

  -- Default privileges belong to the role that creates each object. Include
  -- owners of current application schemas/objects so later tables and sequences
  -- created by those same roles remain readable by pg_dump.
  FOR owner_name IN
    SELECT DISTINCT role_name
      FROM (
        SELECT pg_get_userbyid(nspowner) AS role_name
          FROM pg_namespace
         WHERE nspname <> 'information_schema'
           AND nspname NOT LIKE 'pg\_%' ESCAPE '\'
        UNION
        SELECT pg_get_userbyid(c.relowner) AS role_name
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname <> 'information_schema'
           AND n.nspname NOT LIKE 'pg\_%' ESCAPE '\'
           AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
      ) owners
     WHERE role_name <> target_role
  LOOP
    EXECUTE format(
      'ALTER DEFAULT PRIVILEGES FOR ROLE %I GRANT SELECT ON TABLES TO %I',
      owner_name, target_role
    );
    EXECUTE format(
      'ALTER DEFAULT PRIVILEGES FOR ROLE %I GRANT SELECT ON SEQUENCES TO %I',
      owner_name, target_role
    );
  END LOOP;
END
$block$;

SELECT n.nspname AS schema,
       count(*) FILTER (
         WHERE c.relkind IN ('r', 'p', 'v', 'm', 'f')
           AND NOT has_table_privilege(
             current_setting('screendeck.backup_role'), c.oid, 'SELECT'
           )
       ) AS objetos_sem_select
  FROM pg_namespace n
  LEFT JOIN pg_class c ON c.relnamespace = n.oid
 WHERE n.nspname <> 'information_schema'
   AND n.nspname NOT LIKE 'pg\_%' ESCAPE '\'
 GROUP BY n.nspname
 ORDER BY n.nspname;
SQL

echo "Permissoes aplicadas. Confirme que 'objetos_sem_select' seja 0 em todos os schemas."
