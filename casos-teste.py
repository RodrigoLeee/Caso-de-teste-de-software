import requests
import shutil
import time
import json

import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3000"

def reset_database():
    """Restaura o banco de dados para seu estado original."""
    try:
        shutil.copyfile("db_backup.json", "db.json")
        # print("Banco de dados restaurado.")
        # Pequena pausa para garantir que o json-server detecte a mudança
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro ao restaurar banco de dados: {e}")

def test_create_professional():
    """Testa a criação de um novo profissional (RF001)."""
    payload = {
        "nome": "João Silva",
        "cargo": "Psicólogo",
        "email": "joao.silva@email.com"
    }
    response = requests.post(f"{BASE_URL}/profissionais", json=payload)
    #print(f"Status code: {response.status_code}, Resposta: {response.text}")
    assert response.status_code == 201, "Falha ao criar profissional"
    print("Teste de criação de profissional passou!")

def test_get_professionals():
    """Testa a listagem de profissionais cadastrados (RF001)."""
    response = requests.get(f"{BASE_URL}/profissionais")
    assert response.status_code == 200, "Falha ao obter lista de profissionais"
    assert isinstance(response.json(), list), "Resposta não é uma lista"
    print("Teste de listagem de profissionais passou!")

def test_update_professional():
    """Testa a atualização de um profissional existente (RF001)."""
    # Primeiro vamos criar um novo profissional para garantir que temos um para atualizar
    create_payload = {
        "nome": "Profissional Teste",
        "cargo": "Cargo Teste",
        "email": "teste@example.com"
    }
    
    create_response = requests.post(f"{BASE_URL}/profissionais", json=create_payload)
    #print(f"Criação para teste de atualização - Status: {create_response.status_code}")
    
    if create_response.status_code != 201:
        print("Falha ao criar profissional para teste de atualização")
        return
    
    # Obtém o ID do profissional recém-criado
    novo_profissional = create_response.json()
    profissional_id = novo_profissional["id"]
    
    # Agora tentamos atualizar este profissional
    update_payload = {
        "nome": "Nome Atualizado",
        "cargo": "Cargo Atualizado",
        "email": "email.atualizado@example.com"
    }
    
    #print(f"Atualizando profissional ID: {profissional_id}")
    
    # Usar PATCH em vez de PUT pode resolver problemas de campos ausentes
    response = requests.patch(f"{BASE_URL}/profissionais/{profissional_id}", json=update_payload)
    #print(f"Status code: {response.status_code}, Resposta: {response.text}")
    
    assert response.status_code == 200, f"Falha ao atualizar profissional. Status: {response.status_code}"
    
    # Verificar se a atualização foi realmente aplicada
    verify_response = requests.get(f"{BASE_URL}/profissionais/{profissional_id}")
    updated_data = verify_response.json()
    
    #print(f"Dados após atualização: {updated_data}")
    
    assert updated_data["nome"] == "Nome Atualizado", "Nome não foi atualizado corretamente"
    print("Teste de atualização de profissional passou!")

def test_delete_professional():
    """Testa a remoção de um profissional (RF001)."""
    # Primeiro vamos criar um novo profissional para garantir que temos um para excluir
    create_payload = {
        "nome": "Profissional para Excluir",
        "cargo": "Cargo Temporário",
        "email": "temporario@example.com"
    }
    
    create_response = requests.post(f"{BASE_URL}/profissionais", json=create_payload)
    #print(f"Criação para teste de exclusão - Status: {create_response.status_code}")
    
    if create_response.status_code != 201:
        print("Falha ao criar profissional para teste de exclusão")
        return
    
    # Obtém o ID do profissional recém-criado
    novo_profissional = create_response.json()
    profissional_id = novo_profissional["id"]
    
    #print(f"Excluindo profissional ID: {profissional_id}")
    response = requests.delete(f"{BASE_URL}/profissionais/{profissional_id}")
    #print(f"Status code: {response.status_code}, Resposta: {response.text}")
    
    assert response.status_code == 200, f"Falha ao excluir profissional. Status: {response.status_code}"
    
    # Verifica se o profissional foi realmente excluído
    verify_response = requests.get(f"{BASE_URL}/profissionais/{profissional_id}")
    #print(f"Verificação pós-exclusão - Status: {verify_response.status_code}")
    
    assert verify_response.status_code == 404, "O profissional não foi excluído corretamente"
    print("Teste de exclusão de profissional passou!")

def test_associate_student_with_professional():
    """Testa a associação de um aluno a um profissional (RF002)."""
    # Cria um novo profissional para o teste
    prof_payload = {
        "nome": "Profissional para Associação",
        "cargo": "Terapeuta",
        "email": "terapeuta@example.com"
    }
    
    prof_response = requests.post(f"{BASE_URL}/profissionais", json=prof_payload)
    #print(f"Criação de profissional para associação - Status: {prof_response.status_code}")
    
    if prof_response.status_code != 201:
        print("Falha ao criar profissional para teste de associação")
        return
    
    # Verifica se existem alunos
    alunos_response = requests.get(f"{BASE_URL}/alunos")
    alunos = alunos_response.json()
    
    if not alunos:
        print("Não há alunos para o teste de associação!")
        return
    
    # Usa o primeiro aluno disponível
    aluno_id = alunos[0]["id"]
    profissional_id = prof_response.json()["id"]
    
    payload = {
        "aluno_id": aluno_id,
        "profissional_id": profissional_id,
        "data_atendimento": "2024-04-01T10:00:00",
        "tipo_atendimento": "Atendimento Pedagógico",
        "tecnologia_assistiva_id": 1
    }
    
    #print(f"Associando aluno ID: {aluno_id} com profissional ID: {profissional_id}")
    response = requests.post(f"{BASE_URL}/atendimentos", json=payload)
    #print(f"Status code: {response.status_code}, Resposta: {response.text}")
    
    assert response.status_code == 201, f"Falha ao associar aluno a profissional. Status: {response.status_code}"
    print("Teste de associação aluno-profissional passou!")

def test_search_students():
    """Testa a busca de alunos cadastrados pelo nome (RF007)."""
    # Primeiro verifica se há alunos e obtém um nome para pesquisar
    alunos_response = requests.get(f"{BASE_URL}/alunos")
    alunos = alunos_response.json()
    
    if not alunos:
        print("Não há alunos para pesquisar!")
        return
    
    # Pega parte do nome do primeiro aluno para garantir que encontrará algo
    nome_busca = alunos[0]["nome"].split()[0]
    
    response = requests.get(f"{BASE_URL}/alunos?nome_like={nome_busca}")
    #print(f"Buscando alunos com nome contendo '{nome_busca}'")
    #print(f"Status code: {response.status_code}, Resposta: {response.text}")
    
    assert response.status_code == 200, "Falha na busca de alunos"
    assert isinstance(response.json(), list), "Resposta não é uma lista"
    print("Teste de busca de alunos passou!")

# Executando os testes
if __name__ == "__main__":
    print("Iniciando testes...")
    reset_database()
    test_create_professional()
    reset_database()
    test_get_professionals()
    reset_database()
    test_update_professional()
    reset_database()
    test_delete_professional()
    reset_database()
    test_associate_student_with_professional()
    reset_database()
    test_search_students()
    reset_database()
    print("Todos os testes concluídos!")