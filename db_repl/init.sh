sleep 5

DB_BIN=`pg_config --bindir`
DB_DATA=`psql -U postgres --no-align --quiet --tuples-only --command='SHOW data_directory'`

/$DB_BIN/pg_ctl stop -D $DB_DATA

sleep 5

rm -rf /var/lib/postgresql/data/*

pg_basebackup -R -h db -U $DB_REPL_USER -D /var/lib/postgresql/data -P
/$DB_BIN/pg_ctl start -D $DB_DATA
