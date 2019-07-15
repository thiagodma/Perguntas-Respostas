import pandas as pd
import re, unicodedata
from stop_words import get_stop_words

#==============================================================================
#Definindo algumas variáveis úteis

# stop-words provisorio
stop_words = get_stop_words('portuguese') + ['','art','dou','secao','pag','pagina', 'in', 'inc', ]

#==============================================================================

def importa_dados():
    #primeiramente importa os dados de forma bruta
    df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
    df = df[['Pergunta','Histórico']]
    perguntas = df['Pergunta'].values.tolist()
    respostas = df['Histórico'].values.tolist()
    
    perguntas = [trata_textos(pergunta) for pergunta in perguntas]
    
    
    return perguntas, respostas

def trata_textos(texto):
    
    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    
    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_lower)
    
    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)
    
    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)
    
    #Remove espaços extras
    texto_sem_espacos_extras = re.sub(' +', ' ', texto_sem_espacamentos)
    
    #tira o cabeçalho inicial da pergunta
    #texto_sem_cabecalho = re.sub(r'^empresa')
    
    return texto_sem_espacamentos


# Recodificacao em utf8, removendo cedilhas acentos e coisas de latin
def limpa_utf8(palavra):    

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressao regular para retornar a palavra apenas com numeros, letras e espaco
    #return re.sub('[^a-zA-Z/ \\\]', '', palavraSemAcento)
    palavraSemHifen = re.sub('[-\/]', ' ', palavraSemAcento)
    return re.sub('[^a-zA-Z0-9 ]', ' ', palavraSemHifen).strip()