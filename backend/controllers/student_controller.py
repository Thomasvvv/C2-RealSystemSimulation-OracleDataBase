from flask import Blueprint, request, jsonify
from db.db_conn import connect, close
from datetime import datetime

bp = Blueprint('student', __name__)

def parse_date(dt_str):
    """Convert date from various formats to datetime object or return None."""
    if not dt_str or (isinstance(dt_str, str) and dt_str.strip() == ''):
        return None
    
    if isinstance(dt_str, datetime):
        return dt_str
    
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(dt_str, '%d/%m/%Y')
        except ValueError:
            raise ValueError("A data deve estar no formato 'YYYY-MM-DD' ou 'DD/MM/YYYY'.")

@bp.route('/students', methods=['POST'])
def create_student():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400
        
        nome = data.get('nome')
        cpf = data.get('cpf')
        email = data.get('email')
        periodo = data.get('periodo')
        id_curso = data.get('id_curso')  
        status_curso = data.get('status_curso')
        
        print(f"Dados recebidos: {data}") # Debug
        
        missing_fields = []
        if not nome or nome.strip() == '':
            missing_fields.append('nome')
        if not cpf or cpf.strip() == '':
            missing_fields.append('cpf')
        if not email or email.strip() == '':
            missing_fields.append('email')
        if periodo is None or periodo == '':
            missing_fields.append('periodo')
        if not id_curso or id_curso == '':
            missing_fields.append('id_curso')
        if not status_curso or status_curso.strip() == '':
            missing_fields.append('status_curso')
            
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Campos obrigatórios ausentes ou vazios: {", ".join(missing_fields)}'
            }), 400

        db = connect()
        data_nasc = data.get("data_nasc")
        telefone = data.get("telefone")

        try:
            ano_atual = datetime.now().year
            curso_formatted = str(id_curso).zfill(2)
            
            # Buscar o próximo número sequencial para a matrícula
            prefix_pattern = f"^{ano_atual}{curso_formatted}"
            existing_students = list(db.alunos.find(
                {
                    "matricula": {"$regex": prefix_pattern},
                    "id_curso": int(id_curso)
                },
                {"matricula": 1}
            ).sort("matricula", -1).limit(1))
            
            if existing_students:
                last_matricula = str(existing_students[0]['matricula'])
                proximo_numero = int(last_matricula[-2:]) + 1
            else:
                proximo_numero = 1
            
            numero_formatted = str(proximo_numero).zfill(2)
            matricula = int(f"{ano_atual}{curso_formatted}{numero_formatted}")
            print(f"Matrícula gerada: {matricula}")
            
            # Parse date
            parsed_date = parse_date(data_nasc) if data_nasc else None
            
            # Criar documento do estudante
            student_doc = {
                "matricula": matricula,
                "cpf": cpf,
                "nome": nome,
                "data_nasc": parsed_date,
                "telefone": telefone,
                "email": email,
                "periodo": int(periodo),
                "id_curso": int(id_curso),
                "status_curso": status_curso
            }
            
            db.alunos.insert_one(student_doc)
            
            return jsonify({
                'success': True,
                'message': 'Estudante criado com sucesso',
                'data': {'matricula': matricula}
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar estudante: {str(e)}'
            }), 500
        finally:
            close()
            
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/students', methods=['GET'])
def list_students():
    db = connect()
    try:
        # Buscar todos os alunos ordenados por nome
        cursor = db.alunos.find({}, {"_id": 0}).sort("nome", 1)
        students = []
        
        for doc in cursor:
            student = {
                'matricula': doc.get('matricula'),
                'cpf': doc.get('cpf'),
                'nome': doc.get('nome'),
                'data_nasc': doc.get('data_nasc').strftime('%Y-%m-%d') if doc.get('data_nasc') else None,
                'telefone': doc.get('telefone'),
                'email': doc.get('email'),
                'periodo': doc.get('periodo'),
                'id_curso': doc.get('id_curso'),
                'status_curso': doc.get('status_curso')
            }
            students.append(student)
        
        return jsonify({
            'success': True,
            'data': students,
            'count': len(students)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar estudantes: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/students/<int:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    db = connect()
    try:
        doc = db.alunos.find_one({"matricula": student_id}, {"_id": 0})
        
        if doc:
            student = {
                'matricula': doc.get('matricula'),
                'cpf': doc.get('cpf'),
                'nome': doc.get('nome'),
                'data_nasc': doc.get('data_nasc').strftime('%Y-%m-%d') if doc.get('data_nasc') else None,
                'telefone': doc.get('telefone'),
                'email': doc.get('email'),
                'periodo': doc.get('periodo'),
                'id_curso': doc.get('id_curso'),
                'status_curso': doc.get('status_curso')
            }
            return jsonify({
                'success': True,
                'data': student
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Estudante não encontrado'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estudante: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400

        db = connect()

        try:
            # Verificar se o estudante existe
            existing_student = db.alunos.find_one({"matricula": student_id})
            if not existing_student:
                return jsonify({
                    'success': False,
                    'message': 'Estudante não encontrado'
                }), 404

            update_data = {}
            
            if 'matricula' in data:
                update_data['matricula'] = int(data['matricula'])
            
            if 'nome' in data:
                update_data['nome'] = data['nome']
                
            if 'cpf' in data:
                update_data['cpf'] = data['cpf']
                
            data_nasc = data.get('data_nasc') or data.get('data_nascimento')
            if data_nasc is not None:
                try:
                    parsed_date = parse_date(data_nasc) if data_nasc else None
                    update_data['data_nasc'] = parsed_date
                except ValueError as ve:
                    return jsonify({
                        'success': False,
                        'message': f'Erro ao atualizar estudante: {str(ve)}'
                    }), 400
                    
            if 'telefone' in data:
                update_data['telefone'] = data['telefone']
                
            if 'email' in data:
                update_data['email'] = data['email']
                
            if 'periodo' in data:
                update_data['periodo'] = int(data['periodo'])
                
            id_curso = data.get('id_curso') or data.get('course_id')
            if id_curso is not None:
                update_data['id_curso'] = int(id_curso)
                
            if 'status_curso' in data:
                update_data['status_curso'] = data['status_curso']

            if not update_data:
                return jsonify({
                    'success': False,
                    'message': 'Nenhum campo para atualizar foi fornecido'
                }), 400

            # Atualizar documento
            db.alunos.update_one(
                {"matricula": student_id},
                {"$set": update_data}
            )
            
            return jsonify({
                'success': True,
                'message': 'Estudante atualizado com sucesso'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar estudante: {str(e)}'
            }), 500
        finally:
            close()
            
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    db = connect()
    try:
        # Verificar se o aluno possui matrículas em grade_alunos
        grade_count = db.grade_alunos.count_documents({"id_aluno": student_id})
        if grade_count > 0:
            return jsonify({
                'success': False,
                'message': 'Aluno possui matrículas e não pode ser excluído. Remova-as antes.'
            }), 400
        
        # Verificar se o estudante existe
        existing_student = db.alunos.find_one({"matricula": student_id})
        if not existing_student:
            return jsonify({
                'success': False,
                'message': 'Estudante não encontrado'
            }), 404
        
        # Deletar o estudante
        db.alunos.delete_one({"matricula": student_id})
        
        return jsonify({
            'success': True,
            'message': 'Estudante deletado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar estudante: {str(e)}'
        }), 500
    finally:
        close()
