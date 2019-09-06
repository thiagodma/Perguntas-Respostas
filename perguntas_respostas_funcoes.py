import pandas as pd
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import re, unicodedata, time, itertools, nltk
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from stop_words import get_stop_words
from wordcloud import WordCloud
#nltk.download('stopwords')
#nltk.download('rslp')
#==============================================================================
#Definindo algumas variáveis úteis

#todas as combinacoes possíveis para palavras que indicam comeco de resposta sem ser do E-SIC
words = ['atencao','resposta','relacao','atendimento','contato','solicitacao','questionamento','consulta','preenchimento','questionamentos']
c = [list(t) for t in itertools.combinations(words,2)]
d = [' '.join(comb) for comb in c]
combinacoes = '|'.join(d)
#==============================================================================

#Pega stop_words e as trata para ficarem no formato correto
def define_stop_words():

    stop_words = get_stop_words('portuguese')
    stop_words = stop_words + nltk.corpus.stopwords.words('portuguese')
    stop_words = stop_words + ['art','dou','secao','pag','pagina', 'in', 'inc', 'obs', 'sob', 'ltda']
    stop_words = stop_words + ['ndash', 'mdash', 'lsquo','rsquo','ldquo','rdquo','bull','hellip','prime','lsaquo','rsaquo','frasl', 'ordm']
    stop_words = stop_words + ['prezado', 'prezados', 'prezada', 'prezadas', 'gereg', 'ggali','usuario', 'usuaria', 'deseja','gostaria', 'boa tarde', 'bom dia', 'boa noite']
    stop_words = list(dict.fromkeys(stop_words))
    stop_words = ' '.join(stop_words)
    #As stop_words vem com acentos/cedilhas. Aqui eu tiro os caracteres indesejados
    stop_words = limpa_utf8(stop_words)

    return stop_words

def importa_dados(stop_words):

    print('\nComeçou a importação dos dados.')

    #primeiramente importa os dados de forma bruta
    df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
    df = df[['Pergunta','Histórico']]
    perguntas = df['Pergunta'].values.tolist()
    respostas = df['Histórico'].values.tolist()

    t = time.time()
    perguntas_out = [trata_perguntas(pergunta, stop_words) for pergunta in perguntas]
    elpsd = time.time() - t
    print('Tempo para processar as perguntas: ' + str(elpsd))

    t = time.time()
    respostas_out = []
    respostas_out = [trata_respostas(resposta, stop_words) for resposta in respostas]
    elpsd = time.time() - t
    print('Tempo para processar as respostas: ' + str(elpsd) + '\n')

    return perguntas_out, respostas_out, perguntas, respostas

#Coloca as perguntas no melhor formato para convertê-las para um BOW
def trata_perguntas(texto, stop_words):

    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(' +', ' ', texto_lower)

    #tira sites
    texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_lower)

    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_sem_sites)

    #Retira numeros romanos e stopwords
    texto_sem_acento_pontuacao = texto_sem_acento_pontuacao.split()
    texto_sem_stopwords = [roman2num(palavra,stop_words) for palavra in texto_sem_acento_pontuacao]
    texto_sem_stopwords = ' '.join(texto_sem_stopwords)

    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_stopwords)

    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)

    #Remove pontuacao e digitos
    texto_sem_pontuacao_digitos = re.sub('[^A-Za-z]', ' ' , texto_sem_espacamentos)

    #Tira o cabecalho das perguntas "Dados do remetente"
    m = re.search(r'(.*descricao\s+procedimento)?(.*)', texto_sem_pontuacao_digitos)
    texto_sem_cabecalho_dados_remetente = m.group(2)


    #Tira o cabeçalho das perguntas com E-SIC
    m = re.search(r'(sistema\s+e\s+sic.*estabelecido\s+cgu)?(.*)', texto_sem_cabecalho_dados_remetente)
    texto_sem_cabecalho_esic = m.group(2)
    texto_sem_cabecalho = texto_sem_cabecalho_esic

    #Tira o cabecalho Empresa: CNPJ:
    m = re.search(r'(^\s*empresa.*?cnpj)?(.*)', texto_sem_cabecalho_esic)
    texto_sem_cabecalho = m.group(2)

    #Tira despedida/finalização da pergunta
    m = re.search(r'(.*?)(cordialmente|obrigad|atenciosamente|desde\s+agradeco|att|dados\s*empresa.*cnpj|razao\s*social|grata|grato|$)', texto_sem_cabecalho)
    #m = re.search(r'(.*?)(cordialmente|obrigad|atenciosamente|desde\s+agradeco|att|dados\s*empresa.*cnpj|grata|grato|$)', texto_sem_cabecalho)
    texto_sem_despedida = m.group(1)

    #Retira stopwords que possam ter reaparecido e numeros romanos
    #stop_words = stop_words + ' cnpj'
    texto_sem_despedida = texto_sem_despedida.split()
    texto_limpo = [roman2num(palavra, stop_words) for palavra in texto_sem_despedida]

    texto_limpo = ' '.join(texto_limpo)

    #Remove dígitos
    texto_limpo = re.sub(r'\d','', texto_limpo)

    #Remove espaços extras
    texto_limpo = re.sub(' +', ' ', texto_limpo)

    if len(texto_limpo) <= 29:
        return 'pergunta ou resposta fora de padrao ou nao finalizada'
    else:
        return texto_limpo

#Coloca as respostas no melhor formato para convertê-las para um BOW. Retorna os índices das respostas que não estão finalizadas
def trata_respostas(texto,stop_words):

    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(' +', ' ', texto_lower)

    isEsic = re.search('e-sic',texto_lower) != None

    if(not isEsic):
        #retira todo o lixo antes de começar a resposta (not e-sic)
        texto_sem_cabecalho = texto_lower
        while True:
            m = re.search(r'(data/hora: \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})(.*)', texto_sem_cabecalho)
            if m==None: break
            texto_sem_cabecalho = m.group(2)
    else:
        count = 0
        texto_sem_cabecalho = texto_lower
        while True:
            #retira todo o lixo antes de começar a resposta (e-sic)
            m = re.search(r'(acesso\s+concedido)(.*)',texto_sem_cabecalho)
            if (m==None) and (count==0): return 'não há resposta para essa pergunta'
            if m==None: break
            texto_sem_cabecalho = m.group(2)
            count = count+1    

    return texto_sem_cabecalho




#Coloca as respostas no melhor formato para convertê-las para um BOW. Essa função é específica para as perguntas com E-SIC
def trata_respostas_2(texto, stop_words):

    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(' +', ' ', texto_lower)

    #tira sites
    texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_lower)

    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_sem_sites)

    #Retira stopwords que possam ter reaparecido e numeros romanos
    texto_sem_acento_pontuacao = texto_sem_acento_pontuacao.split()
    texto_sem_stopwords = [roman2num(palavra, stop_words) for palavra in texto_sem_acento_pontuacao if palavra not in stop_words]
    texto_sem_stopwords = ' '.join(texto_sem_stopwords)

    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_stopwords)

    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)

    #Remove dígitos
    texto_sem_digitos = re.sub(r'\d','', texto_sem_espacamentos)

    #Remove pontuacao
    texto_sem_pontuacao = re.sub('[^A-Za-z]', ' ' , texto_sem_digitos)

    #Remove espaços extras
    texto_sem_espacos_extras = re.sub(' +', ' ', texto_sem_pontuacao)

    #Pega apenas a resposta final (nem sempre o padrao eh bonitinho)
    firstRegex = '(acesso concedido|informacao inexistente) (.+?) (responsavel|$)'
    secondRegex = r'(' + combinacoes + ') (.+)'
    m = re.search(firstRegex, texto_sem_espacos_extras)

    if m is not None:
        while m is not None:
            texto_so_resposta_final = m.group(2)
            m = re.search(secondRegex, m.group(2))
    else:
        return 'pergunta ou resposta fora de padrao ou nao finalizada'

    #Retira stopwords que possam ter reaparecido e numeros romanos
    texto_so_resposta_final = texto_so_resposta_final.split()
    texto_limpo = [roman2num(palavra, stop_words) for palavra in texto_so_resposta_final if palavra not in stop_words]
    texto_limpo = ' '.join(texto_limpo)

    #Remove dígitos
    texto_limpo = re.sub(r'\d','', texto_limpo)

    #Remove espaços extras
    texto_limpo = re.sub(' +', ' ', texto_limpo)

    return texto_limpo



# Recodificacao em utf8, removendo cedilhas acentos e coisas de latin
def limpa_utf8(texto):

    texto = texto.split()
    texto_tratado = []
    for palavra in texto:
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        texto_tratado.append(palavra_sem_acento)

    return ' '.join(texto_tratado)


def roman2num(roman, stop_words, values={'m': 1000, 'd': 500, 'c': 100, 'l': 50,
                                'x': 10, 'v': 5, 'i': 1}):
    roman = limpa_utf8(roman)

    #remove stopwords
    if roman in stop_words:
        return ''


    #como eu vou tirar numeros de qualquer forma, posso simplesmente retornar um numero
    if(len(roman) < 2 ):
        return str(1)

    if (roman == ''): return ''
    out = re.sub('[^mdclxvi]', '', roman)
    if (len(out) != len(roman)):
        return roman

    numbers = []
    for char in roman:
        numbers.append(values[char])
    total = 0
    if(len(numbers) > 1):
        for num1, num2 in zip(numbers, numbers[1:]):
            if num1 >= num2:
                total += num1
            else:
                total -= num1
        return str(total + num2)
    else:
        return str(numbers[0])

#Reduz a dimensionalidade dos dados
def SVD(dim,base_tfidf):
    print('Começou a redução de dimensionalidade.')
    t = time.time()
    svd = TruncatedSVD(n_components = dim, random_state = 42)
    base_tfidf_reduced = svd.fit_transform(base_tfidf)
    print('Número de dimensoes de entrada: ' + str(base_tfidf.shape[1]))
    print(str(dim) + ' dimensões explicam ' + str(svd.explained_variance_ratio_.sum()) + ' da variância.')
    elpsd = time.time() - t
    print('Tempo para fazer a redução de dimensionalidade: ' + str(elpsd) + '\n')
    return base_tfidf_reduced


#Visualiza as cluster definidas pelo algoritmo. Além disso também retorna o número
#de normas por cluster.
def analisa_clusters(base_tfidf, id_clusters):

    clusters = np.unique(id_clusters)

    #inicializa o output da funcao
    n_normas = np.zeros(len(clusters)) #numero de normas pertencentes a uma cluster

    #reduz a dimensionalidade para 2 dimensoes
    base_tfidf_reduced = SVD(2,base_tfidf)
    X = base_tfidf_reduced[:,0]
    Y = base_tfidf_reduced[:,1]

    colors = cm.rainbow(np.linspace(0, 1, len(n_normas)))

    for cluster, color in zip(clusters, colors):
        idxs = np.where(id_clusters == cluster) #a primeira cluster não é a 0 e sim a 1
        n_normas[cluster-1] = len(idxs[0])
        x = X[idxs[0]]
        y = Y[idxs[0]]
        plt.scatter(x, y, color=color)

    return n_normas

#Faz os stemming nas palavras utilizando o pacote NLTK com o RSLP Portuguese stemmer
def stem(resolucoes):

    print('Comecou a fazer o stemming.')
    t = time.time()
    #Inicializo a lista que será o retorno da funcao
    res = []

    #inicializando o objeto stemmer
    stemmer = nltk.stem.RSLPStemmer()

    for resolucao in resolucoes:
        #Faz o stemming para cada palavra na resolucao
        palavras_stemmed_resolucao = [stemmer.stem(word) for word in resolucao.split()]
        #Faz o append da resolucao que passou pelo stemming
        res.append(" ".join(palavras_stemmed_resolucao))

    print('Tempo para fazer o stemming: ' + str(time.time() - t) + '\n')

    return res


def mostra_conteudo_clusters(cluster,n_amostras,perguntas,respostas):
    df = pd.read_csv('texto_perguntas_por_cluster.csv', sep='|')
    a = df[df['cluster_id'] == cluster]

    if a.shape[0] >= n_amostras: mostra = a.sample(n_amostras,random_state = 42)
    else : mostra = a

    fo = open(r'conteudo_cluster'+str(cluster)+'_n_'+str(a.shape[0])+'.txt', 'w+')

    for i in range(mostra.shape[0]):
        if mostra.iloc[i,1][0] == 'P':
            fo.writelines(mostra.iloc[i,1][:] + '\n')
            fo.writelines(perguntas[int(mostra.iloc[i,1][1:])])
            fo.write('\n\n')
        else:
            fo.writelines(mostra.iloc[i,1][:] + '\n')
            fo.writelines(respostas[int(mostra.iloc[i,1][1:])])
            fo.write('\n\n')

    fo.close()

def generate_wordcloud(cluster, stop_words):
    '''
    Gera uma nuvem de palavras de uma cluster 'cluster'.
    '''

    #importa o csv que tem a informação das clusters
    df = pd.read_csv('texto_perguntas_por_cluster.csv', sep='|')
    a = df[df['cluster_id'] == cluster]

    L = list(a.iloc[:,3])
    text = '\n'.join(L)


    wordcloud = WordCloud(stopwords=stop_words.split()+['laboratorio','laboratorios','rdc']).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def mostra_palavras_relevantes(cluster, perguntasx, n_palavras):

    #importa o csv que tem a informação das clusters
    df = pd.read_csv('texto_perguntas_por_cluster.csv', sep='|')
    a = df[df['cluster_id'] == cluster]

    #importa as perguntas pertencentes à cluster
    textos=[]
    for i in range(a.shape[0]):
        textos.append(perguntasx[int(a.iloc[i,1][1:])])

    #vetoriza para contar facilmente quantas vezes cada palavra aparece
    vec = CountVectorizer()
    bag_palavras = vec.fit_transform(textos)
    feature_names = vec.get_feature_names()

    #Se apareceu apenas uma vez em uma pergunta já e suficiente
    bag_palavras[bag_palavras>1] = 1

    #Computa o número de vezes que cada palavra apareceu
    count = bag_palavras.sum(axis=0)

    #inicializa a variável de retorno
    palavras_relevantes=[]

    #Coloca na variável de saída as palavras mais relevantes com a respectiva contagem
    for i in range(n_palavras):
       idx = count.argmax()
       palavras_relevantes.append(feature_names[idx] + '-' + str(count[0,idx]))
       count[0,idx] = -1

    return ' '.join(palavras_relevantes)


def generate_csvs_for_powerbi(analise, Z, perguntas, perguntasx):

    clusters = [i for i in range(1,len(analise)+1)]

    #Prepara a tabela que indica o número de perguntas por cluster
    d={'cluster_id':clusters,'numero_de_perguntas':analise}
    df = pd.DataFrame(d)
    #exporta a tabela para um csv
    df.to_csv('info_cluster.csv',sep='|',index=False,encoding='utf-8')

    #adiciona as keywords de cada cluster no csv
    palavras_relevantes = [mostra_palavras_relevantes(cluster,perguntasx,10) for cluster in clusters]
    df['Keywords'] = 'default'
    for i in range(len(clusters)):
        df.iloc[i,2] = palavras_relevantes[i]
    df.to_csv('info_cluster.csv',sep='|',index=False,encoding='utf-8')

    #Prepara a tabela que tem a pergunta, o indentificador da pergunta
    #e a qual cluster a pergunta pertence
    Z['pergunta_sem_processamento'] = 'default'
    Z['pergunta_com_processamento'] = 'default'
    for i in range(Z.shape[0]):
        idx = int(Z.iloc[i,1][1:])
        #Adiciona a pergunta sem processamento na coluna correspondente
        Z.iloc[i,2] = perguntas[idx]
        #Adiciona a pergunta com processamento na coluna correspondente
        Z.iloc[i,3] = perguntasx[idx]

    Z.to_csv('texto_perguntas_por_cluster.csv',sep='|',index=False,encoding='utf-8')
