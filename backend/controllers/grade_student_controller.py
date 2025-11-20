from flask import Blueprint, request, jsonify
from db.db_conn import connect, close

bp = Blueprint('grade_student', __name__)

def refresh_grade_student_table():
    """Atualiza completamente a coleção grade_alunos com todas as matrículas"""
    db = None
    try:
        db = connect()
        
        # Deletar todas as matrículas existentes
        db.grade_alunos.delete_many({})
        
        # Buscar todos os alunos
        alunos = list(db.alunos.find({}, {"matricula": 1, "id_curso": 1, "status_curso": 1}))
        
        enrollments_to_insert = []
        
        for aluno in alunos:
            student_id = aluno.get('matricula')
            id_curso = aluno.get('id_curso')
            student_status = aluno.get('status_curso')
            
            # Buscar ofertas do curso do aluno
            ofertas = list(db.ofertas.find({"id_curso": id_curso}, {"id": 1}))
            
            for oferta in ofertas:
                offer_id = oferta.get('id')
                enrollments_to_insert.append({
                    "id_aluno": student_id,
                    "id_oferta": offer_id,
                    "status": student_status
                })
        
        if enrollments_to_insert:
            db.grade_alunos.insert_many(enrollments_to_insert)
        
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar coleção grade_alunos: {str(e)}")
        return False
    finally:
        if db is not None:
            close()

@bp.route('/enrollments/refresh', methods=['POST'])
def refresh_enrollments():
    """Endpoint para forçar a atualização da coleção grade_alunos"""
    try:
        success = refresh_grade_student_table()
        if success:
            return jsonify({'message': 'Coleção grade_alunos atualizada com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao atualizar coleção grade_alunos'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@bp.route('/enrollments', methods=['GET'])
def list_enrollments():
    """Listar todas as matrículas com aggregation"""
    db = None
    try:
        db = connect()
        
        pipeline = [
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "id_aluno",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {
                "$lookup": {
                    "from": "ofertas",
                    "localField": "id_oferta",
                    "foreignField": "id",
                    "as": "oferta"
                }
            },
            {"$unwind": {"path": "$aluno", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$oferta", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$oferta.id_materia", "id_cur": "$oferta.id_curso"},
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
                    "localField": "oferta.id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "oferta.id_professor",
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
                    "matricula": "$id_aluno",
                    "id_oferta": 1,
                    "status": 1,
                    "aluno_nome": "$aluno.nome",
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome",
                    "ano": "$oferta.ano",
                    "semestre": "$oferta.semestre"
                }
            },
            {
                "$sort": {
                    "aluno_nome": 1,
                    "ano": -1,
                    "semestre": -1,
                    "materia_nome": 1
                }
            }
        ]
        
        enrollments = list(db.grade_alunos.aggregate(pipeline))
        
        return jsonify(enrollments), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar matrículas: {str(e)}'}), 500
    finally:
        if db is not None:
            close()

@bp.route('/enrollments/<int:student_id>/<int:offer_id>', methods=['GET'])
def get_enrollment(student_id, offer_id):
    db = None
    try:
        db = connect()
        
        pipeline = [
            {
                "$match": {
                    "id_aluno": student_id,
                    "id_oferta": offer_id
                }
            },
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "id_aluno",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {
                "$lookup": {
                    "from": "ofertas",
                    "localField": "id_oferta",
                    "foreignField": "id",
                    "as": "oferta"
                }
            },
            {"$unwind": {"path": "$aluno", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$oferta", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$oferta.id_materia", "id_cur": "$oferta.id_curso"},
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
                    "localField": "oferta.id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "oferta.id_professor",
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
                    "matricula": "$id_aluno",
                    "id_oferta": 1,
                    "status": 1,
                    "aluno_nome": "$aluno.nome",
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome",
                    "ano": "$oferta.ano",
                    "semestre": "$oferta.semestre"
                }
            }
        ]
        
        result = list(db.grade_alunos.aggregate(pipeline))
        
        if result:
            return jsonify(result[0]), 200
        return jsonify({'error': 'Matrícula não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar matrícula: {str(e)}'}), 500
    finally:
        if db is not None:
            close()

@bp.route('/students/<int:student_id>/enrollments', methods=['GET'])
def get_student_enrollments(student_id):
    db = None
    try:
        db = connect()
        
        pipeline = [
            {"$match": {"id_aluno": student_id}},
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "id_aluno",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {
                "$lookup": {
                    "from": "ofertas",
                    "localField": "id_oferta",
                    "foreignField": "id",
                    "as": "oferta"
                }
            },
            {"$unwind": {"path": "$aluno", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$oferta", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$oferta.id_materia", "id_cur": "$oferta.id_curso"},
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
                    "localField": "oferta.id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "oferta.id_professor",
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
                    "matricula": "$id_aluno",
                    "id_oferta": 1,
                    "status": 1,
                    "aluno_nome": "$aluno.nome",
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome",
                    "ano": "$oferta.ano",
                    "semestre": "$oferta.semestre"
                }
            },
            {
                "$sort": {
                    "ano": -1,
                    "semestre": -1,
                    "materia_nome": 1
                }
            }
        ]
        
        enrollments = list(db.grade_alunos.aggregate(pipeline))
        
        return jsonify(enrollments), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar matrículas do aluno: {str(e)}'}), 500
    finally:
        if db is not None:
            close()

@bp.route('/offers/<int:offer_id>/enrollments', methods=['GET'])
def get_offer_enrollments(offer_id):
    db = None
    try:
        db = connect()
        
        pipeline = [
            {"$match": {"id_oferta": offer_id}},
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "id_aluno",
                    "foreignField": "matricula",
                    "as": "aluno"
                }
            },
            {
                "$lookup": {
                    "from": "ofertas",
                    "localField": "id_oferta",
                    "foreignField": "id",
                    "as": "oferta"
                }
            },
            {"$unwind": {"path": "$aluno", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$oferta", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "materias",
                    "let": {"id_mat": "$oferta.id_materia", "id_cur": "$oferta.id_curso"},
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
                    "localField": "oferta.id_curso",
                    "foreignField": "id",
                    "as": "curso"
                }
            },
            {
                "$lookup": {
                    "from": "professores",
                    "localField": "oferta.id_professor",
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
                    "matricula": "$id_aluno",
                    "id_oferta": 1,
                    "status": 1,
                    "aluno_nome": "$aluno.nome",
                    "materia_nome": "$materia.nome",
                    "curso_nome": "$curso.nome",
                    "professor_nome": "$professor.nome",
                    "ano": "$oferta.ano",
                    "semestre": "$oferta.semestre"
                }
            },
            {"$sort": {"aluno_nome": 1}}
        ]
        
        enrollments = list(db.grade_alunos.aggregate(pipeline))
        
        return jsonify(enrollments), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar matrículas da oferta: {str(e)}'}), 500
    finally:
        if db is not None:
            close()
