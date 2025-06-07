import pandas as pd
import questionary
from os import system, name

# Supondo que a função de normalização e outras funções auxiliares estejam disponíveis
from data_pipeline.normalization import normalizar_paciente

# --- Funções Auxiliares ---
def limpar_tela():
    """Limpa a tela do terminal para uma melhor visualização."""
    _ = system('cls' if name == 'nt' else 'clear')

def is_float(text):
    """Função de validação para garantir que a entrada é um número."""
    if text:
        try:
            float(text)
            return True
        except ValueError:
            return "Por favor, insira um número válido."
    return "Este campo não pode ser vazio."

# --- Função Principal de Coleta ---
def coletar_dados_paciente():
    """
    Exibe um menu interativo e estruturado para coletar dados de um novo paciente.
    """
    limpar_tela()
    print("=" * 50)
    print("     Coleta de Dados do Novo Paciente")
    print("=" * 50)
    print("\nInstruções:")
    print(" -> Use as setas (↑, ↓) para navegar e ENTER para selecionar.")
    print(" -> Pressione Ctrl+C a qualquer momento para cancelar.\n")

    dados_paciente = {}

    # --- Definições (Perguntas, Colunas, Opções) ---
    # (O mapa de perguntas e as definições de colunas foram movidos para dentro
    # para melhor organização)

    mapa_de_perguntas = {
        # Dados Básicos
        'Age': 'Qual a idade do paciente?',
        'Sex': 'Qual o sexo do paciente?',
        'Height': 'Qual a altura (em cm)?',
        'Weight': 'Qual o peso (em kg)?',
        'BMI': 'Qual o IMC (Índice de Massa Corporal)?',
        'Length_of_Stay': 'Qual foi o tempo de permanência (em dias)?',
        # Sinais e Sintomas
        'Migratory_Pain': 'Houve dor migratória?',
        'Lower_Right_Abd_Pain': 'Paciente tem dor no abdômen inferior direito?',
        'Contralateral_Rebound_Tenderness': 'Houve sensibilidade contralateral (Blumberg)?',
        'Coughing_Pain': 'Sente dor ao tossir?',
        'Nausea': 'Apresentou náusea?',
        'Loss_of_Appetite': 'Houve perda de apetite?',
        'Body_Temperature': 'Qual a temperatura corporal (em °C)?',
        'Dysuria': 'Apresenta disúria (dor ao urinar)?',
        'Stool': 'Como está o trânsito intestinal (fezes)?',
        'Peritonitis': 'Apresenta sinais de peritonite?',
        'Psoas_Sign': 'O sinal de Psoas é positivo?',
        'Ipsilateral_Rebound_Tenderness': 'Houve sensibilidade ipsilateral?',
        # Scores
        'Alvarado_Score': 'Qual o Escore de Alvarado?',
        'Paedriatic_Appendicitis_Score': 'Qual o Escore Pediátrico de Apendicite (PAS)?',
        # Exames Laboratoriais
        'WBC_Count': 'Qual a contagem de leucócitos (x10^9/L)?',
        'Neutrophil_Percentage': 'Qual a porcentagem de neutrófilos (%)?',
        'Neutrophilia': 'Apresenta neutrofilia?',
        'RBC_Count': 'Qual a contagem de hemácias?',
        'Hemoglobin': 'Qual o nível de hemoglobina (g/dL)?',
        'RDW': 'Qual o valor do RDW (%)?',
        'Thrombocyte_Count': 'Qual a contagem de plaquetas?',
        'Ketones_in_Urine': 'Qual o nível de cetonas na urina?',
        'RBC_in_Urine': 'Qual o nível de hemácias na urina?',
        'WBC_in_Urine': 'Qual o nível de leucócitos na urina?',
        'CRP': 'Qual o valor da Proteína C-Reativa (PCR) (mg/L)?',
        # Ultrassom
        'US_Performed': 'O ultrassom foi realizado?',
        'Appendix_on_US': 'O apêndice foi visível no ultrassom?',
        'Appendix_Diameter': 'Qual o diâmetro do apêndice (em mm)?',
        'Free_Fluids': 'Foram observados fluidos livres no ultrassom?'
    }

    # Estrutura das perguntas por seção
    secoes = {
        "Dados Básicos do Paciente": ['Age', 'Sex', 'Height', 'Weight', 'BMI', 'Length_of_Stay'],
        "Sinais, Sintomas e Scores": ['Migratory_Pain', 'Lower_Right_Abd_Pain', 'Contralateral_Rebound_Tenderness',
                                    'Coughing_Pain', 'Nausea', 'Loss_of_Appetite', 'Body_Temperature', 'Dysuria',
                                    'Stool', 'Peritonitis', 'Psoas_Sign', 'Ipsilateral_Rebound_Tenderness',
                                    'Alvarado_Score', 'Paedriatic_Appendicitis_Score'],
        "Exames Laboratoriais": ['WBC_Count', 'Neutrophil_Percentage', 'Neutrophilia', 'RBC_Count', 'Hemoglobin',
                                'RDW', 'Thrombocyte_Count', 'Ketones_in_Urine', 'RBC_in_Urine', 'WBC_in_Urine', 'CRP']
    }

    # --- Função interna para fazer perguntas e evitar repetição de código ---
    def fazer_pergunta(coluna):
        """Busca a definição da pergunta e coleta a resposta do usuário."""
        pergunta_texto = mapa_de_perguntas.get(coluna)

        # Define tipos e opções
        colunas_numericas = ['Age', 'BMI', 'Height', 'Weight', 'Length_of_Stay', 'Appendix_Diameter',
                             'Body_Temperature', 'WBC_Count', 'Neutrophil_Percentage', 'RBC_Count',
                             'Hemoglobin', 'RDW', 'Thrombocyte_Count', 'CRP']
        
        colunas_categoricas = {
            'Sex': ['Feminino', 'Masculino'],
            'Alvarado_Score': [str(i) for i in range(11)],
            'Paedriatic_Appendicitis_Score': [str(i) for i in range(11)],
            'Migratory_Pain': ['Sim', 'Não'], 'Lower_Right_Abd_Pain': ['Sim', 'Não'],
            'Contralateral_Rebound_Tenderness': ['Sim', 'Não'], 'Coughing_Pain': ['Sim', 'Não'],
            'Nausea': ['Sim', 'Não'], 'Loss_of_Appetite': ['Sim', 'Não'],
            'Neutrophilia': ['Sim', 'Não'], 'Dysuria': ['Sim', 'Não'],
            'Peritonitis': ['Não', 'Localizada', 'Generalizada'], 'Psoas_Sign': ['Sim', 'Não'],
            'Ipsilateral_Rebound_Tenderness': ['Sim', 'Não'], 'US_Performed': ['Sim', 'Não'],
            'Appendix_on_US': ['Sim', 'Não'], 'Free_Fluids': ['Sim', 'Não'],
            'Ketones_in_Urine': ['Não', '+', '++', '+++'], 'RBC_in_Urine': ['Não', '+', '++', '+++'],
            'WBC_in_Urine': ['Não', '+', '++', '+++'],
            'Stool': ['Normal', 'Constipação', 'Diarreia', 'Constipação e Diarreia'],
        }
        
        mapa_respostas_para_ingles = {
            'Feminino': 'female', 'Masculino': 'male', 'Sim': 'yes', 'Não': 'no',
            'Normal': 'normal', 'Constipação': 'constipation', 'Diarreia': 'diarrhea',
            'Constipação e Diarreia': 'constipation, diarrhea', 'Localizada': 'local', 'Generalizada': 'generalized',
        }

        # Coleta a resposta
        if coluna in colunas_numericas:
            resposta = questionary.text(f"{pergunta_texto}:", validate=is_float).ask()
            if resposta is None: raise KeyboardInterrupt
            dados_paciente[coluna] = float(resposta)
        
        elif coluna in colunas_categoricas:
            opcoes = colunas_categoricas[coluna]
            resposta_traduzida = questionary.select(f"{pergunta_texto}", choices=opcoes, use_indicator=True).ask()
            if resposta_traduzida is None: raise KeyboardInterrupt
            
            resposta = mapa_respostas_para_ingles.get(resposta_traduzida, resposta_traduzida)
            
            if "Score" in coluna:
                dados_paciente[coluna] = int(resposta)
            else:
                dados_paciente[coluna] = resposta

    # --- Laço Principal de Coleta por Seções ---
    try:
        for nome_secao, lista_colunas in secoes.items():
            print(f"\n--- {nome_secao} ---\n")
            for coluna in lista_colunas:
                fazer_pergunta(coluna)

        # Seção Condicional do Ultrassom
        print("\n--- Ultrassom ---\n")
        fazer_pergunta('US_Performed')
        
        if dados_paciente['US_Performed'] == 'yes':
            fazer_pergunta('Appendix_on_US')
            fazer_pergunta('Appendix_Diameter')
            fazer_pergunta('Free_Fluids')
        else:
            # Preenche com None se o ultrassom não foi realizado
            dados_paciente['Appendix_on_US'] = None
            dados_paciente['Appendix_Diameter'] = None
            dados_paciente['Free_Fluids'] = None

    except KeyboardInterrupt:
        print("\n\nColeta de dados cancelada pelo usuário.")
        return None
        
    return dados_paciente


def novo_paciente():
    dados_dict = coletar_dados_paciente()
    
    if dados_dict is None:
        return None

    paciente_df = pd.DataFrame([dados_dict])
    
    # A normalização agora é importada do local correto
    paciente_normalizado = normalizar_paciente(paciente_df)
    
    return paciente_normalizado