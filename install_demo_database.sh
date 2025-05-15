# Use the official PostgreSQL image
FROM postgres:latest

# Set environment variables (make sure the correct variables are set)
ENV POSTGRES_DB=ghdemo44
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=gnusolidario

# Copy the custom script and the database dump into the container
COPY install_demo_database.sh /docker-entrypoint-initdb.d/install_demo_database.sh
COPY gnuhealth-44-demo.sql.gz /docker-entrypoint-initdb.d/gnuhealth-44-demo.sql.gz

# Give execute permissions to the script
RUN chmod +x /docker-entrypoint-initdb.d/install_demo_database.sh

# Expose port 5432 for PostgreSQL
EXPOSE 5432
