import perguntas_respostas_funcoes as prf


#As stop_words vem com acentos/cedilhas. Aqui eu tiro os caracteres indesejados
stop_words = [prf.limpa_utf8(w) for w in prf.stop_words]

#Importa os dados e os retorna já tratados
perguntasx, respostasx = prf.importa_dados()


