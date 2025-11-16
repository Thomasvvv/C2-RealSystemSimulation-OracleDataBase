from flask import Blueprint, request, jsonify
from db.db_conn import connect, close

bp = Blueprint('offer', __name__)

@bp.route('/offers', methods=['POST'])
def create_offer():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400
        
        ano = data.get('ano')
        semestre = data.get('semestre')
        id_materia = data.get('id_materia')
        id_curso = data.get('id_curso')
        id_professor = data.get('id_professor')
        
        if not all([ano, semestre, id_materia, id_curso, id_professor]):
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: ano, semestre, id_materia, id_curso, id_professor'
            }), 400

        db = connect()

        try:
            # Verificar se a matéria existe
            materia_exists = db.materias.count_documents({
                "id_materia": int(id_materia),
                "id_curso": int(id_curso)
            })
            if materia_exists == 0:
                return jsonify({
                    'success': False,
                    'message': 'Matéria não encontrada'
                }), 404

            # Verificar se o professor existe
            professor_exists = db.professores.count_documents({"id_professor": int(id_professor)})
            if professor_exists == 0:
                return jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404

            # Gerar novo ID
            result = db.counters.find_one_and_update(
                {"_id": "oferta_id"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            new_id = result["seq"]
            
            # Criar documento da oferta
            offer_doc = {
                "id": new_id,
                "ano": int(ano),
                "semestre": int(semestre),
                "id_materia": int(id_materia),
                "id_curso": int(id_curso),
                "id_professor": int(id_professor)
            }
            
            db.ofertas.insert_one(offer_doc)
            
            return jsonify({
                'success': True,
                'message': 'Oferta criada com sucesso',
                'data': {'id': new_id}
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar oferta: {str(e)}'
            }), 500
        finally:
            close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/offers', methods=['GET'])
def list_offers():
    db = connect()
    try:
        # Usar aggregation pipeline para fazer joins
        pipeline = [
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$id_materia", "id_cur": "$id_curso"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$id_materia", "$$id_mat"]},
                                    {"$eq": ["$id_curso", "$$id_cur"]}
                                ]
                            }
                        }}
                    ],
                    "as": "materia"
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
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "id_professor",
                    "foreignField": "id_professor",
                    "as": "professor"
                }
            },
            {"$unwind": {"path": "$materia", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$professor", "preserveNullAndEmptyArrays": True}},
            {
                "$sort": {
                    "ano": -1,
                    "semestre": -1,
                    "curso.nome": 1,
                    "materia.nome": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "ano": 1,
                    "semestre": 1,
                    "id_materia": 1,
                    "id_curso": 1,
                    "id_professor": 1,
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome"
                }
            }
        ]
        
        offers = list(db.ofertas.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'data': offers,
            'count': len(offers)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar ofertas: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/offers/<int:offer_id>', methods=['GET'])
def get_offer_by_id(offer_id):
    db = connect()
    try:
        pipeline = [
            {"$match": {"id": offer_id}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$id_materia", "id_cur": "$id_curso"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$id_materia", "$$id_mat"]},
                                    {"$eq": ["$id_curso", "$$id_cur"]}
                                ]
                            }
                        }}
                    ],
                    "as": "materia"
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
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "id_professor",
                    "foreignField": "id_professor",
                    "as": "professor"
                }
            },
            {"$unwind": {"path": "$materia", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$professor", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "ano": 1,
                    "semestre": 1,
                    "id_materia": 1,
                    "id_curso": 1,
                    "id_professor": 1,
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome"
                }
            }
        ]
        
        result = list(db.ofertas.aggregate(pipeline))
        
        if result:
            return jsonify({
                'success': True,
                'data': result[0]
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Oferta não encontrada'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar oferta: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/offers/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400

        db = connect()

        try:
            # Verificar se a oferta existe
            existing_offer = db.ofertas.find_one({"id": offer_id})
            if not existing_offer:
                return jsonify({
                    'success': False,
                    'message': 'Oferta não encontrada'
                }), 404

            update_data = {}
            
            if 'ano' in data:
                update_data['ano'] = int(data['ano'])
            
            if 'semestre' in data:
                update_data['semestre'] = int(data['semestre'])
                
            if 'id_professor' in data:
                # Verificar se o professor existe
                professor_exists = db.professores.count_documents({"id_professor": int(data['id_professor'])})
                if professor_exists == 0:
                    return jsonify({
                        'success': False,
                        'message': 'Professor não encontrado'
                    }), 404
                update_data['id_professor'] = int(data['id_professor'])

            if 'id_materia' in data and 'id_curso' in data:
                # Verificar se a matéria existe
                materia_exists = db.materias.count_documents({
                    "id_materia": int(data['id_materia']),
                    "id_curso": int(data['id_curso'])
                })
                if materia_exists == 0:
                    return jsonify({
                        'success': False,
                        'message': 'Matéria não encontrada'
                    }), 404
                update_data['id_materia'] = int(data['id_materia'])
                update_data['id_curso'] = int(data['id_curso'])

            if not update_data:
                return jsonify({
                    'success': False,
                    'message': 'Nenhum campo para atualizar foi fornecido'
                }), 400

            # Atualizar documento
            db.ofertas.update_one(
                {"id": offer_id},
                {"$set": update_data}
            )
            
            return jsonify({
                'success': True,
                'message': 'Oferta atualizada com sucesso'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar oferta: {str(e)}'
            }), 500
        finally:
            close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@bp.route('/offers/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    db = connect()
    try:
        # Verificar se há alunos matriculados na oferta
        enrollment_count = db.grade_alunos.count_documents({"id_oferta": offer_id})
        if enrollment_count > 0:
            return jsonify({
                'success': False,
                'message': 'Oferta possui alunos matriculados e não pode ser excluída. Remova-os antes.'
            }), 400
        
        # Verificar se a oferta existe
        existing_offer = db.ofertas.find_one({"id": offer_id})
        if not existing_offer:
            return jsonify({
                'success': False,
                'message': 'Oferta não encontrada'
            }), 404
        
        # Deletar a oferta
        db.ofertas.delete_one({"id": offer_id})
        
        return jsonify({
            'success': True,
            'message': 'Oferta deletada com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar oferta: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/offers/semester/<int:year>/<int:semester>', methods=['GET'])
def get_offers_by_semester(year, semester):
    """Buscar todas as ofertas de um semestre específico"""
    db = connect()
    try:
        pipeline = [
            {"$match": {"ano": year, "semestre": semester}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$id_materia", "id_cur": "$id_curso"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$id_materia", "$$id_mat"]},
                                    {"$eq": ["$id_curso", "$$id_cur"]}
                                ]
                            }
                        }}
                    ],
                    "as": "materia"
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
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "id_professor",
                    "foreignField": "id_professor",
                    "as": "professor"
                }
            },
            {"$unwind": {"path": "$materia", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$professor", "preserveNullAndEmptyArrays": True}},
            {
                "$sort": {
                    "curso.nome": 1,
                    "materia.nome": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "ano": 1,
                    "semestre": 1,
                    "id_materia": 1,
                    "id_curso": 1,
                    "id_professor": 1,
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome"
                }
            }
        ]
        
        offers = list(db.ofertas.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'data': offers,
            'count': len(offers)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar ofertas do semestre: {str(e)}'
        }), 500
    finally:
        close()
