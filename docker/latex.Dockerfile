FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends latexmk texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-lang-spanish fonts-lmodern && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends lmodern python3 python3-reportlab && rm -rf /var/lib/apt/lists/*
WORKDIR /work
