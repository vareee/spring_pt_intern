FROM postgres:14-alpine

RUN mkdir -p /var/log/postgresql \
    && chown -R postgres:postgres /var/log/postgresql \
    && chmod -R 755 /var/log/postgresql \
    && touch /var/log/postgresql/postgresql.log \
    && chown -R postgres:postgres /var/log/postgresql/postgresql.log \
    && chmod -R 755 /var/log/postgresql/postgresql.log

COPY ./init.sh /docker-entrypoint-initdb.d/init.sh

COPY ./init.sql /init.sql
RUN chmod 777 /init.sql

RUN chown postgres /docker-entrypoint-initdb.d/init.sh
RUN chmod ugo+x /docker-entrypoint-initdb.d/init.sh


