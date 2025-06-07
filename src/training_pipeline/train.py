import pandas as pd
from pathlib import Path
from pickle import dump, load

# Importa as funções dos outros pacotes
from data_pipeline.processing import importar_dataset, preprocessar_dados
from data_pipeline.normalization import normalizar_dados
from data_pipeline.balancing import balancear

# Importa as funções para o treinamento do modelo
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_validate

# --- NOVO: Definição de Caminho ---
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

def treinar_modelo_individual(dados, target):
    print(f"\n> Treinando modelo para a coluna target: {target}")

    model_path = MODELS_DIR / f'pediactric_appendicitis_{target}_model.pkl'

    if model_path.exists():
        print(f"Modelo para {target} já existe. Pulando treinamento.")
        return

    # Separar atributos e rótulo
    dados_atributos = dados.drop(columns=[target])
    dados_classes = dados[target]

    # Definir o modelo
    tree = RandomForestClassifier()

    # Definir os parâmetros para busca em grade
    tree_grid = {
        'n_estimators': [100, 200,300],
        'criterion': ['gini', 'entropy'],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'max_features': ['sqrt', 'log2'],
        'random_state': [42],
        'n_jobs': [-1]
    }

    # Configurar a busca em grade
    print(f"> Realizando hiperparametrização")
    tree_hyperparameters = GridSearchCV(estimator=tree, param_grid=tree_grid, cv=5, verbose=1, n_jobs=-1, scoring='accuracy')
    
    # Treinar o modelo
    tree_hyperparameters.fit(dados_atributos, dados_classes)
    
    tree = RandomForestClassifier(**tree_hyperparameters.best_params_)
    scoring_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
    scores_cross = cross_validate(tree, dados_atributos, dados_classes, cv=10, scoring=scoring_metrics)

    print(f'> Modelo treinado com sucesso para a coluna {target}!')

    tree = tree.fit(dados_atributos, dados_classes)

    # Salva o modelo
    dump(tree, open(model_path, "wb"))
    print(f"> Modelo para {target} salvo em {model_path}")


# Esta é a função que o menu vai chamar
def executar_pipeline_de_treinamento():
    print("> Iniciando pipeline de treinamento...")
    dados_raw = importar_dataset()
    dados_processados = preprocessar_dados(dados_raw.copy())
    dados_normalizados = normalizar_dados(dados_processados.copy())
    print("> Dados processados e normalizados.")

    # Treinar modelo 'Diagnosis'
    diagnosis_df = balancear(dados_normalizados.copy(), 'Diagnosis')
    treinar_modelo_individual(diagnosis_df, 'Diagnosis')

    # Treinar modelo 'Severity'
    severity_df = dados_normalizados[dados_normalizados['Diagnosis'] == 'appendicitis'].copy()
    severity_df = balancear(severity_df, 'Severity')
    treinar_modelo_individual(severity_df, 'Severity')

    # Treinar modelo 'Management'
    management_df = dados_normalizados[dados_normalizados['Diagnosis'] == 'appendicitis'].copy()
    management_df = balancear(management_df, 'Management')
    treinar_modelo_individual(management_df, 'Management')
    
    print("> Pipeline de treinamento concluído com sucesso!")