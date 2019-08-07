# Clusterização de Perguntas feitas ao setor GGALI da ANVISA

Foi finalizada a abordagem clássica para fazer clusterização de texto. Foi feito um forte pré-processamento colocando todas as letras como minúsculas, retirando pontuações, retirando stop words etc. Após o pré processamento, um bag of words é gerado e é aplicado o tfidf nesse bag of words. Após isso, fazemos uma redução de dimensionalidade usando o Truncated SVD. Por fim, o algoritmo de clusterização escolhido é o hierarchical clustering.

Os resultados estão dispostos nos arquivos info_cluster.csv e texto_perguntas_por_cluster.csv.

info_cluster.csv: contém o código de cada cluster e o número de perguntas pertencentes a essa cluster.
texto_perguntas_por_cluster.csv: contém o código da cluster, o código da pergunta, a pergunta sem pré-processamento e a pergunta com pré-processamento.
