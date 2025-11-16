from flask import Blueprint, request, jsonify
from db.db_conn import connect, close

bp = Blueprint('course', __name__)

@bp.route('/courses', methods=['POST'])
def create_course():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400
        
        nome = data.get('nome')
        carga_horaria_total = data.get('carga_horaria_total')
        
        if not all([nome, carga_horaria_total]):
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: nome, carga_horaria_total'
            }), 400

        db = connect()

        try:
            # Buscar o próximo ID usando contador
            result = db.counters.find_one_and_update(
                {"_id": "curso_id"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            new_id = result["seq"]
            
            # Criar documento do curso
            course_doc = {
                "id": new_id,
                "nome": nome,
                "carga_horaria_total": float(carga_horaria_total)
            }
            
            db.cursos.insert_one(course_doc)
            
            return jsonify({
                'success': True,
                'message': 'Curso criado com sucesso',
                'data': {'id': new_id}
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar curso: {str(e)}'
            }), 500
        finally:
            close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/courses', methods=['GET'])
def list_courses():
    db = connect()
    try:
        # Buscar todos os cursos ordenados por nome
        cursor = db.cursos.find({}, {"_id": 0}).sort("nome", 1)
        courses = []
        
        for doc in cursor:
            courses.append({
                'id': doc.get('id'),
                'nome': doc.get('nome'),
                'carga_horaria_total': doc.get('carga_horaria_total')
            })
        
        return jsonify({
            'success': True,
            'data': courses,
            'count': len(courses)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar cursos: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course_by_id(course_id):
    db = connect()
    try:
        doc = db.cursos.find_one({"id": course_id}, {"_id": 0})
        
        if doc:
            course = {
                'id': doc.get('id'),
                'nome': doc.get('nome'),
                'carga_horaria_total': doc.get('carga_horaria_total')
            }
            return jsonify({
                'success': True,
                'data': course
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Curso não encontrado'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar curso: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400

        db = connect()

        try:
            # Verificar se o curso existe
            existing_course = db.cursos.find_one({"id": course_id})
            if not existing_course:
                return jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404

            update_data = {}
            
            if 'nome' in data and data['nome'] is not None and str(data['nome']).strip() != '':
                update_data['nome'] = str(data['nome'])
            
            if 'carga_horaria_total' in data:
                carga_value = data['carga_horaria_total']
                
                if carga_value is not None and not (isinstance(carga_value, str) and carga_value.strip() == ''):
                    try:
                        carga_horaria = float(carga_value)
                        if carga_horaria < 0:
                            return jsonify({
                                'success': False,
                                'message': 'Carga horária deve ser um número positivo'
                            }), 400
                        update_data['carga_horaria_total'] = carga_horaria
                    except (ValueError, TypeError):
                        return jsonify({
                            'success': False,
                            'message': f'Carga horária deve ser um número válido. Valor fornecido: {carga_value}'
                        }), 400

            if not update_data:
                return jsonify({
                    'success': False,
                    'message': 'Nenhum campo válido para atualizar foi fornecido'
                }), 400

            # Atualizar documento
            db.cursos.update_one(
                {"id": course_id},
                {"$set": update_data}
            )
            
            return jsonify({
                'success': True,
                'message': 'Curso atualizado com sucesso'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar curso: {str(e)}'
            }), 500
        finally:
            close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    db = connect()
    try:
        # Verificar se o curso possui alunos matriculados
        student_count = db.alunos.count_documents({"id_curso": course_id})
        if student_count > 0:
            return jsonify({
                'success': False,
                'message': 'Curso possui alunos matriculados e não pode ser excluído. Remova-os antes.'
            }), 400
        
        # Verificar se o curso possui matérias cadastradas
        subject_count = db.materias.count_documents({"id_curso": course_id})
        if subject_count > 0:
            return jsonify({
                'success': False,
                'message': 'Curso possui matérias cadastradas e não pode ser excluído. Remova-as antes.'
            }), 400
        
        # Verificar se o curso existe
        existing_course = db.cursos.find_one({"id": course_id})
        if not existing_course:
            return jsonify({
                'success': False,
                'message': 'Curso não encontrado'
            }), 404
        
        # Deletar o curso
        db.cursos.delete_one({"id": course_id})
        
        return jsonify({
            'success': True,
            'message': 'Curso deletado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar curso: {str(e)}'
        }), 500
    finally:
        close()