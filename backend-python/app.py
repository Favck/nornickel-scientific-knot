import os
import tempfile

import requests
import streamlit as st
import streamlit.components.v1 as components
from loguru import logger
from pyvis.network import Network

from ml.search import Search

st.set_page_config(
    page_title="Научный клубок | Поиск",
    page_icon="🕸️",
    layout="wide"
)


class GoSearchClient:
    """Клиент для взаимодействия с Go-бэкендом."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.search_endpoint = f"{self.base_url}/api/v1/search"

    def search(self, payload: dict) -> dict:
        """Отправляет POST-запрос с вектором и фильтрами на бэкенд."""
        try:
            logger.info(f"Отправка запроса на {self.search_endpoint}...")
            response = requests.post(self.search_endpoint, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Go-бэкенду: {e}")
            return None


class GraphVisualizer:
    """Класс для отрисовки интерактивных графов с помощью Pyvis."""
    
    COLORS = {
        "Process": "#4EA8DE",
        "Material": "#56CFE1",
        "Property": "#72EFDD"
    }

    @staticmethod
    def render_mock() -> str:
        """Генерирует фейковый граф для демонстрации интерфейса."""
        net = Network(
            height="600px", 
            width="100%", 
            bgcolor="#0E1117",
            font_color="white",
            directed=True
        )
        
        net.add_node(
            1, label="Выщелачивание", color=GraphVisualizer.COLORS["Process"], 
            title="Процесс: Выщелачивание\nСтатус: Изучено"
        )
        net.add_node(
            2, label="Файнштейн", color=GraphVisualizer.COLORS["Material"], 
            title="Материал: Файнштейн"
        )
        net.add_node(
            3, label="ОВП", color=GraphVisualizer.COLORS["Property"], 
            title="Параметр: ОВП\nДиапазон: 200-300 мг/л"
        )
        
        net.add_edge(1, 2)
        net.add_edge(1, 3)
        
        tmp_path = os.path.join(tempfile.gettempdir(), "mock_graph.html")
        net.save_graph(tmp_path)
        return tmp_path

    @staticmethod
    def render_real_graph(backend_data: dict) -> str:
        """Генерирует граф на основе реальных данных от Go-бэкенда."""
        net = Network(
            height="600px", 
            width="100%", 
            bgcolor="#0E1117",
            font_color="white",
            directed=True
        )
        
        nodes = backend_data.get("nodes", [])
        edges = backend_data.get("edges", [])
        
        for node in nodes:
            node_id = node.get("id")
            node_label = node.get("label", "Unknown")
            node_type = node.get("group", node.get("type", "Process")) 
            
            color = GraphVisualizer.COLORS.get(node_type, "#999999")
            
            # Формируем тултип из всех свойств
            props = node.get("properties", {})
            title_lines = [f"{node_type}: {node_label}"]
            for k, v in props.items():
                title_lines.append(f"{k}: {v}")
            title = "\n".join(title_lines)
            
            net.add_node(
                node_id,
                label=node_label,
                color=color,
                title=title
            )
            
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            rel_type = edge.get("type", "")
            
            color = "#ff4d4d" if rel_type == "contradicts" else "#97c2fc"
            dashes = True if rel_type == "contradicts" else False
            
            net.add_edge(source, target, label=rel_type, color=color, dashes=dashes)
            
        tmp_path = os.path.join(tempfile.gettempdir(), "real_graph.html")
        net.save_graph(tmp_path)
        return tmp_path

    @staticmethod
    def display_html(filepath: str, height: int = 650):
        """Читает HTML файл графа и встраивает его в Streamlit."""
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=height)


class StreamlitApp:
    """Главный класс-оркестратор Streamlit приложения."""

    def __init__(self):
        self.search_engine = self._load_search_engine()
        self.api_client = GoSearchClient()

    @staticmethod
    @st.cache_resource
    def _load_search_engine() -> Search:
        """Загружает ML-компоненты поиска в кэш Streamlit."""
        logger.info("Инициализация ML-движка поиска...")
        return Search()

    def _fetch_search_data(self, query: str) -> dict:
        """Обрабатывает поисковый запрос и дергает ML + бэкенд."""
        logger.info(f"Получен поисковый запрос: {query}")
        
        with st.spinner("Извлечение фильтров и построение вектора (ML)..."):
            search_result = self.search_engine.process_query(query)
            
        st.session_state["ml_debug"] = {
            "clean_query_text": search_result.get("clean_query_text"),
            "filters": search_result.get("filters"),
            "query_vector_length": len(search_result.get("query_vector", [])),
            "query_vector_preview": search_result.get("query_vector", [])[:5]
        }
        
        with st.spinner("Поиск связей в графе..."):
            api_response = self.api_client.search(search_result)
            
        return api_response

    def _generate_markdown_report(self, nodes: list) -> str:
        """Генерирует Markdown отчет по узлам графа."""
        report = "# Отчет по результатам поиска\n\n"
        for node in nodes:
            label = node.get("label", "Unknown")
            ntype = node.get("group", node.get("type", "Process"))
            props = node.get("properties", {})
            
            report += f"## {label} ({ntype})\n"
            for k, v in props.items():
                report += f"- **{k}**: {v}\n"
            report += "\n"
        return report

    def _render_sidebar(self):
        """Отрисовывает боковую панель."""
        st.sidebar.title("📥 Загрузка статей")
        uploaded_file = st.sidebar.file_uploader(
            "Загрузить научную статью", 
            type=["docx", "pdf"],
            help="Файл будет отправлен в фоновый ETL-пайплайн (inbound/)"
        )
        
        if uploaded_file is not None:
            os.makedirs("inbound", exist_ok=True)
            file_path = os.path.join("inbound", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.sidebar.success(f"Файл {uploaded_file.name} сохранен и передан в очередь!")

        st.sidebar.divider()
        st.sidebar.title("🔍 Детали узла")
        
        api_response = st.session_state.get("api_response")
        selected_label = st.session_state.get("node_selectbox_key")
        
        if api_response and selected_label:
            nodes = api_response.get("nodes", [])
            node = next((n for n in nodes if f"{n.get('label')} ({n.get('group', n.get('type', 'Unknown'))})" == selected_label), None)
            
            if node:
                st.sidebar.subheader(f"{node.get('label')}")
                st.sidebar.caption(f"Тип: {node.get('group', node.get('type', 'Unknown'))}")
                
                props = node.get("properties", {})
                if props:
                    for k, v in props.items():
                        st.sidebar.markdown(f"**{k}:** {v}")
                else:
                    st.sidebar.markdown("*Нет дополнительных свойств*")
            else:
                st.sidebar.markdown("Здесь будет отображаться подробная информация по выбранному узлу.")
        else:
            st.sidebar.markdown("Здесь будет отображаться подробная информация по выбранному узлу.")

    def _render_header(self):
        """Отрисовывает шапку приложения."""
        st.title("🕸️ Научный клубок R&D")
        st.markdown("Интерактивный семантический поиск по базе знаний.")

    def _render_results_from_state(self):
        """Отрисовывает результаты (граф и детали) из стейта."""
        st.info(f"**Текущий запрос:** {st.session_state.get('search_query', '')}")
        
        api_response = st.session_state.get("api_response")
        
        if api_response:
            st.success("Граф успешно загружен!")
            graph_path = GraphVisualizer.render_real_graph(api_response)
        else:
            st.error("Не удалось получить данные от бэкенда. Показываем тестовый граф.")
            # Делаем фейковый ответ, чтобы селектбокс не падал
            api_response = {
                "nodes": [
                    {"id": 1, "label": "Выщелачивание", "group": "Process", "properties": {"Статус": "Изучено"}},
                    {"id": 2, "label": "Файнштейн", "group": "Material", "properties": {}},
                    {"id": 3, "label": "ОВП", "group": "Property", "properties": {"Диапазон": "200-300 мг/л"}},
                ],
                "edges": []
            }
            st.session_state["api_response"] = api_response
            graph_path = GraphVisualizer.render_mock()
            
        with st.expander("Посмотреть результат работы ML (Отладка)"):
            st.json(st.session_state.get("ml_debug", {}))
            
        # Рендер графа
        GraphVisualizer.display_html(graph_path)
        
        # Интерактивность под графом
        st.divider()
        st.markdown("### Анализ результатов")
        
        nodes = api_response.get("nodes", [])
        options = [""] + [f"{n.get('label')} ({n.get('group', n.get('type', 'Unknown'))})" for n in nodes]
        
        col_select, col_export = st.columns([3, 1])
        with col_select:
            st.selectbox(
                "Выберите узел для просмотра деталей в панели слева:", 
                options, 
                key="node_selectbox_key"
            )
            
        with col_export:
            st.write("") # Отступ
            md_report = self._generate_markdown_report(nodes)
            st.download_button(
                label="📥 Скачать Markdown отчет",
                data=md_report,
                file_name="nornickel_rd_report.md",
                mime="text/markdown",
                use_container_width=True
            )

    def run(self):
        """Точка входа для запуска отрисовки всего приложения."""
        self._render_header()

        search_query = st.text_input(
            "Введите запрос (например: 'Очистка сточных вод сульфаты <250 мг/л')", 
            placeholder="Искать..."
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.button("Искать в графе", type="primary")

        st.divider()

        # Если нажата кнопка поиска — обрабатываем запрос и кладем результат в стейт
        if search_button and search_query:
            st.session_state["search_query"] = search_query
            st.session_state["api_response"] = self._fetch_search_data(search_query)

        # Рендерим сайдбар
        self._render_sidebar()

        # Рендерим результаты
        if "api_response" in st.session_state:
            self._render_results_from_state()
        elif search_button and not search_query:
            st.warning("Пожалуйста, введите поисковый запрос.")
        else:
            st.markdown("### Поисковая выдача")
            st.write("Введите запрос, чтобы построить граф связей.")
            graph_path = GraphVisualizer.render_mock()
            GraphVisualizer.display_html(graph_path)


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
