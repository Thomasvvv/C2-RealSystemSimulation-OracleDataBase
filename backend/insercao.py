from db_conn import connect, close
from datetime import datetime

def seed_database():
    """Insere dados iniciais no banco de dados MongoDB"""
    try:
        db = connect()
        print("🔌 Conectado ao MongoDB")
        
        # Limpar dados existentes (opcional - comente se não quiser limpar)
        print("\n🗑️  Limpando dados existentes...")
        db.cursos.delete_many({})
        db.professores.delete_many({})
        db.materias.delete_many({})
        db.alunos.delete_many({})
        db.ofertas.delete_many({})
        db.grade_alunos.delete_many({})
        db.counters.delete_many({})
        print("✅ Dados existentes removidos")
        
        # ========================================
        # CURSOS
        # ========================================
        print("\n📚 Inserindo cursos...")
        cursos = [
            {"id": 1, "nome": "Ciência da Computação", "carga_horaria_total": 3200},
            {"id": 2, "nome": "Medicina", "carga_horaria_total": 7200},
            {"id": 3, "nome": "Direito", "carga_horaria_total": 3700},
            {"id": 4, "nome": "Engenharia Civil", "carga_horaria_total": 3600},
            {"id": 5, "nome": "Psicologia", "carga_horaria_total": 4000},
            {"id": 6, "nome": "Administração", "carga_horaria_total": 3000},
            {"id": 7, "nome": "Arquitetura e Urbanismo", "carga_horaria_total": 3600},
            {"id": 8, "nome": "Engenharia Elétrica", "carga_horaria_total": 3600},
            {"id": 9, "nome": "Enfermagem", "carga_horaria_total": 4000},
            {"id": 10, "nome": "Pedagogia", "carga_horaria_total": 3200}
        ]
        db.cursos.insert_many(cursos)
        print(f"✅ {len(cursos)} cursos inseridos")
        
        # ========================================
        # PROFESSORES
        # ========================================
        print("\n👨‍🏫 Inserindo professores...")
        professores = [
            {"id_professor": 1, "nome": "Dr. Carlos Silva", "cpf": "12345678901", "email": "carlos.silva@universidade.edu.br", "data_nasc": datetime(1975, 5, 10), "telefone": "11912345601", "status": "Ativo"},
            {"id_professor": 2, "nome": "Dra. Ana Paula Santos", "cpf": "23456789012", "email": "ana.santos@universidade.edu.br", "data_nasc": datetime(1980, 3, 22), "telefone": "11912345602", "status": "Ativo"},
            {"id_professor": 3, "nome": "Me. Roberto Oliveira", "cpf": "34567890123", "email": "roberto.oliveira@universidade.edu.br", "data_nasc": datetime(1978, 11, 15), "telefone": "11912345603", "status": "Ativo"},
            {"id_professor": 4, "nome": "Dra. Fernanda Costa", "cpf": "45678901234", "email": "fernanda.costa@universidade.edu.br", "data_nasc": datetime(1982, 7, 8), "telefone": "11912345604", "status": "Ativo"},
            {"id_professor": 5, "nome": "Me. Lucas Ferreira", "cpf": "56789012345", "email": "lucas.ferreira@universidade.edu.br", "data_nasc": datetime(1985, 9, 30), "telefone": "11912345605", "status": "Ativo"},
            {"id_professor": 6, "nome": "Dr. Pedro Almeida", "cpf": "67890123456", "email": "pedro.almeida@universidade.edu.br", "data_nasc": datetime(1976, 2, 14), "telefone": "11912345606", "status": "Ativo"},
            {"id_professor": 7, "nome": "Dra. Juliana Rocha", "cpf": "78901234567", "email": "juliana.rocha@universidade.edu.br", "data_nasc": datetime(1983, 6, 25), "telefone": "11912345607", "status": "Ativo"},
            {"id_professor": 8, "nome": "Me. Rafael Lima", "cpf": "89012345678", "email": "rafael.lima@universidade.edu.br", "data_nasc": datetime(1988, 12, 3), "telefone": "11912345608", "status": "Ativo"},
            {"id_professor": 9, "nome": "Dra. Mariana Souza", "cpf": "90123456789", "email": "mariana.souza@universidade.edu.br", "data_nasc": datetime(1981, 4, 18), "telefone": "11912345609", "status": "Ativo"},
            {"id_professor": 10, "nome": "Me. Bruno Martins", "cpf": "01234567890", "email": "bruno.martins@universidade.edu.br", "data_nasc": datetime(1986, 10, 12), "telefone": "11912345610", "status": "Inativo"}
        ]
        db.professores.insert_many(professores)
        print(f"✅ {len(professores)} professores inseridos")
        
        # ========================================
        # MATÉRIAS
        # ========================================
        print("\n📖 Inserindo matérias...")
        materias = [
            {"id_materia": 1, "id_curso": 1, "nome": "Algoritmos e Estruturas de Dados", "periodo": 2, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 2, "id_curso": 1, "nome": "Programação Orientada a Objetos", "periodo": 3, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 3, "id_curso": 1, "nome": "Banco de Dados I", "periodo": 4, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 4, "id_curso": 1, "nome": "Engenharia de Software", "periodo": 5, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 5, "id_curso": 1, "nome": "Inteligência Artificial", "periodo": 7, "carga_horaria": 80, "tipo": "Optativa"},
            {"id_materia": 1, "id_curso": 2, "nome": "Fundamentos de Programação", "periodo": 1, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 2, "id_curso": 2, "nome": "Arquitetura de Software", "periodo": 4, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 3, "id_curso": 2, "nome": "Testes de Software", "periodo": 5, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 4, "id_curso": 2, "nome": "DevOps", "periodo": 6, "carga_horaria": 80, "tipo": "Optativa"},
            {"id_materia": 5, "id_curso": 2, "nome": "Metodologias Ágeis", "periodo": 6, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 1, "id_curso": 3, "nome": "Introdução à Computação", "periodo": 1, "carga_horaria": 60, "tipo": "Obrigatória"},
            {"id_materia": 2, "id_curso": 3, "nome": "Redes de Computadores", "periodo": 3, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 3, "id_curso": 3, "nome": "Sistemas Operacionais", "periodo": 4, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 4, "id_curso": 3, "nome": "Segurança da Informação", "periodo": 6, "carga_horaria": 80, "tipo": "Obrigatória"},
            {"id_materia": 1, "id_curso": 4, "nome": "Lógica de Programação", "periodo": 1, "carga_horaria": 60, "tipo": "Obrigatória"}
        ]
        db.materias.insert_many(materias)
        print(f"✅ {len(materias)} matérias inseridas")
        
        # ========================================
        # ALUNOS
        # ========================================
        print("\n👨‍🎓 Inserindo alunos...")
        alunos = [
            {"matricula": 202501, "nome": "João Pedro Silva", "cpf": "11122233344", "email": "joao.silva@aluno.edu.br", "data_nasc": datetime(2002, 5, 15), "telefone": "11987654321", "periodo": 4, "id_curso": 1, "status_curso": "Cursando"},
            {"matricula": 202502, "nome": "Maria Eduarda Santos", "cpf": "22233344455", "email": "maria.santos@aluno.edu.br", "data_nasc": datetime(2001, 8, 22), "telefone": "11987654322", "periodo": 5, "id_curso": 1, "status_curso": "Cursando"},
            {"matricula": 202503, "nome": "Pedro Henrique Costa", "cpf": "33344455566", "email": "pedro.costa@aluno.edu.br", "data_nasc": datetime(2003, 1, 10), "telefone": "11987654323", "periodo": 3, "id_curso": 2, "status_curso": "Cursando"},
            {"matricula": 202504, "nome": "Ana Julia Oliveira", "cpf": "44455566677", "email": "ana.oliveira@aluno.edu.br", "data_nasc": datetime(2002, 11, 30), "telefone": "11987654324", "periodo": 4, "id_curso": 2, "status_curso": "Cursando"},
            {"matricula": 202505, "nome": "Lucas Gabriel Ferreira", "cpf": "55566677788", "email": "lucas.ferreira@aluno.edu.br", "data_nasc": datetime(2001, 4, 18), "telefone": "11987654325", "periodo": 6, "id_curso": 1, "status_curso": "Cursando"},
            {"matricula": 202506, "nome": "Beatriz Almeida", "cpf": "66677788899", "email": "beatriz.almeida@aluno.edu.br", "data_nasc": datetime(2003, 7, 25), "telefone": "11987654326", "periodo": 2, "id_curso": 3, "status_curso": "Cursando"},
            {"matricula": 202507, "nome": "Guilherme Rocha", "cpf": "77788899900", "email": "guilherme.rocha@aluno.edu.br", "data_nasc": datetime(2002, 9, 12), "telefone": "11987654327", "periodo": 3, "id_curso": 3, "status_curso": "Trancado"},
            {"matricula": 202508, "nome": "Isabela Lima", "cpf": "88899900011", "email": "isabela.lima@aluno.edu.br", "data_nasc": datetime(2001, 12, 5), "telefone": "11987654328", "periodo": 5, "id_curso": 4, "status_curso": "Cursando"},
            {"matricula": 202509, "nome": "Rafael Souza", "cpf": "99900011122", "email": "rafael.souza@aluno.edu.br", "data_nasc": datetime(2003, 3, 20), "telefone": "11987654329", "periodo": 2, "id_curso": 4, "status_curso": "Cursando"},
            {"matricula": 202510, "nome": "Larissa Martins", "cpf": "00011122233", "email": "larissa.martins@aluno.edu.br", "data_nasc": datetime(2002, 6, 8), "telefone": "11987654330", "periodo": 4, "id_curso": 5, "status_curso": "Cursando"}
        ]
        db.alunos.insert_many(alunos)
        print(f"✅ {len(alunos)} alunos inseridos")
        
        # ========================================
        # OFERTAS
        # ========================================
        print("\n📋 Inserindo ofertas...")
        ofertas = [
            {"id": 1, "id_materia": 1, "id_curso": 1, "id_professor": 1, "ano": 2025, "semestre": 1, "vagas": 40},
            {"id": 2, "id_materia": 2, "id_curso": 1, "id_professor": 2, "ano": 2025, "semestre": 1, "vagas": 35},
            {"id": 3, "id_materia": 3, "id_curso": 1, "id_professor": 3, "ano": 2025, "semestre": 1, "vagas": 40},
            {"id": 4, "id_materia": 4, "id_curso": 1, "id_professor": 4, "ano": 2025, "semestre": 1, "vagas": 30},
            {"id": 5, "id_materia": 5, "id_curso": 1, "id_professor": 5, "ano": 2025, "semestre": 1, "vagas": 25},
            {"id": 6, "id_materia": 1, "id_curso": 2, "id_professor": 6, "ano": 2025, "semestre": 1, "vagas": 40},
            {"id": 7, "id_materia": 2, "id_curso": 2, "id_professor": 7, "ano": 2025, "semestre": 1, "vagas": 35},
            {"id": 8, "id_materia": 3, "id_curso": 2, "id_professor": 8, "ano": 2025, "semestre": 1, "vagas": 30},
            {"id": 9, "id_materia": 1, "id_curso": 3, "id_professor": 9, "ano": 2025, "semestre": 1, "vagas": 45},
            {"id": 10, "id_materia": 2, "id_curso": 3, "id_professor": 1, "ano": 2025, "semestre": 1, "vagas": 40}
        ]
        db.ofertas.insert_many(ofertas)
        print(f"✅ {len(ofertas)} ofertas inseridas")
        
        # ========================================
        # GRADE DE ALUNOS
        # ========================================
        print("\n📊 Inserindo grade de alunos...")
        grade_alunos = [
            {"id_oferta": 1, "matricula": 202501, "nota_final": 8.5, "frequencia": 92.0, "status": "Aprovado"},
            {"id_oferta": 1, "matricula": 202502, "nota_final": 9.0, "frequencia": 95.0, "status": "Aprovado"},
            {"id_oferta": 2, "matricula": 202502, "nota_final": 7.5, "frequencia": 88.0, "status": "Aprovado"},
            {"id_oferta": 3, "matricula": 202501, "nota_final": 8.0, "frequencia": 90.0, "status": "Aprovado"},
            {"id_oferta": 3, "matricula": 202505, "nota_final": 9.5, "frequencia": 98.0, "status": "Aprovado"},
            {"id_oferta": 4, "matricula": 202505, "nota_final": 8.5, "frequencia": 93.0, "status": "Aprovado"},
            {"id_oferta": 6, "matricula": 202503, "nota_final": 7.0, "frequencia": 85.0, "status": "Aprovado"},
            {"id_oferta": 6, "matricula": 202504, "nota_final": 8.0, "frequencia": 90.0, "status": "Aprovado"},
            {"id_oferta": 7, "matricula": 202504, "nota_final": None, "frequencia": None, "status": "Cursando"},
            {"id_oferta": 8, "matricula": 202508, "nota_final": 9.0, "frequencia": 96.0, "status": "Aprovado"}
        ]
        db.grade_alunos.insert_many(grade_alunos)
        print(f"✅ {len(grade_alunos)} registros de grade inseridos")
        
        # ========================================
        # COUNTERS
        # ========================================
        print("\n🔢 Inserindo counters...")
        counters = [
            {"_id": "curso_id", "seq": 10},
            {"_id": "professor_id", "seq": 10},
            {"_id": "oferta_id", "seq": 10}
        ]
        db.counters.insert_many(counters)
        print(f"✅ {len(counters)} counters inseridos")
        
        # ========================================
        # RESUMO FINAL
        # ========================================
        print("\n" + "="*50)
        print("✅ TODOS OS DADOS FORAM INSERIDOS COM SUCESSO!")
        print("="*50)
        print(f"📊 Resumo:")
        print(f"  - Cursos: {db.cursos.count_documents({})}")
        print(f"  - Professores: {db.professores.count_documents({})}")
        print(f"  - Matérias: {db.materias.count_documents({})}")
        print(f"  - Alunos: {db.alunos.count_documents({})}")
        print(f"  - Ofertas: {db.ofertas.count_documents({})}")
        print(f"  - Grade de Alunos: {db.grade_alunos.count_documents({})}")
        print(f"  - Counters: {db.counters.count_documents({})}")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Erro ao inserir dados: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close()
        print("\n🔌 Conexão com MongoDB encerrada")

if __name__ == "__main__":
    print("🚀 Iniciando inserção de dados no MongoDB...")
    seed_database()