import perguntas_respostas_funcoes as prf


stop_words = [prf.limpa_utf8(w) for w in prf.stop_words]

perguntasx, respostasx = prf.importa_dados()
