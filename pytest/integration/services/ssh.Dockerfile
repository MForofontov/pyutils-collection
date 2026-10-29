FROM node:22-bookworm-slim
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && mkdir -p /run/sshd \
    && useradd -m -s /bin/sh audit \
    && echo 'audit:pyutils_test_only' | chpasswd \
    && rm -f /etc/ssh/ssh_host_* \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 22
CMD ["sh", "-c", "ssh-keygen -A >/dev/null && exec /usr/sbin/sshd -D -e -o PasswordAuthentication=yes -o UsePAM=no -o PermitRootLogin=no"]
