FROM python:3.5-jessie

LABEL "Maintainer"="Alexandre Maldémé" \
        "version"="0.1"


# Add the app in /opt
ADD . /var/www

# Working directory for "CMD"
WORKDIR /var/www

# Set Flask env variables
ENV FLASK_APP=app.py \
    FLASK_DEBUG=1

# By default Flask use port 5000
EXPOSE 5000

# Install Flask via pip,
# Change ownership of app to www-data
RUN pip install -r requirements.txt && \
    chown -R www-data: /var/www

# Adjust permissions on /etc/passwd so writable by group root.
RUN chmod g+w /etc/passwd

# "CMD" will be executed as www-data
USER www-data

ENTRYPOINT["/var/www/entrypoint.sh"]

# Run the app
CMD ["flask", "run", "--host=0.0.0.0"]
