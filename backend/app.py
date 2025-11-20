from flask import Flask, jsonify
from flask_cors import CORS
from controllers import (
    student_controller,
    course_controller,
    professor_controller,
    subject_controller,
    offer_controller,
    grade_student_controller,
    reports_controller
)
from db.db_conn import get_connection
import sys

app = Flask(__name__)
CORS(app)

# Testar conexão com MongoDB na inicialização
def test_mongo_connection():
    """Testa a conexão com MongoDB ao iniciar a aplicação"""
    try:
        db = get_connection()
        # Tentar fazer uma operação simples para verificar a conexão
        db.command('ping')
        print("✅ Conexão com MongoDB estabelecida com sucesso!")
        print(f"📁 Database: {db.name}")
        print(f"📊 Coleções disponíveis: {db.list_collection_names()}")
        return True
    except Exception as e:
        print(f"❌ ERRO: Não foi possível conectar ao MongoDB: {e}")
        print("⚠️  Certifique-se de que o MongoDB está rodando em localhost:27017")
        return False

@app.route("/")
def home():
    return {
        "msg": "SGE - Sistema de Gestão de Estudantes",
        "version": "1.0.0",
        "database": "MongoDB",
        "endpoints": {
            "students": "/api/students",
            "courses": "/api/courses", 
            "professors": "/api/professors",
            "subjects": "/api/subjects",
            "offers": "/api/offers",
            "enrollments": "/api/enrollments",
            "reports": "/api/reports"
        }
    }

@app.route("/api/")
def api_info():
    return {
        "msg": "SGE API - Sistema de Gestão de Estudantes",
        "version": "1.0.0",
        "database": "MongoDB",
        "status": "online",
        "available_endpoints": [
            "/api/students",
            "/api/courses", 
            "/api/professors",
            "/api/subjects",
            "/api/offers",
            "/api/enrollments",
            "/api/reports/dashboard",
            "/api/reports/course-statistics",
            "/api/reports/offers-complete"
        ]
    }

@app.route("/api/health")
def health_check():
    """Endpoint para verificar a saúde da API e conexão com MongoDB"""
    try:
        db = get_connection()
        db.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "database_name": db.name,
            "collections": db.list_collection_names()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content - evita erro 404 no console

# Registrar todas as rotas dos controladores
app.register_blueprint(student_controller.bp, url_prefix="/api")
app.register_blueprint(course_controller.bp, url_prefix="/api")
app.register_blueprint(professor_controller.bp, url_prefix="/api")
app.register_blueprint(subject_controller.bp, url_prefix="/api")
app.register_blueprint(offer_controller.bp, url_prefix="/api")
app.register_blueprint(grade_student_controller.bp, url_prefix="/api")
app.register_blueprint(reports_controller.bp, url_prefix="/api")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando SGE - Sistema de Gestão de Estudantes")
    print("=" * 60)
    
    # Testar conexão com MongoDB antes de iniciar o servidor
    if not test_mongo_connection():
        print("\n⚠️  AVISO: Aplicação iniciará sem conexão com MongoDB!")
        print("   Você pode precisar iniciar o MongoDB primeiro:")
        print("   $ sudo systemctl start mongod")
        print("   ou")
        print("   $ mongod")
        print()
    
    print("\n🌐 Servidor Flask iniciando...")
    print("   URL: http://localhost:5000")
    print("   Health Check: http://localhost:5000/api/health")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)