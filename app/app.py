from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"pong": True})

@app.route("/soma", methods=["POST"])
def soma():
    data = request.json
    valor = data.get("valor", 0)
    return jsonify({"resultado": valor + 1})

@app.route("/serAPI", methods=["GET"])
def serapi_search():
    """
    Endpoint para pesquisar no Google Maps usando SerpAPI com paginação automática.
    
    Parâmetros esperados no JSON:
    - q: termo de busca (obrigatório)
    - ll: coordenadas no formato "@lat,lng,zoom" (opcional)
    - api_key: chave da SerpAPI (obrigatório)
    
    Retorna:
    - JSON com todos os resultados concatenados de todas as páginas
    """
    try:
        # Obter dados da requisição
        data = request.json
        if not data:
            return jsonify({"error": "JSON body é obrigatório"}), 400
        
        # Validar parâmetros obrigatórios
        query = data.get("q")
        api_key = data.get("api_key")
        
        if not query:
            return jsonify({"error": "Parâmetro 'q' (termo de busca) é obrigatório"}), 400
        
        if not api_key:
            return jsonify({"error": "Parâmetro 'api_key' é obrigatório"}), 400
        
        # Parâmetros opcionais
        ll = data.get("ll")  # coordenadas
        
        # Configurar parâmetros base para a SerpAPI
        base_params = {
            "engine": "google_maps",
            "q": query,
            "api_key": api_key
        }
        
        # Adicionar coordenadas se fornecidas
        if ll:
            base_params["ll"] = ll
        
        # Lista para armazenar todos os resultados
        all_results = []
        
        # Metadados da primeira busca
        search_metadata = None
        search_parameters = None
        search_information = None
        
        # Variáveis para controle de paginação
        start = 0
        page_count = 0
        max_pages = 50  # Limite de segurança para evitar loops infinitos
        
        print(f"Iniciando busca para: {query}")
        
        while page_count < max_pages:
            # Adicionar parâmetro de offset
            params = base_params.copy()
            params["start"] = start
            
            print(f"Buscando página {page_count + 1} (start={start})")
            
            # Fazer requisição para SerpAPI
            response = requests.get("https://serpapi.com/search.json", params=params)
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code != 200:
                return jsonify({
                    "error": f"Erro na SerpAPI: {response.status_code}",
                    "message": response.text
                }), 500
            
            # Parsear resposta JSON
            result_data = response.json()
            
            # Verificar se há erro na resposta da SerpAPI
            if "error" in result_data:
                return jsonify({
                    "error": "Erro da SerpAPI",
                    "serpapi_error": result_data["error"]
                }), 400
            
            # Salvar metadados da primeira página
            if page_count == 0:
                search_metadata = result_data.get("search_metadata", {})
                search_parameters = result_data.get("search_parameters", {})
                search_information = result_data.get("search_information", {})
            
            # Obter resultados locais desta página
            local_results = result_data.get("local_results", [])
            
            # Se não há resultados nesta página, parar
            if not local_results:
                print(f"Nenhum resultado encontrado na página {page_count + 1}")
                break
            
            # Adicionar resultados à lista geral
            all_results.extend(local_results)
            print(f"Página {page_count + 1}: {len(local_results)} resultados encontrados")
            
            # Verificar se há próxima página
            serpapi_pagination = result_data.get("serpapi_pagination", {})
            if "next" not in serpapi_pagination:
                print("Não há mais páginas disponíveis")
                break
            
            # Incrementar para próxima página
            start += 20  # SerpAPI retorna 20 resultados por página para Google Maps
            page_count += 1
        
        # Preparar resposta final
        final_response = {
            "search_metadata": search_metadata,
            "search_parameters": search_parameters,
            "search_information": search_information,
            "pagination_info": {
                "total_pages_processed": page_count + 1,
                "total_results": len(all_results),
                "results_per_page": 20
            },
            "local_results": all_results
        }
        
        print(f"Busca concluída: {len(all_results)} resultados em {page_count + 1} páginas")
        
        return jsonify(final_response)
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Erro de conexão com SerpAPI",
            "message": str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e)
        }), 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
