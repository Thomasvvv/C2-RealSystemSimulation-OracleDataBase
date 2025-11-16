from flask import Blueprint, request, jsonify
from db.db_conn import connect, close
from datetime import datetime

bp = Blueprint('professor', __name__)

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

@bp.route('/professors', methods=['POST'])
def create_professor():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400
        
        cpf = data.get('cpf')
        nome = data.get('nome')
        email = data.get('email')
        status = data.get('status')
        
        if not all([cpf, nome, email, status]):
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: cpf, nome, email, status'
            }), 400

        db = connect()
        data_nasc = data.get("data_nasc")
        telefone = data.get("telefone")

        try:
            # Parse date
            parsed_date = parse_date(data_nasc) if data_nasc else None
            
            # Gerar novo ID
            result = db.counters.find_one_and_update(
                {"_id": "professor_id"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            new_id = result["seq"]
            
            # Criar documento do professor
            professor_doc = {
                "id_professor": new_id,
                "cpf": cpf,
                "nome": nome,
                "data_nasc": parsed_date,
                "telefone": telefone,
                "email": email,
                "status": status
            }
            
            db.professores.insert_one(professor_doc)
            
            return jsonify({
                'success': True,
                'message': 'Professor criado com sucesso',
                'data': {'id_professor': new_id}
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar professor: {str(e)}'
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

@bp.route('/professors', methods=['GET'])
def list_professors():
    db = connect()
    try:
        # Buscar todos os professores ordenados por nome
        cursor = db.professores.find({}, {"_id": 0}).sort("nome", 1)
        professors = []
        
        for doc in cursor:
            professor = {
                'id_professor': doc.get('id_professor'),
                'cpf': doc.get('cpf'),
                'nome': doc.get('nome'),
                'data_nasc': doc.get('data_nasc').strftime('%Y-%m-%d') if doc.get('data_nasc') else None,
                'telefone': doc.get('telefone'),
                'email': doc.get('email'),
                'status': doc.get('status')
            }
            professors.append(professor)
        
        return jsonify({
            'success': True,
            'data': professors,
            'count': len(professors)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar professores: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/professors/<int:professor_id>', methods=['GET'])
def get_professor_by_id(professor_id):
    db = connect()
    try:
        doc = db.professores.find_one({"id_professor": professor_id}, {"_id": 0})
        
        if doc:
            professor = {
                'id_professor': doc.get('id_professor'),
                'cpf': doc.get('cpf'),
                'nome': doc.get('nome'),
                'data_nasc': doc.get('data_nasc').strftime('%Y-%m-%d') if doc.get('data_nasc') else None,
                'telefone': doc.get('telefone'),
                'email': doc.get('email'),
                'status': doc.get('status')
            }
            return jsonify({
                'success': True,
                'data': professor
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Professor não encontrado'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar professor: {str(e)}'
        }), 500
    finally:
        close()

@bp.route('/professors/<int:professor_id>', methods=['PUT'])
def update_professor(professor_id):
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados JSON são obrigatórios'
            }), 400

        db = connect()

        try:
            # Verificar se o professor existe
            existing_professor = db.professores.find_one({"id_professor": professor_id})
            if not existing_professor:
                return jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404

            update_data = {}
            
            if 'cpf' in data:
                update_data['cpf'] = data['cpf']
            
            if 'nome' in data:
                update_data['nome'] = data['nome']
                
            if 'data_nasc' in data:
                parsed_date = parse_date(data['data_nasc']) if data['data_nasc'] else None
                update_data['data_nasc'] = parsed_date
                    
            if 'telefone' in data:
                update_data['telefone'] = data['telefone']
                
            if 'email' in data:
                update_data['email'] = data['email']
                
            if 'status' in data:
                status_value = data['status']
                if status_value is None:
                    return jsonify({
                        'success': False,
                        'message': 'Campo status é obrigatório e não pode ser nulo'
                    }), 400
                
                status_str = str(status_value).strip()
                if not status_str:
                    return jsonify({
                        'success': False,
                        'message': 'Campo status é obrigatório e não pode estar vazio'
                    }), 400
                    
                update_data['status'] = status_str

            if not update_data:
                return jsonify({
                    'success': False,
                    'message': 'Nenhum campo para atualizar foi fornecido'
                }), 400

            # Atualizar documento
            db.professores.update_one(
                {"id_professor": professor_id},
                {"$set": update_data}
            )
            
            return jsonify({
                'success': True,
                'message': 'Professor atualizado com sucesso'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar professor: {str(e)}'
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

@bp.route('/professors/<int:professor_id>', methods=['DELETE'])
def delete_professor(professor_id):
    db = connect()
    try:
        # Verificar se o professor possui ofertas cadastradas
        offer_count = db.ofertas.count_documents({"id_professor": professor_id})
        if offer_count > 0:
            return jsonify({
                'success': False,
                'message': 'Professor possui ofertas cadastradas e não pode ser excluído. Remova-as antes.'
            }), 400
        
        # Verificar se o professor existe
        existing_professor = db.professores.find_one({"id_professor": professor_id})
        if not existing_professor:
            return jsonify({
                'success': False,
                'message': 'Professor não encontrado'
            }), 404
        
        # Deletar o professor
        db.professores.delete_one({"id_professor": professor_id})
        
        return jsonify({
            'success': True,
            'message': 'Professor deletado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar professor: {str(e)}'
        }), 500
    finally:
        close()
