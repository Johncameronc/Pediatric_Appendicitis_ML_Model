# ... (imports do os, questionary)
from os import system, name
import questionary

# Importa as funções dos outros pacotes
from app.inference import inferir_paciente
from app.patient_intake import novo_paciente

# Importa a função principal do pipeline de treinamento
from training_pipeline.train import executar_pipeline_de_treinamento

def limpar_tela():
    # Para Windows
    if name == 'nt':
        _ = system('cls')
    # Para Mac e Linux
    else:
        _ = system('clear')

def menu_principal():
    while True:
        limpar_tela()
        print("=" * 50)
        print("   Modelo de Predição de Apendicite Pediátrica")
        print("=" * 50)

        # Cria o menu interativo
        escolha = questionary.select(
            "Selecione uma opção:",
            choices=[
                "Treinar modelos",
                "Diagnosticar um novo paciente",
                "Sair"
            ],
            use_indicator=True  # Mostra um '►' na opção atual
        ).ask()

        # Se o usuário escolher "Sair" ou pressionar Ctrl+C
        if escolha is None or escolha == "Sair":
            print("\nEncerrando o programa...")
            break

        # Se o usuário escolher "Diagnosticar"
        if escolha == "Diagnosticar um novo paciente":
            paciente = novo_paciente()  # Chama sua função de coleta de dados

            if paciente is not None:
                # Se a coleta de dados não foi cancelada
                limpar_tela()
                print("=" * 50)
                print("      Resultado da Análise do Paciente")
                print("=" * 50)
                inferir_paciente(paciente)  # Roda a inferência
                print("\n" + "=" * 50)
                input("\nPressione ENTER para voltar ao menu principal...")
            else:
                # Se a coleta foi cancelada no meio
                input("\nColeta de dados cancelada. Pressione ENTER para voltar...")

        if escolha == "Treinar modelos":
            executar_pipeline_de_treinamento()