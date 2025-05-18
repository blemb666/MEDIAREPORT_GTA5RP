# GTA5RP Media Report
[![Anurag's GitHub stats](https://github-readme-stats.vercel.app/api?username=blemb666)](https://github.com/anuraghazra/github-readme-stats)

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