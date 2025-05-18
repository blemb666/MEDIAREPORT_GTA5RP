# GTA5RP Media Report
## Описание
!report {id} {reason} - в чат твича
Отчет отправляется через вебхук в дискорд (only Rainbow)

## Установка через Dockerfile
Dockerfile
```
FROM python
# Аргумент, чтобы избежать кэширования git clone
ARG CACHEBUST=1
# Клонирование репозитория
RUN git clone "https://github.com/blemb666/MEDIAREPORT_GTA5RP.git"
ENV MEDIA_name="?"
ENV token="?" 
ENV id="?"
ENV channel_suspect="?"
ENV webhook_discord="?"
RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir twitchio
WORKDIR /MEDIAREPORT_GTA5RP
CMD ["python3", "main.py"]
```