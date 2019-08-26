from classic_clustering import *

class Perguntas(ClassicClustering):

    def __init__(self):
        ClassicClustering.__init__(self)

    def importa_textos(self):
        print('\nComeçou a importação dos textos.')

        #primeiramente importa os dados de forma bruta
        df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
        df = df[['Pergunta','Histórico']]
        self.textos = df['Pergunta'].values.tolist()

        t = time.time()
        self.textos_tratados = [self.trata_textos(pergunta) for pergunta in self.textos]
        self.textos_id = ['P' + str(i) for i in range(len(self.textos_tratados))]
        elpsd = time.time() - t
        print('Tempo para processar os textos: ' + str(elpsd))

    def trata_textos(self, texto):

        #converte todos caracteres para letra minúscula
        texto_lower = texto.lower()
        texto_lower = re.sub(' +', ' ', texto_lower)

        #tira sites
        texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_lower)

        #Remove acentos e pontuação
        texto_sem_acento_pontuacao = self.limpa_utf8(texto_sem_sites)

        #Retira numeros romanos e stopwords
        texto_sem_acento_pontuacao = texto_sem_acento_pontuacao.split()
        texto_sem_stopwords = [self.tira_stopwords_e_romanos(palavra) for palavra in texto_sem_acento_pontuacao]
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
        texto_limpo = [self.tira_stopwords_e_romanos(palavra) for palavra in texto_sem_despedida]

        texto_limpo = ' '.join(texto_limpo)

        #Remove dígitos
        texto_limpo = re.sub(r'\d','', texto_limpo)

        #Remove espaços extras
        texto_limpo = re.sub(' +', ' ', texto_limpo)

        if len(texto_limpo) <= 29:
            return 'pergunta ou resposta fora de padrao ou nao finalizada'
        else:
            return texto_limpo


    def generate_csvs(self, info_cluster, id_clusters):

        #cria o arquivo info_cluster_perguntas.csv
        info_cluster.to_csv('info_cluster_perguntas.csv', sep='|', index=False, encoding='utf-8')
        lista_textos_por_cluster_perguntas = list(zip(self.textos_id, id_clusters, self.textos, self.textos_tratados))
        #cria o arquivo textos_por_cluster_perguntas.csv
        textos_por_cluster_perguntas = pd.DataFrame(lista_textos_por_cluster_perguntas,
                                       columns=['textos_id','cluster_id','texto','texto_tratado'])
        textos_por_cluster_perguntas.to_csv('textos_por_cluster_perguntas.csv', sep='|', index=False, encoding='utf-8')

class Respostas(ClassicClustering):

    def __init__(self):
        ClassicClustering.__init__(self)

    def importa_textos(self):

        print('\nComeçou a importação dos textos.')

        #primeiramente importa os dados de forma bruta
        df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
        df = df[['Pergunta','Histórico']]
        self.textos = df['Histórico'].values.tolist()

        t = time.time()
        self.textos_tratados = [self.trata_textos(resposta) for resposta in self.textos]
        self.textos_id = ['R' + str(i) for i in range(len(self.textos_tratados))]
        elpsd = time.time() - t
        print('Tempo para processar os textos: ' + str(elpsd))

    def trata_textos(self, texto):

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
            #retira todo o lixo antes de começar a resposta (e-sic)
            m = re.search(r'(acesso\s+concedido)(.*)',texto_lower)
            if m==None: return 'não há resposta para essa pergunta'
            texto_sem_cabecalho = m.group(2)

        #tira a saudacao (all)
        texto_sem_saudacao = re.sub(r'prezado\s+\(a\)\s+senhor\s+\(a\),.*?,','',texto_sem_cabecalho)

        #retira a despedida (not e-sic)
        texto_sem_despedida = re.sub(r'por\s+favor,\s+avalie\s+a\s+resposta.*','',texto_sem_saudacao)

        #retira a despedida (e-sic)
        if(isEsic):
            texto_sem_despedida = re.sub(r'responsável:.*','',texto_sem_despedida)

        #remove despedida geral
        texto_sem_despedida = re.sub(r'atenciosamente.*','',texto_sem_despedida)

        #tira sites
        texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_sem_despedida)

        #Remove acentos e pontuação
        texto_sem_acento_pontuacao = self.limpa_utf8(texto_sem_sites)

        #Remove hifens e barras
        texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)

        #Troca qualquer tipo de espacamento por espaço
        texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)

        #Remove pontuacao e digitos
        texto_sem_pontuacao_digitos = re.sub('[^A-Za-z]', ' ' , texto_sem_espacamentos)

        #Retira numeros romanos e stopwords
        texto_sem_pontuacao_digitos = texto_sem_pontuacao_digitos.split()
        texto_sem_stopwords = [self.tira_stopwords_e_romanos(palavra) for palavra in texto_sem_pontuacao_digitos]
        texto_sem_stopwords = ' '.join(texto_sem_stopwords)

        texto_limpo = re.sub(' +', ' ', texto_sem_stopwords)

        return texto_limpo

    def generate_csvs(self, info_cluster, id_clusters):

        #cria o arquivo info_cluster_respostas.csv
        info_cluster.to_csv('info_cluster_respostas.csv', sep='|', index=False, encoding='utf-8')
        lista_textos_por_cluster_respostas = list(zip(self.textos_id, id_clusters, self.textos, self.textos_tratados))
        #cria o arquivo textos_por_cluster_perguntas.csv
        textos_por_cluster_respostas = pd.DataFrame(lista_textos_por_cluster_respostas,
                                       columns=['textos_id','cluster_id','texto','texto_tratado'])
        textos_por_cluster_respostas.to_csv('textos_por_cluster_respostas.csv', sep='|', index=False, encoding='utf-8')
