FROM postgres:14-alpine

RUN mkdir -p /var/log/postgresql \
    && chown -R postgres:postgres /var/log/postgresql \
    && chmod -R 755 /var/log/postgresql 

COPY ./init.sh /docker-entrypoint-initdb.d/init.sh

RUN chown postgres /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh
