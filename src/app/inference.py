import csv
from pickle import load
from pathlib import Path
from colorama import init, Fore, Style
from data_pipeline.normalization import desnormalizar_paciente

# Inicializa colorama para terminais Windows
init()

# --- CAMINHOS ROBUSTOS ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "pacientes_inferidos.csv"

# --- DEFINIÇÃO DAS COLUNAS ---

# 1. Lista de colunas que o MODELO espera (com one-hot encoding)
ENCODED_FEATURES_NAMES = [
    'Age','BMI','Height','Weight','Length_of_Stay','Appendix_Diameter','Body_Temperature','WBC_Count',
    'Neutrophil_Percentage','RBC_Count','Hemoglobin','RDW','Thrombocyte_Count','CRP','Alvarado_Score',
    'Paedriatic_Appendicitis_Score','Sex_female','Sex_male','Appendix_on_US_no','Appendix_on_US_yes',
    'Migratory_Pain_no','Migratory_Pain_yes','Lower_Right_Abd_Pain_no','Lower_Right_Abd_Pain_yes',
    'Contralateral_Rebound_Tenderness_no','Contralateral_Rebound_Tenderness_yes','Coughing_Pain_no',
    'Coughing_Pain_yes','Nausea_no','Nausea_yes','Loss_of_Appetite_no','Loss_of_Appetite_yes',
    'Neutrophilia_no','Neutrophilia_yes','Ketones_in_Urine_+','Ketones_in_Urine_++',
    'Ketones_in_Urine_+++','Ketones_in_Urine_no','RBC_in_Urine_+','RBC_in_Urine_++',
    'RBC_in_Urine_+++','RBC_in_Urine_no','WBC_in_Urine_+','WBC_in_Urine_++',
    'WBC_in_Urine_+++','WBC_in_Urine_no','Dysuria_no','Dysuria_yes','Stool_constipation',
    'Stool_constipation, diarrhea','Stool_diarrhea','Stool_normal','Peritonitis_generalized',
    'Peritonitis_local','Peritonitis_no','Psoas_Sign_no','Psoas_Sign_yes',
    'Ipsilateral_Rebound_Tenderness_no','Ipsilateral_Rebound_Tenderness_yes','US_Performed_no',
    'US_Performed_yes','Free_Fluids_no','Free_Fluids_yes'
]

# 2. Lista de colunas originais que queremos MANTER no CSV final
# (Já removemos as colunas desnecessárias que você listou)
ORIGINAL_COLUMNS_TO_KEEP = [
    'Age','BMI','Sex','Height','Weight','Length_of_Stay','Alvarado_Score','Paedriatic_Appendicitis_Score',
    'Appendix_on_US','Appendix_Diameter','Migratory_Pain','Lower_Right_Abd_Pain',
    'Contralateral_Rebound_Tenderness','Coughing_Pain','Nausea','Loss_of_Appetite','Body_Temperature',
    'WBC_Count','Neutrophil_Percentage','Neutrophilia','RBC_Count','Hemoglobin','RDW','Thrombocyte_Count',
    'Ketones_in_Urine','RBC_in_Urine','WBC_in_Urine','CRP','Dysuria','Stool','Peritonitis','Psoas_Sign',
    'Ipsilateral_Rebound_Tenderness','US_Performed','Free_Fluids'
]

# 3. Colunas de resultado da inferência
RESULT_NAMES = ['Diagnosis', 'Severity', 'Management']

# 4. Cabeçalho final do arquivo CSV
FINAL_CSV_HEADERS = ORIGINAL_COLUMNS_TO_KEEP + RESULT_NAMES


def reverter_one_hot_encoding(paciente_encoded_data):
    # Cria um dicionário mapeando o nome da coluna codificada ao seu valor
    dados = dict(zip(ENCODED_FEATURES_NAMES, paciente_encoded_data))
    dados_revertidos = {}

    # Mapeamento para reverter as colunas
    # Estrutura: 'ColunaOriginal': {'prefixo': 'Prefixo_Comum', 'valores': ['valor1', 'valor2']}
    mapa_reversao = {
        'Sex': {'prefixo': 'Sex_', 'valores': ['female', 'male']},
        'Appendix_on_US': {'prefixo': 'Appendix_on_US_', 'valores': ['no', 'yes']},
        'Migratory_Pain': {'prefixo': 'Migratory_Pain_', 'valores': ['no', 'yes']},
        'Lower_Right_Abd_Pain': {'prefixo': 'Lower_Right_Abd_Pain_', 'valores': ['no', 'yes']},
        'Contralateral_Rebound_Tenderness': {'prefixo': 'Contralateral_Rebound_Tenderness_', 'valores': ['no', 'yes']},
        'Coughing_Pain': {'prefixo': 'Coughing_Pain_', 'valores': ['no', 'yes']},
        'Nausea': {'prefixo': 'Nausea_', 'valores': ['no', 'yes']},
        'Loss_of_Appetite': {'prefixo': 'Loss_of_Appetite_', 'valores': ['no', 'yes']},
        'Neutrophilia': {'prefixo': 'Neutrophilia_', 'valores': ['no', 'yes']},
        'Ketones_in_Urine': {'prefixo': 'Ketones_in_Urine_', 'valores': ['+', '++', '+++', 'no']},
        'RBC_in_Urine': {'prefixo': 'RBC_in_Urine_', 'valores': ['+', '++', '+++', 'no']},
        'WBC_in_Urine': {'prefixo': 'WBC_in_Urine_', 'valores': ['+', '++', '+++', 'no']},
        'Dysuria': {'prefixo': 'Dysuria_', 'valores': ['no', 'yes']},
        'Stool': {'prefixo': 'Stool_', 'valores': ['constipation', 'constipation, diarrhea', 'diarrhea', 'normal']},
        'Peritonitis': {'prefixo': 'Peritonitis_', 'valores': ['generalized', 'local', 'no']},
        'Psoas_Sign': {'prefixo': 'Psoas_Sign_', 'valores': ['no', 'yes']},
        'Ipsilateral_Rebound_Tenderness': {'prefixo': 'Ipsilateral_Rebound_Tenderness_', 'valores': ['no', 'yes']},
        'US_Performed': {'prefixo': 'US_Performed_', 'valores': ['no', 'yes']},
        'Free_Fluids': {'prefixo': 'Free_Fluids_', 'valores': ['no', 'yes']},
    }

    # Passa pelas colunas que queremos no CSV final
    for col in ORIGINAL_COLUMNS_TO_KEEP:
        if col in mapa_reversao:
            # Se for uma coluna categórica, encontra o valor original
            info = mapa_reversao[col]
            for valor in info['valores']:
                coluna_codificada = f"{info['prefixo']}{valor}"
                if dados.get(coluna_codificada) == 1:
                    dados_revertidos[col] = valor
                    break
            else: # Caso não encontre um valor (ex: todos 0)
                dados_revertidos[col] = 'N/A'
        else:
            # Se for uma coluna numérica, apenas copia o valor
            dados_revertidos[col] = dados.get(col, 'N/A')
            
    return dados_revertidos


def inferir_target(paciente, target):
    modelo_path = MODELS_DIR / f"pediactric_appendicitis_{target}_model.pkl"
    try:
        with open(modelo_path, "rb") as f:
            return load(f).predict_proba(paciente)
    except FileNotFoundError:
        print(f"{Fore.RED}ERRO: Modelo '{modelo_path.name}' não encontrado!{Style.RESET_ALL}")
        return None

def salvar_inferencia_csv(dados_dict):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        escrever_cabecalho = not CSV_PATH.exists()

        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FINAL_CSV_HEADERS)
            if escrever_cabecalho:
                writer.writeheader()
            writer.writerow(dados_dict)
            
    except IOError as e:
        print(f"{Fore.RED}ERRO AO SALVAR CSV: {e}{Style.RESET_ALL}")

def inferir_paciente(paciente):
    # Reverte os dados do paciente para o formato original para salvamento posterior
    dados_para_salvar = reverter_one_hot_encoding(paciente.iloc[0].values)
    
    # Desnormaliza os dados numéricos
    dados_desnormalizados = desnormalizar_paciente(paciente)
    if dados_desnormalizados is not None:
        for col in dados_desnormalizados.columns:
            dados_para_salvar[col] = dados_desnormalizados[col].iloc[0]

    # --- 1. Diagnóstico ---
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}=========== DIAGNÓSTICO DE APENDICITE ==========={Style.RESET_ALL}")
    diagnostico_proba = inferir_target(paciente, 'Diagnosis')
    if diagnostico_proba is None: return

    prob_apendicite = diagnostico_proba[0][0]
    
    # Adiciona os resultados ao dicionário que será salvo
    dados_para_salvar['Severity'] = 'N/A'
    dados_para_salvar['Management'] = 'N/A'

    if prob_apendicite > 0.5:
        dados_para_salvar['Diagnosis'] = 'appendicitis'
        print(f"{Fore.GREEN}Resultado: {prob_apendicite:.2%} de chance - {dados_para_salvar['Diagnosis']}{Style.RESET_ALL}")

        # --- 2. Gravidade (só se o diagnóstico for positivo) ---
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}=== GRAVIDADE DA APENDICITE ==={Style.RESET_ALL}")
        severity_proba = inferir_target(paciente, 'Severity')
        
        if severity_proba is not None:
            prob_complicada = severity_proba[0][0]
            if prob_complicada > 0.5:
                dados_para_salvar['Severity'] = 'complicated'
                print(f"{Fore.RED}Resultado: {prob_complicada:.2%} de chance - {dados_para_salvar['Severity']}{Style.RESET_ALL}")
            else:
                dados_para_salvar['Severity'] = 'uncomplicated'
                print(f"{Fore.GREEN}Resultado: {(1 - prob_complicada):.2%} de chance - {dados_para_salvar['Severity']}{Style.RESET_ALL}")

        # --- 3. Tratamento (só se o diagnóstico for positivo) ---
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}=== TRATAMENTO RECOMENDADO ==={Style.RESET_ALL}")
        management_proba = inferir_target(paciente, 'Management')
        
        if management_proba is not None:
            prob_conservador = management_proba[0][0]
            if prob_conservador > 0.5:
                dados_para_salvar['Management'] = 'conservative'
                print(f"{Fore.BLUE}Resultado: {prob_conservador:.2%} de chance - {dados_para_salvar['Management']}{Style.RESET_ALL}")
            else:
                dados_para_salvar['Management'] = 'primary surgical'
                print(f"{Fore.MAGENTA}Resultado: {(1 - prob_conservador):.2%} de chance - {dados_para_salvar['Management']}{Style.RESET_ALL}")

    else:
        dados_para_salvar['Diagnosis'] = 'no appendicitis'
        print(f"{Fore.RED}Resultado: {(1 - prob_apendicite):.2%} de chance - {dados_para_salvar['Diagnosis']}{Style.RESET_ALL}")

    # --- Salvamento dos dados ---
    salvar_inferencia_csv(dados_para_salvar)
    print(f"\n{Fore.CYAN}--- Inferência salva em '{CSV_PATH.name}' ---{Style.RESET_ALL}")