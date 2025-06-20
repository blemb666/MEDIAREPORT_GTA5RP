# GTA5RP Media Report
## Описание
!report {id} {reason} - в чат твича
Отчет отправляется через вебхук в дискорд (only Rainbow)

## Установка через Dockerfile
Dockerfile
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git clone "https://github.com/blemb666/MEDIAREPORT_GTA5RP.git"
ENV MEDIA_name="?"
ENV token="?"
client_id=p063h8nr6c7i7w8zcn96489x6e26pv&redirect_uri=http://localhost&response_type=token&scope=clips:edit%20channel:moderate%20chat:edit%20chat:read%20moderation:read%20moderator:manage:announcements%20user:edit%20user:read:email%20user:read:follows%20channel:manage:broadcast%20channel:manage:videos
ENV id="?"
ENV channel_suspect="?"
ENV webhook_discord="?"
RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir twitchio
WORKDIR /MEDIAREPORT_GTA5RP
CMD ["python3", "main.py"]
```
