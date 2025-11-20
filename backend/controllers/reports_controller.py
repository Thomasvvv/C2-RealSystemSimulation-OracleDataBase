from flask import Blueprint, request, jsonify
from db.db_conn import connect, close
from datetime import datetime

bp = Blueprint('reports', __name__)

# ===== RELATÓRIOS ESSENCIAIS DO SISTEMA =====
# Apenas relatórios ativamente utilizados pelo frontend

@bp.route('/reports/dashboard', methods=['GET'])
def dashboard_summary():
    """Resumo geral do sistema para dashboard"""
    db = None
    
    try:
        print("🔄 [DASHBOARD] Iniciando geração de relatório do dashboard...")
        
        db = connect()
        if not db:
            raise Exception("Falha ao estabelecer conexão com o banco de dados")
        
        print("✅ [DASHBOARD] Conexão com banco estabelecida com sucesso")
        
    except Exception as e:
        error_msg = f"Erro de conexão com banco: {str(e)}"
        print(f"❌ [DASHBOARD] {error_msg}")
        return jsonify({'error': error_msg, 'tipo': 'conexao_banco'}), 500
    
    try:
        print("📊 [DASHBOARD] Coletando contadores gerais...")
        
        try:
            total_courses = db.cursos.count_documents({})
            print(f"✅ [DASHBOARD] Total de cursos: {total_courses}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar cursos: {e}")
            raise Exception(f"Erro ao acessar coleção cursos: {str(e)}")
        
        try:
            total_students = db.alunos.count_documents({})
            print(f"✅ [DASHBOARD] Total de alunos: {total_students}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar alunos: {e}")
            raise Exception(f"Erro ao acessar coleção alunos: {str(e)}")
        
        try:
            total_professors = db.professores.count_documents({})
            print(f"✅ [DASHBOARD] Total de professores: {total_professors}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar professores: {e}")
            raise Exception(f"Erro ao acessar coleção professores: {str(e)}")
        
        try:
            total_subjects = db.materias.count_documents({})
            print(f"✅ [DASHBOARD] Total de matérias: {total_subjects}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar matérias: {e}")
            raise Exception(f"Erro ao acessar coleção materias: {str(e)}")
        
        try:
            total_offers = db.ofertas.count_documents({})
            print(f"✅ [DASHBOARD] Total de ofertas: {total_offers}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar ofertas: {e}")
            raise Exception(f"Erro ao acessar coleção ofertas: {str(e)}")
        
        try:
            total_enrollments = db.grade_alunos.count_documents({})
            print(f"✅ [DASHBOARD] Total de matrículas: {total_enrollments}")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao contar matrículas: {e}")
            raise Exception(f"Erro ao acessar coleção grade_alunos: {str(e)}")
        
        print("📅 [DASHBOARD] Coletando atividades recentes...")
        
        try:
            recent_students = list(db.alunos.find(
                {"data_nasc": {"$ne": None}},
                {"_id": 0, "nome": 1, "data_nasc": 1}
            ).sort("data_nasc", -1).limit(5))
            print(f"✅ [DASHBOARD] Coletados {len(recent_students)} alunos recentes")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao buscar alunos recentes: {e}")
            recent_students = []
        
        try:
            recent_professors = list(db.professores.find(
                {"data_nasc": {"$ne": None}},
                {"_id": 0, "nome": 1, "data_nasc": 1}
            ).sort("data_nasc", -1).limit(5))
            print(f"✅ [DASHBOARD] Coletados {len(recent_professors)} professores recentes")
        except Exception as e:
            print(f"❌ [DASHBOARD] Erro ao buscar professores recentes: {e}")
            recent_professors = []
        
        recent_activities = []
        for student in recent_students:
            recent_activities.append({
                'tipo': 'Aluno',
                'nome': student.get('nome', 'Nome não informado'),
                'data': student.get('data_nasc').strftime('%Y-%m-%d') if student.get('data_nasc') else 'Data não informada'
            })
        
        for professor in recent_professors:
            recent_activities.append({
                'tipo': 'Professor',
                'nome': professor.get('nome', 'Nome não informado'),
                'data': professor.get('data_nasc').strftime('%Y-%m-%d') if professor.get('data_nasc') else 'Data não informada'
            })
        
        recent_activities.sort(key=lambda x: x['data'], reverse=True)
        recent_activities = recent_activities[:10]
        
        report = {
            'totais': {
                'cursos': total_courses,
                'alunos': total_students,
                'professores': total_professors,
                'materias': total_subjects,
                'ofertas': total_offers,
                'matriculas': total_enrollments
            },
            'atividades_recentes': recent_activities
        }
        
        print("✅ [DASHBOARD] Relatório gerado com sucesso")
        return jsonify(report), 200
        
    except Exception as e:
        error_msg = f'Erro ao gerar dashboard: {str(e)}'
        error_type = 'processamento'
        
        print(f"❌ [DASHBOARD] {error_msg}")
        
        import traceback
        print(f"📋 [DASHBOARD] Stack trace completo:\n{traceback.format_exc()}")
        
        return jsonify({
            'error': error_msg, 
            'tipo': error_type,
            'detalhes': str(e)
        }), 500
        
    finally:
        try:
            if db is not None:
                close()
            print("🔒 [DASHBOARD] Conexões fechadas")
        except Exception as e:
            print(f"⚠️ [DASHBOARD] Erro ao fechar conexões: {e}")

@bp.route('/reports/course-statistics', methods=['GET'])
def course_statistics():
    """Relatório de estatísticas por curso usando aggregation"""
    db = None
    
    try:
        print("🔄 [COURSE_STATS] Iniciando geração de estatísticas por curso...")
        
        db = connect()
        if not db:
            raise Exception("Falha ao estabelecer conexão com o banco de dados")
        
        print("✅ [COURSE_STATS] Conexão com banco estabelecida com sucesso")
        
    except Exception as e:
        error_msg = f"Erro de conexão com banco: {str(e)}"
        print(f"❌ [COURSE_STATS] {error_msg}")
        return jsonify({'error': error_msg, 'tipo': 'conexao_banco'}), 500
    
    try:
        print("📊 [COURSE_STATS] Executando aggregation pipeline...")
        
        # Pipeline de aggregation para estatísticas por curso
        pipeline = [
            {
                "$lookup": {
                    "from": "alunos",
                    "localField": "id",
                    "foreignField": "id_curso",
                    "as": "alunos"
                }
            },
            {
                "$lookup": {
                    "from": "materias",
                    "localField": "id",
                    "foreignField": "id_curso",
                    "as": "materias"
                }
            },
            {
                "$lookup": {
                    "from": "ofertas",
                    "localField": "id",
                    "foreignField": "id_curso",
                    "as": "ofertas"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "curso_id": "$id",
                    "curso_nome": "$nome",
                    "carga_total_curso": "$carga_horaria_total",
                    "total_alunos": {"$size": "$alunos"},
                    "total_materias": {"$size": "$materias"},
                    "carga_horaria_materias": {
                        "$sum": "$materias.carga_horaria"
                    },
                    "total_ofertas": {"$size": "$ofertas"},
                    "ofertas_ano_atual": {
                        "$size": {
                            "$filter": {
                                "input": "$ofertas",
                                "as": "oferta",
                                "cond": {"$eq": ["$$oferta.ano", datetime.now().year]}
                            }
                        }
                    },
                    "ofertas": 1
                }
            }
        ]
        
        courses = list(db.cursos.aggregate(pipeline))
        print(f"✅ [COURSE_STATS] Aggregation executada. {len(courses)} cursos encontrados")
        
        if not courses:
            print("⚠️ [COURSE_STATS] Nenhum curso encontrado no banco")
            return jsonify({
                'resumo_geral': {
                    'total_cursos': 0,
                    'total_alunos_sistema': 0,
                    'total_materias_sistema': 0,
                    'total_ofertas_sistema': 0,
                    'total_matriculas_sistema': 0
                },
                'estatisticas_por_curso': [],
                'mensagem': 'Nenhum curso cadastrado no sistema'
            }), 200
        
        # Calcular matriculas ativas por curso
        for course in courses:
            oferta_ids = [o.get('id') for o in course.get('ofertas', [])]
            matriculas_count = db.grade_alunos.count_documents({"id_oferta": {"$in": oferta_ids}}) if oferta_ids else 0
            course['total_matriculas_ativas'] = matriculas_count
        
        try:
            total_students = sum(course.get('total_alunos', 0) for course in courses)
            total_subjects = sum(course.get('total_materias', 0) for course in courses)
            total_offers = sum(course.get('total_ofertas', 0) for course in courses)
            total_enrollments = sum(course.get('total_matriculas_ativas', 0) for course in courses)
            
            print(f"📊 [COURSE_STATS] Totais calculados - Alunos: {total_students}, Ofertas: {total_offers}")
        except Exception as e:
            print(f"❌ [COURSE_STATS] Erro ao calcular totais: {e}")
            raise Exception(f"Erro no processamento dos dados: {str(e)}")
        
        report = {
            'resumo_geral': {
                'total_cursos': len(courses),
                'total_alunos_sistema': total_students,
                'total_materias_sistema': total_subjects,
                'total_ofertas_sistema': total_offers,
                'total_matriculas_sistema': total_enrollments
            },
            'estatisticas_por_curso': []
        }
        
        print("🔄 [COURSE_STATS] Processando estatísticas por curso...")
        
        for i, course in enumerate(courses):
            try:
                alunos = course.get('total_alunos', 0)
                ofertas = course.get('total_ofertas', 0)
                matriculas = course.get('total_matriculas_ativas', 0)
                
                perc_alunos = (alunos / total_students * 100) if total_students > 0 else 0
                perc_ofertas = (ofertas / total_offers * 100) if total_offers > 0 else 0
                
                media_alunos_por_oferta = round(matriculas / ofertas, 2) if ofertas > 0 else 0
                
                course_stats = {
                    'curso_id': course.get('curso_id', 0),
                    'curso_nome': course.get('curso_nome', 'Nome não informado'),
                    'carga_horaria_total_curso': course.get('carga_total_curso', 0),
                    'total_alunos': alunos,
                    'total_materias': course.get('total_materias', 0),
                    'carga_horaria_materias': course.get('carga_horaria_materias', 0),
                    'total_ofertas': ofertas,
                    'total_matriculas_ativas': matriculas,
                    'ofertas_ano_atual': course.get('ofertas_ano_atual', 0),
                    'percentual_alunos': round(perc_alunos, 2),
                    'percentual_ofertas': round(perc_ofertas, 2),
                    'media_alunos_por_oferta': media_alunos_por_oferta
                }
                
                report['estatisticas_por_curso'].append(course_stats)
                
            except Exception as e:
                print(f"⚠️ [COURSE_STATS] Erro ao processar curso {i+1}: {e}")
                continue
        
        # Ordenar por total de alunos e ofertas
        report['estatisticas_por_curso'].sort(key=lambda x: (x['total_alunos'], x['total_ofertas']), reverse=True)
        
        print(f"✅ [COURSE_STATS] Relatório gerado com {len(report['estatisticas_por_curso'])} cursos")
        return jsonify(report), 200
        
    except Exception as e:
        error_msg = f'Erro ao gerar relatório de estatísticas: {str(e)}'
        error_type = 'processamento'
        
        print(f"❌ [COURSE_STATS] {error_msg}")
        
        import traceback
        print(f"📋 [COURSE_STATS] Stack trace completo:\n{traceback.format_exc()}")
        
        return jsonify({
            'error': error_msg, 
            'tipo': error_type,
            'detalhes': str(e)
        }), 500
        
    finally:
        try:
            if db is not None:
                close()
            print("🔒 [COURSE_STATS] Conexões fechadas")
        except Exception as e:
            print(f"⚠️ [COURSE_STATS] Erro ao fechar conexões: {e}")

@bp.route('/reports/offers-complete', methods=['GET'])
def offers_complete_report():
    """Relatório completo de ofertas com aggregation pipeline"""
    db = None
    
    try:
        print("🔄 [OFFERS_REPORT] Iniciando geração de relatório de ofertas...")
        
        db = connect()
        if not db:
            raise Exception("Falha ao estabelecer conexão com o banco de dados")
        
        print("✅ [OFFERS_REPORT] Conexão com banco estabelecida com sucesso")
        
        print("📊 [OFFERS_REPORT] Executando aggregation pipeline...")
        
        pipeline = [
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
                    "from": "professores",
                    "localField": "id_professor",
                    "foreignField": "id_professor",
                    "as": "professor"
                }
            },
            {
                "$lookup": {
                    "from": "grade_alunos",
                    "localField": "id",
                    "foreignField": "id_oferta",
                    "as": "matriculas"
                }
            },
            {"$unwind": {"path": "$curso", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$materia", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$professor", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "oferta_id": "$id",
                    "ano": 1,
                    "semestre": 1,
                    "curso_nome": "$curso.nome",
                    "materia_nome": "$materia.nome",
                    "periodo_materia": "$materia.periodo",
                    "carga_horaria_materia": "$materia.carga_horaria",
                    "professor_nome": "$professor.nome",
                    "professor_email": "$professor.email",
                    "professor_status": "$professor.status",
                    "total_matriculados": {"$size": "$matriculas"},
                    "carga_total_curso": "$curso.carga_horaria_total"
                }
            },
            {
                "$sort": {
                    "ano": -1,
                    "semestre": -1,
                    "curso_nome": 1,
                    "materia_nome": 1
                }
            }
        ]
        
        offers = list(db.ofertas.aggregate(pipeline))
        print(f"✅ [OFFERS_REPORT] Aggregation executada. {len(offers)} ofertas encontradas")
        
        if not offers:
            print("⚠️ [OFFERS_REPORT] Nenhuma oferta encontrada no banco")
            return jsonify({
                'resumo_geral': {
                    'total_ofertas': 0,
                    'total_matriculados': 0,
                    'professores_ativos': 0,
                    'cursos_ativos': 0,
                    'media_alunos_por_oferta': 0
                },
                'todas_ofertas': [],
                'mensagem': 'Nenhuma oferta cadastrada no sistema'
            }), 200
        
        total_offers = len(offers)
        total_students = sum(offer.get('total_matriculados', 0) for offer in offers)
        
        professor_names = {offer.get('professor_nome') for offer in offers if offer.get('professor_nome') and offer.get('professor_nome') != 'Professor não informado'}
        course_names = {offer.get('curso_nome') for offer in offers if offer.get('curso_nome') and offer.get('curso_nome') != 'Curso não informado'}
        
        active_professors = len(professor_names)
        active_courses = len(course_names)
        
        print(f"📊 [OFFERS_REPORT] Estatísticas - Ofertas: {total_offers}, Matriculados: {total_students}")
        
        report = {
            'resumo_geral': {
                'total_ofertas': total_offers,
                'total_matriculados': total_students,
                'professores_ativos': active_professors,
                'cursos_ativos': active_courses,
                'media_alunos_por_oferta': round(total_students / total_offers, 2) if total_offers > 0 else 0
            },
            'todas_ofertas': []
        }
        
        print("🔄 [OFFERS_REPORT] Processando detalhes das ofertas...")
        
        processed_offers = 0
        for i, offer in enumerate(offers):
            try:
                offer_detail = {
                    'oferta_id': offer.get('oferta_id', 0),
                    'periodo': f"{offer.get('ano', 0)}/{offer.get('semestre', 0)}º",
                    'curso_nome': offer.get('curso_nome') or 'Curso não informado',
                    'materia_nome': offer.get('materia_nome') or 'Matéria não informada',
                    'periodo_materia': f"{offer.get('periodo_materia', 0)}º período",
                    'carga_horaria': f"{offer.get('carga_horaria_materia', 0)}h",
                    'professor_nome': offer.get('professor_nome') or 'Professor não informado',
                    'professor_email': offer.get('professor_email') or 'Email não informado',
                    'professor_status': offer.get('professor_status') or 'Status não informado',
                    'total_matriculados': offer.get('total_matriculados', 0),
                    'carga_total_curso': offer.get('carga_total_curso', 0)
                }
                
                report['todas_ofertas'].append(offer_detail)
                processed_offers += 1
                
            except Exception as e:
                print(f"⚠️ [OFFERS_REPORT] Erro ao processar oferta {i+1}: {e}")
                continue
        
        print(f"✅ [OFFERS_REPORT] Relatório gerado com {processed_offers} ofertas processadas")
        return jsonify(report), 200
        
    except Exception as e:
        error_msg = f'Erro ao gerar relatório de ofertas: {str(e)}'
        error_type = 'processamento'
        
        print(f"❌ [OFFERS_REPORT] {error_msg}")
        
        import traceback
        print(f"📋 [OFFERS_REPORT] Stack trace completo:\n{traceback.format_exc()}")
        
        return jsonify({
            'error': error_msg, 
            'tipo': error_type,
            'detalhes': str(e)
        }), 500
        
    finally:
        try:
            if db is not None:
                close()
                print("🔒 [OFFERS_REPORT] Conexão fechada")
        except Exception as e:
            print(f"⚠️ [OFFERS_REPORT] Erro ao fechar conexões: {e}")
