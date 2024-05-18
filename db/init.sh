mkdir -p /tmp/archive

DB_BIN=`pg_config --bindir`
DB_CONF=`psql -U postgres --no-align --quiet --tuples-only --command='SHOW config_file'`
DB_HBA=`psql -U postgres --no-align --quiet --tuples-only --command='SHOW hba_file'`
DB_DATA=`psql -U postgres --no-align --quiet --tuples-only --command='SHOW data_directory'`


sed -i "s/^#*\(log_replication_commands *= *\).*/\1on/" $DB_CONF
sed -i "s/^#*\(archive_mode *= *\).*/\1on/" $DB_CONF
sed -i "s|^#*\(archive_command *= *\).*|\1'cp %p /tmp/archive/%f'|" $DB_CONF
sed -i "s/^#*\(max_wal_senders *= *\).*/\110/" $DB_CONF
sed -i "s/^#*\(wal_level *= *\).*/\1replica/" $DB_CONF
sed -i "s/^#*\(wal_log_hints *= *\).*/\1on/" $DB_CONF
sed -i "s/^#*\(logging_collector *= *\).*/\1on/" $DB_CONF
sed -i "s|^#*\(log_directory *= *\).*|\1'/var/log/postgresql'|" $DB_CONF
sed -i -e"s/^#log_filename = 'postgresql-\%Y-\%m-\%d_\%H\%M\%S.log'.*$/log_filename = 'postgresql.log'/" $DB_CONF
sed -i "s/#log_line_prefix = '%m \[%p\] '/log_line_prefix = '%m [%p] %q%u@%d '/g" $DB_CONF

psql -c "CREATE USER $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';" 
psql -c "CREATE DATABASE $DB_DATABASE;" 
psql -d $DB_DATABASE -a -f /init.sql 
psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_DATABASE TO $DB_USER;" 
psql -d $DB_DATABASE -c "ALTER TABLE emails OWNER TO $DB_USER;" 
psql -d $DB_DATABASE -c "ALTER TABLE phone_numbers OWNER TO $DB_USER;" 
psql -d test_db -c "GRANT EXECUTE ON FUNCTION pg_current_logfile() TO $DB_USER;" 
psql -d test_db	 -c "GRANT EXECUTE ON FUNCTION pg_read_file(text) TO $DB_USER;"

echo "host replication $DB_REPL_USER 0.0.0.0/0 trust" >> $DB_HBA 
echo "host all $DB_USER bot trust" >> $DB_HBA

/$DB_BIN/pg_ctl restart -D $DB_DATA
