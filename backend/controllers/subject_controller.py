from flask import Blueprint, request, jsonify
from db.db_conn import connect, close

bp = Blueprint('subject', __name__)

@bp.route('/subjects', methods=['POST'])
def create_subject():
    db = None
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400
        
        id_curso = data.get('id_curso')
        periodo = data.get('periodo')
        nome = data.get('nome')
        carga_horaria = data.get('carga_horaria')
        
        missing_fields = []
        if not id_curso or id_curso == '':
            missing_fields.append('id_curso')
        if periodo is None or periodo == '':
            missing_fields.append('periodo')
        if not nome or nome.strip() == '':
            missing_fields.append('nome')
        if carga_horaria is None or carga_horaria == '':
            missing_fields.append('carga_horaria')
            
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400

        id_materia = data.get('id_materia')
        
        db = connect()
        
        if not id_materia:
            max_materia = db.materias.find_one(
                {"id_curso": id_curso},
                sort=[("id_materia", -1)]
            )
            id_materia = (max_materia['id_materia'] + 1) if max_materia else 1

        try:
            curso_exists = db.cursos.count_documents({"id": id_curso})
            if curso_exists == 0:
                return jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404

            subject_doc = {
                "id_materia": id_materia,
                "id_curso": id_curso,
                "periodo": periodo,
                "nome": nome,
                "carga_horaria": carga_horaria
            }
            
            db.materias.insert_one(subject_doc)
            
            return jsonify({
                'success': True,
                'message': 'Matéria criada com sucesso',
                'data': {'id_materia': id_materia, 'id_curso': id_curso}
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar matéria: {str(e)}'
            }), 500
        finally:
            if db:
                close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/subjects', methods=['GET'])
def list_subjects():
    db = None
    try:
        db = connect()
        
        pipeline = [
            {
                "$lookup": {
                    "from": "cursos",
                    "localField": "id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id_materia": 1,
                    "id_curso": 1,
                    "periodo": 1,
                    "nome": 1,
                    "carga_horaria": 1,
                    "curso_nome": "$curso.nome"
                }
            },
            {
                "$sort": {
                    "curso_nome": 1,
                    "periodo": 1,
                    "nome": 1
                }
            }
        ]
        
        subjects = list(db.materias.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'data': subjects,
            'count': len(subjects)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar matérias: {str(e)}'
        }), 500
    finally:
        if db:
            close()

@bp.route('/subjects/<int:subject_id>/<int:course_id>', methods=['GET'])
def get_subject_by_id(subject_id, course_id):
    db = None
    try:
        db = connect()
        
        pipeline = [
            {
                "$match": {
                    "id_materia": subject_id,
                    "id_curso": course_id
                }
            },
            {
                "$lookup": {
                    "from": "cursos",
                    "localField": "id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id_materia": 1,
                    "id_curso": 1,
                    "periodo": 1,
                    "nome": 1,
                    "carga_horaria": 1,
                    "curso_nome": "$curso.nome"
                }
            }
        ]
        
        result = list(db.materias.aggregate(pipeline))
        
        if result:
            subject = result[0]
            return jsonify({
                'success': True,
                'data': subject
            }), 200
        return jsonify({
            'success': False,
            'message': 'Matéria não encontrada'
        }), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar matéria: {str(e)}'}), 500
    finally:
        if db:
            close()

@bp.route('/subjects/<int:subject_id>/<int:course_id>', methods=['PUT'])
def update_subject(subject_id, course_id):
    db = None
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400

        db = connect()

        try:
            subject_exists = db.materias.count_documents({
                "id_materia": subject_id,
                "id_curso": course_id
            })
            if subject_exists == 0:
                return jsonify({'error': 'Matéria não encontrada'}), 404

            update_fields = {}
            
            print(f"DEBUG - Dados recebidos: {data}")  # Log para debug
            
            if 'periodo' in data:
                try:
                    periodo_value = int(data['periodo']) if data['periodo'] else None
                    update_fields['periodo'] = periodo_value
                    print(f"DEBUG - Periodo convertido: {periodo_value}")
                except (ValueError, TypeError) as e:
                    return jsonify({'error': f'Período deve ser um número válido: {data["periodo"]}'}), 400
            
            if 'nome' in data:
                update_fields['nome'] = data['nome']
                print(f"DEBUG - Nome: {data['nome']}")
                
            if 'carga_horaria' in data:
                try:
                    carga_value = int(data['carga_horaria']) if data['carga_horaria'] else None
                    update_fields['carga_horaria'] = carga_value
                    print(f"DEBUG - Carga horária convertida: {carga_value}")
                except (ValueError, TypeError) as e:
                    return jsonify({'error': f'Carga horária deve ser um número válido: {data["carga_horaria"]}'}), 400
            
            if 'id_curso' in data:
                try:
                    id_curso_value = int(data['id_curso']) if data['id_curso'] else None
                    update_fields['id_curso'] = id_curso_value
                    print(f"DEBUG - ID Curso convertido: {id_curso_value}")
                except (ValueError, TypeError) as e:
                    return jsonify({'error': f'ID do curso deve ser um número válido: {data["id_curso"]}'}), 400

            if not update_fields:
                return jsonify({'error': 'Nenhum campo para atualizar foi fornecido'}), 400

            db.materias.update_one(
                {"id_materia": subject_id, "id_curso": course_id},
                {"$set": update_fields}
            )
            
            return jsonify({'message': 'Matéria atualizada com sucesso'}), 200
            
        except Exception as e:
            return jsonify({'error': f'Erro ao atualizar matéria: {str(e)}'}), 500
        finally:
            if db:
                close()
            
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@bp.route('/subjects/<int:subject_id>/<int:course_id>', methods=['DELETE'])
def delete_subject(subject_id, course_id):
    db = None
    try:
        db = connect()
        
        offer_count = db.ofertas.count_documents({
            "id_materia": subject_id,
            "id_curso": course_id
        })
        if offer_count > 0:
            return jsonify({'error': 'Não é possível excluir matéria com ofertas cadastradas'}), 400
        
        subject_exists = db.materias.count_documents({
            "id_materia": subject_id,
            "id_curso": course_id
        })
        if subject_exists == 0:
            return jsonify({'error': 'Matéria não encontrada'}), 404
        
        db.materias.delete_one({
            "id_materia": subject_id,
            "id_curso": course_id
        })
        
        return jsonify({'message': 'Matéria deletada com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar matéria: {str(e)}'}), 500
    finally:
        if db:
            close()

@bp.route('/courses/<int:course_id>/subjects', methods=['GET'])
def get_subjects_by_course(course_id):
    """Buscar todas as matérias de um curso específico"""
    db = None
    try:
        db = connect()
        
        pipeline = [
            {
                "$match": {
                    "id_curso": course_id
                }
            },
            {
                "$lookup": {
                    "from": "cursos",
                    "localField": "id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id_materia": 1,
                    "id_curso": 1,
                    "periodo": 1,
                    "nome": 1,
                    "carga_horaria": 1,
                    "curso_nome": "$curso.nome"
                }
            },
            {
                "$sort": {
                    "periodo": 1,
                    "nome": 1
                }
            }
        ]
        
        subjects = list(db.materias.aggregate(pipeline))
        
        return jsonify(subjects), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar matérias do curso: {str(e)}'}), 500
    finally:
        if db:
            close()
