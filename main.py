import perguntas_respostas_funcoes as prf


stop_words = [prf.limpa_utf8(w) for w in prf.stop_words]

perguntas, respostas = prf.importa_dados()