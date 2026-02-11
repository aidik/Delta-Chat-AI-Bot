FROM python:3.13
WORKDIR /app
COPY requirements.txt requirements.txt
COPY deltabot.py deltabot.py
COPY bot-avatar.jpg bot-avatar.jpg
RUN apt-get update
RUN pip3 install -r requirements.txt

CMD ["sh", "-c", "\
  if [ ! -f /dcconfig/.initialized ]; then \
    python deltabot.py --config-dir /dcconfig  init 'DCACCOUNT:https://nine.testrun.org/new' && \
    python deltabot.py --config-dir /dcconfig config displayname 'AI Delta Bot' && \
    python deltabot.py --config-dir /dcconfig config selfstatus 'Hi, I am AI Delta Bot, ask me something.' && \
    python deltabot.py --config-dir /dcconfig config selfavatar './bot-avatar.jpg' && \
    touch /dcconfig/.initialized; \
  fi && \
  python deltabot.py --config-dir /dcconfig link && python deltabot.py --config-dir /dcconfig serve"]