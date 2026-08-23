// Curated translations for page-level console content. Product and protocol names stay unchanged.

const PAGE_LOCALE_TRANSLATIONS = {
    en: {
        clear_all: 'Clear all',
        'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Not connected', 'logs.waiting': 'Waiting for logs...',
        'models.virtual_model': 'Virtual Model', 'models.not_configured': 'Not configured', 'models.virtual_model_description': 'Use omway in OpenAI, Anthropic, or Google GenAI clients. Requests try the selected models from top to bottom.', 'models.provider_models': 'Provider Models', 'models.search_models': 'Search models', 'models.unavailable_routes': 'Unavailable Model Routes',
        'about.project': 'Project', 'about.project_description': 'Omni Gateway provides one management plane for routing coding-tool requests across compatible AI formats, active credential pools, and resilient fallback behavior.', 'about.repository': 'Repository', 'about.operating_model': 'Operating Model', 'about.operating_model_description': 'Core capabilities available through the routing layer.', 'about.feature_routing': 'Virtual model orchestration and smart auto-fallback', 'about.feature_tokens': 'Token-aware cleanup and usage visibility', 'about.feature_credentials': 'OAuth accounts, API keys, and local model servers in one pool', 'about.feature_translation': 'OpenAI, Anthropic, Google GenAI, and provider-native format translation',
        'dashboard.requests_period': 'Requests {period}', 'dashboard.tokens_period': 'Tokens {period}', 'dashboard.period_1d': 'in the last 24 hours', 'dashboard.period_7d': 'in the last 7 days', 'dashboard.period_30d': 'in the last 30 days', 'dashboard.period_all': 'across all recorded time', 'dashboard.breakdown_1d': '24-Hour Request Breakdown', 'dashboard.breakdown_7d': '7-Day Request Breakdown', 'dashboard.breakdown_30d': '30-Day Request Breakdown', 'dashboard.breakdown_all': 'All-Time Request Breakdown', 'dashboard.breakdown_description': 'Review provider and credential traffic {period}.', 'dashboard.successful_failed': '{successful} successful / {failed} failed', 'dashboard.success_rate': 'Success rate', 'dashboard.no_traffic_yet': 'No traffic yet', 'dashboard.requests_succeeded': '{successful} of {total} requests succeeded.', 'dashboard.active_total_credentials': 'Active / total credentials', 'dashboard.disabled_count': '{count} disabled', 'dashboard.requests_per_credential': 'Requests per active credential', 'dashboard.assigned_requests': '{count} assigned requests', 'dashboard.tokens_per_request': 'Tokens per successful request', 'dashboard.input_output': 'Input {input} / output {output}', 'dashboard.cache_savings': 'Cached {cached} / estimated savings {savings}', 'dashboard.api_integration': 'API Integration', 'dashboard.api_integration_description': 'Copy the API key and SDK base URLs used by compatible clients.', 'dashboard.sdk_setup': 'SDK Setup', 'dashboard.sdk_setup_description': 'Select a language to view the client configuration for each supported SDK.', 'dashboard.client_language': 'Client language', 'dashboard.historical_usage': 'Historical Credential Usage', 'dashboard.historical_usage_description': 'Review retained, anonymized traffic from credentials that are no longer available in the pool.', 'dashboard.no_credential': 'No credential assigned', 'dashboard.requests_count': '{count} requests', 'dashboard.success_count': '{count} successful / {failed} failed', 'dashboard.succeeded_count': '{successful} of {total} succeeded', 'dashboard.no_traffic_recorded': 'No traffic recorded', 'dashboard.tokens_total': '{count} total', 'dashboard.token_details': 'Input {input} / output {output} / estimated savings {savings}', 'dashboard.active_credentials_count': '{count} active credential', 'dashboard.active_credentials_count_plural': '{count} active credentials', 'dashboard.no_active_credentials': 'No active credentials', 'dashboard.no_traffic': 'No traffic'
    },
    'zh-CN': {
        clear_all: '全部清除', 'logs.websocket': 'WebSocket：', 'logs.not_connected': '未连接', 'logs.waiting': '正在等待日志...', 'models.virtual_model': '虚拟模型', 'models.not_configured': '尚未配置', 'models.virtual_model_description': '在 OpenAI、Anthropic 或 Google GenAI 客户端中使用 omway。请求会按顺序尝试已选择的模型。', 'models.provider_models': '提供商模型', 'models.search_models': '搜索模型', 'models.unavailable_routes': '不可用的模型路由', 'about.project': '项目', 'about.project_description': 'Omni Gateway 提供统一的管理平面，用于在兼容的 AI 格式、有效凭据池和弹性故障转移机制之间路由编码工具请求。', 'about.repository': '代码仓库', 'about.operating_model': '运行模式', 'about.operating_model_description': '路由层提供的核心能力。', 'about.feature_routing': '虚拟模型编排与智能自动故障转移', 'about.feature_tokens': '令牌感知清理与用量可见性', 'about.feature_credentials': '在一个凭据池中管理 OAuth 账户、API 密钥和本地模型服务器', 'about.feature_translation': 'OpenAI、Anthropic、Google GenAI 与提供商原生格式转换', 'dashboard.requests_period': '请求数（{period}）', 'dashboard.tokens_period': '令牌数（{period}）', 'dashboard.period_1d': '过去 24 小时', 'dashboard.period_7d': '过去 7 天', 'dashboard.period_30d': '过去 30 天', 'dashboard.period_all': '全部已记录时间', 'dashboard.breakdown_1d': '24 小时请求明细', 'dashboard.breakdown_7d': '7 天请求明细', 'dashboard.breakdown_30d': '30 天请求明细', 'dashboard.breakdown_all': '全部时间请求明细', 'dashboard.breakdown_description': '查看{period}的提供商与凭据流量。', 'dashboard.successful_failed': '成功 {successful} / 失败 {failed}', 'dashboard.success_rate': '成功率', 'dashboard.no_traffic_yet': '暂无流量', 'dashboard.requests_succeeded': '{total} 个请求中有 {successful} 个成功。', 'dashboard.active_total_credentials': '有效凭据 / 凭据总数', 'dashboard.disabled_count': '已停用 {count} 个', 'dashboard.requests_per_credential': '每个有效凭据的请求数', 'dashboard.assigned_requests': '已分配 {count} 个请求', 'dashboard.tokens_per_request': '每个成功请求的令牌数', 'dashboard.input_output': '输入 {input} / 输出 {output}', 'dashboard.cache_savings': '缓存 {cached} / 预计节省 {savings}', 'dashboard.api_integration': 'API 集成', 'dashboard.api_integration_description': '复制兼容客户端使用的 API 密钥和 SDK 基础 URL。', 'dashboard.sdk_setup': 'SDK 设置', 'dashboard.sdk_setup_description': '选择语言以查看各个受支持 SDK 的客户端配置。', 'dashboard.client_language': '客户端语言', 'dashboard.historical_usage': '历史凭据用量', 'dashboard.historical_usage_description': '查看已不在凭据池中的凭据所保留的匿名流量。', 'dashboard.no_credential': '未分配凭据', 'dashboard.requests_count': '{count} 个请求', 'dashboard.success_count': '成功 {count} / 失败 {failed}', 'dashboard.succeeded_count': '{total} 个中成功 {successful} 个', 'dashboard.no_traffic_recorded': '没有流量记录', 'dashboard.tokens_total': '共 {count}', 'dashboard.token_details': '输入 {input} / 输出 {output} / 预计节省 {savings}', 'dashboard.active_credentials_count': '{count} 个有效凭据', 'dashboard.active_credentials_count_plural': '{count} 个有效凭据', 'dashboard.no_active_credentials': '没有有效凭据', 'dashboard.no_traffic': '无流量'
    },
    'zh-TW': {
        clear_all: '全部清除', 'logs.websocket': 'WebSocket：', 'logs.not_connected': '未連線', 'logs.waiting': '正在等待日誌...', 'models.virtual_model': '虛擬模型', 'models.not_configured': '尚未設定', 'models.virtual_model_description': '在 OpenAI、Anthropic 或 Google GenAI 用戶端中使用 omway。請求會依序嘗試已選取的模型。', 'models.provider_models': '供應商模型', 'models.search_models': '搜尋模型', 'models.unavailable_routes': '無法使用的模型路由', 'about.project': '專案', 'about.project_description': 'Omni Gateway 提供統一的管理平面，用於在相容的 AI 格式、有效憑證集區與彈性容錯機制之間路由程式開發工具的請求。', 'about.repository': '程式碼儲存庫', 'about.operating_model': '運作模式', 'about.operating_model_description': '路由層提供的核心功能。', 'about.feature_routing': '虛擬模型協調與智慧自動容錯', 'about.feature_tokens': '權杖感知清理與用量可見性', 'about.feature_credentials': '在單一集區中管理 OAuth 帳戶、API 金鑰與本機模型伺服器', 'about.feature_translation': 'OpenAI、Anthropic、Google GenAI 與供應商原生格式轉換', 'dashboard.requests_period': '請求數（{period}）', 'dashboard.tokens_period': '權杖數（{period}）', 'dashboard.period_1d': '過去 24 小時', 'dashboard.period_7d': '過去 7 天', 'dashboard.period_30d': '過去 30 天', 'dashboard.period_all': '所有已記錄期間', 'dashboard.breakdown_1d': '24 小時請求明細', 'dashboard.breakdown_7d': '7 天請求明細', 'dashboard.breakdown_30d': '30 天請求明細', 'dashboard.breakdown_all': '所有期間請求明細', 'dashboard.breakdown_description': '檢視{period}的供應商與憑證流量。', 'dashboard.successful_failed': '成功 {successful} / 失敗 {failed}', 'dashboard.success_rate': '成功率', 'dashboard.no_traffic_yet': '目前沒有流量', 'dashboard.requests_succeeded': '{total} 個請求中有 {successful} 個成功。', 'dashboard.active_total_credentials': '有效憑證 / 憑證總數', 'dashboard.disabled_count': '已停用 {count} 個', 'dashboard.requests_per_credential': '每個有效憑證的請求數', 'dashboard.assigned_requests': '已指派 {count} 個請求', 'dashboard.tokens_per_request': '每個成功請求的權杖數', 'dashboard.input_output': '輸入 {input} / 輸出 {output}', 'dashboard.cache_savings': '快取 {cached} / 預估節省 {savings}', 'dashboard.api_integration': 'API 整合', 'dashboard.api_integration_description': '複製相容用戶端使用的 API 金鑰與 SDK 基礎 URL。', 'dashboard.sdk_setup': 'SDK 設定', 'dashboard.sdk_setup_description': '選擇語言以檢視各個支援 SDK 的用戶端設定。', 'dashboard.client_language': '用戶端語言', 'dashboard.historical_usage': '歷史憑證用量', 'dashboard.historical_usage_description': '檢視已不在憑證集區中的憑證所保留的匿名流量。', 'dashboard.no_credential': '未指派憑證', 'dashboard.requests_count': '{count} 個請求', 'dashboard.success_count': '成功 {count} / 失敗 {failed}', 'dashboard.succeeded_count': '{total} 個中成功 {successful} 個', 'dashboard.no_traffic_recorded': '沒有流量記錄', 'dashboard.tokens_total': '共 {count}', 'dashboard.token_details': '輸入 {input} / 輸出 {output} / 預估節省 {savings}', 'dashboard.active_credentials_count': '{count} 個有效憑證', 'dashboard.active_credentials_count_plural': '{count} 個有效憑證', 'dashboard.no_active_credentials': '沒有有效憑證', 'dashboard.no_traffic': '無流量'
    },
    de: {
        clear_all: 'Alle löschen', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Nicht verbunden', 'logs.waiting': 'Warten auf Protokolle...', 'models.virtual_model': 'Virtuelles Modell', 'models.not_configured': 'Nicht konfiguriert', 'models.virtual_model_description': 'Verwenden Sie omway in OpenAI-, Anthropic- oder Google-GenAI-Clients. Anfragen durchlaufen die ausgewählten Modelle der Reihe nach.', 'models.provider_models': 'Provider-Modelle', 'models.search_models': 'Modelle suchen', 'models.unavailable_routes': 'Nicht verfügbare Modellrouten', 'about.project': 'Projekt', 'about.project_description': 'Omni Gateway bietet eine zentrale Verwaltungsebene, die Anfragen von Coding-Tools über kompatible KI-Formate, aktive Zugangspools und ausfallsicheres Fallback routet.', 'about.repository': 'Repository', 'about.operating_model': 'Funktionsweise', 'about.operating_model_description': 'Kernfunktionen der Routing-Schicht.', 'about.feature_routing': 'Orchestrierung virtueller Modelle und intelligentes Auto-Failover', 'about.feature_tokens': 'Tokenbewusste Bereinigung und Nutzungsübersicht', 'about.feature_credentials': 'OAuth-Konten, API-Schlüssel und lokale Modellserver in einem Pool', 'about.feature_translation': 'Formatübersetzung für OpenAI, Anthropic, Google GenAI und native Provider-Protokolle', 'dashboard.requests_period': 'Anfragen {period}', 'dashboard.tokens_period': 'Token {period}', 'dashboard.period_1d': 'in den letzten 24 Stunden', 'dashboard.period_7d': 'in den letzten 7 Tagen', 'dashboard.period_30d': 'in den letzten 30 Tagen', 'dashboard.period_all': 'im gesamten Aufzeichnungszeitraum', 'dashboard.breakdown_1d': 'Anfragen der letzten 24 Stunden', 'dashboard.breakdown_7d': 'Anfragen der letzten 7 Tage', 'dashboard.breakdown_30d': 'Anfragen der letzten 30 Tage', 'dashboard.breakdown_all': 'Anfragen im Gesamtzeitraum', 'dashboard.breakdown_description': 'Provider- und Zugangsdatenverkehr {period} prüfen.', 'dashboard.successful_failed': '{successful} erfolgreich / {failed} fehlgeschlagen', 'dashboard.success_rate': 'Erfolgsquote', 'dashboard.no_traffic_yet': 'Noch kein Traffic', 'dashboard.requests_succeeded': '{successful} von {total} Anfragen waren erfolgreich.', 'dashboard.active_total_credentials': 'Aktive / gesamte Zugänge', 'dashboard.disabled_count': '{count} deaktiviert', 'dashboard.requests_per_credential': 'Anfragen pro aktivem Zugang', 'dashboard.assigned_requests': '{count} zugewiesene Anfragen', 'dashboard.tokens_per_request': 'Token pro erfolgreicher Anfrage', 'dashboard.input_output': 'Eingabe {input} / Ausgabe {output}', 'dashboard.cache_savings': 'Im Cache {cached} / geschätzte Ersparnis {savings}', 'dashboard.api_integration': 'API-Integration', 'dashboard.api_integration_description': 'API-Schlüssel und SDK-Basis-URLs für kompatible Clients kopieren.', 'dashboard.sdk_setup': 'SDK-Einrichtung', 'dashboard.sdk_setup_description': 'Wählen Sie eine Sprache, um die Clientkonfiguration der unterstützten SDKs anzuzeigen.', 'dashboard.client_language': 'Clientsprache', 'dashboard.historical_usage': 'Historische Zugangsnutzung', 'dashboard.historical_usage_description': 'Anonymisierten, aufbewahrten Traffic von Zugängen prüfen, die nicht mehr im Pool vorhanden sind.', 'dashboard.no_credential': 'Kein Zugang zugewiesen', 'dashboard.requests_count': '{count} Anfragen', 'dashboard.success_count': '{count} erfolgreich / {failed} fehlgeschlagen', 'dashboard.succeeded_count': '{successful} von {total} erfolgreich', 'dashboard.no_traffic_recorded': 'Kein Traffic aufgezeichnet', 'dashboard.tokens_total': '{count} insgesamt', 'dashboard.token_details': 'Eingabe {input} / Ausgabe {output} / geschätzte Ersparnis {savings}', 'dashboard.active_credentials_count': '{count} aktiver Zugang', 'dashboard.active_credentials_count_plural': '{count} aktive Zugänge', 'dashboard.no_active_credentials': 'Keine aktiven Zugänge', 'dashboard.no_traffic': 'Kein Traffic'
    },
    es: {
        clear_all: 'Limpiar todo', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Sin conexión', 'logs.waiting': 'Esperando registros...', 'models.virtual_model': 'Modelo virtual', 'models.not_configured': 'Sin configurar', 'models.virtual_model_description': 'Usa omway en clientes OpenAI, Anthropic o Google GenAI. Las solicitudes prueban los modelos seleccionados en orden.', 'models.provider_models': 'Modelos de proveedores', 'models.search_models': 'Buscar modelos', 'models.unavailable_routes': 'Rutas de modelo no disponibles', 'about.project': 'Proyecto', 'about.project_description': 'Omni Gateway ofrece un único plano de administración para enrutar solicitudes de herramientas de programación entre formatos de IA compatibles, pools de credenciales activos y mecanismos de respaldo resistentes.', 'about.repository': 'Repositorio', 'about.operating_model': 'Modelo operativo', 'about.operating_model_description': 'Capacidades principales de la capa de enrutamiento.', 'about.feature_routing': 'Orquestación de modelos virtuales y conmutación automática inteligente', 'about.feature_tokens': 'Limpieza basada en tokens y visibilidad del uso', 'about.feature_credentials': 'Cuentas OAuth, claves API y servidores de modelos locales en un solo pool', 'about.feature_translation': 'Traducción de formatos OpenAI, Anthropic, Google GenAI y nativos de proveedores', 'dashboard.requests_period': 'Solicitudes {period}', 'dashboard.tokens_period': 'Tokens {period}', 'dashboard.period_1d': 'en las últimas 24 horas', 'dashboard.period_7d': 'en los últimos 7 días', 'dashboard.period_30d': 'en los últimos 30 días', 'dashboard.period_all': 'en todo el periodo registrado', 'dashboard.breakdown_1d': 'Desglose de solicitudes de 24 horas', 'dashboard.breakdown_7d': 'Desglose de solicitudes de 7 días', 'dashboard.breakdown_30d': 'Desglose de solicitudes de 30 días', 'dashboard.breakdown_all': 'Desglose de solicitudes histórico', 'dashboard.breakdown_description': 'Consulta el tráfico de proveedores y credenciales {period}.', 'dashboard.successful_failed': '{successful} correctas / {failed} fallidas', 'dashboard.success_rate': 'Tasa de éxito', 'dashboard.no_traffic_yet': 'Aún no hay tráfico', 'dashboard.requests_succeeded': '{successful} de {total} solicitudes se completaron correctamente.', 'dashboard.active_total_credentials': 'Credenciales activas / totales', 'dashboard.disabled_count': '{count} desactivadas', 'dashboard.requests_per_credential': 'Solicitudes por credencial activa', 'dashboard.assigned_requests': '{count} solicitudes asignadas', 'dashboard.tokens_per_request': 'Tokens por solicitud correcta', 'dashboard.input_output': 'Entrada {input} / salida {output}', 'dashboard.cache_savings': 'En caché {cached} / ahorro estimado {savings}', 'dashboard.api_integration': 'Integración de API', 'dashboard.api_integration_description': 'Copia la clave API y las URL base de los SDK para clientes compatibles.', 'dashboard.sdk_setup': 'Configuración de SDK', 'dashboard.sdk_setup_description': 'Elige un lenguaje para ver la configuración de cliente de cada SDK compatible.', 'dashboard.client_language': 'Lenguaje del cliente', 'dashboard.historical_usage': 'Uso histórico de credenciales', 'dashboard.historical_usage_description': 'Consulta el tráfico anonimizado conservado de credenciales que ya no están en el pool.', 'dashboard.no_credential': 'Sin credencial asignada', 'dashboard.requests_count': '{count} solicitudes', 'dashboard.success_count': '{count} correctas / {failed} fallidas', 'dashboard.succeeded_count': '{successful} de {total} correctas', 'dashboard.no_traffic_recorded': 'Sin tráfico registrado', 'dashboard.tokens_total': '{count} en total', 'dashboard.token_details': 'Entrada {input} / salida {output} / ahorro estimado {savings}', 'dashboard.active_credentials_count': '{count} credencial activa', 'dashboard.active_credentials_count_plural': '{count} credenciales activas', 'dashboard.no_active_credentials': 'Sin credenciales activas', 'dashboard.no_traffic': 'Sin tráfico'
    },
    fr: {
        clear_all: 'Tout effacer', 'logs.websocket': 'WebSocket :', 'logs.not_connected': 'Non connecté', 'logs.waiting': 'En attente de journaux...', 'models.virtual_model': 'Modèle virtuel', 'models.not_configured': 'Non configuré', 'models.virtual_model_description': 'Utilisez omway dans les clients OpenAI, Anthropic ou Google GenAI. Les requêtes essaient les modèles sélectionnés dans l’ordre.', 'models.provider_models': 'Modèles fournisseurs', 'models.search_models': 'Rechercher des modèles', 'models.unavailable_routes': 'Routes de modèles indisponibles', 'about.project': 'Projet', 'about.project_description': 'Omni Gateway fournit un plan de gestion unique pour acheminer les requêtes des outils de développement entre formats IA compatibles, pools d’identifiants actifs et mécanismes de repli résilients.', 'about.repository': 'Dépôt', 'about.operating_model': 'Mode de fonctionnement', 'about.operating_model_description': 'Fonctions essentielles disponibles dans la couche de routage.', 'about.feature_routing': 'Orchestration de modèles virtuels et basculement automatique intelligent', 'about.feature_tokens': 'Nettoyage tenant compte des tokens et visibilité de l’utilisation', 'about.feature_credentials': 'Comptes OAuth, clés API et serveurs de modèles locaux dans un même pool', 'about.feature_translation': 'Traduction des formats OpenAI, Anthropic, Google GenAI et natifs des fournisseurs', 'dashboard.requests_period': 'Requêtes {period}', 'dashboard.tokens_period': 'Tokens {period}', 'dashboard.period_1d': 'sur les dernières 24 heures', 'dashboard.period_7d': 'sur les 7 derniers jours', 'dashboard.period_30d': 'sur les 30 derniers jours', 'dashboard.period_all': 'sur toute la période enregistrée', 'dashboard.breakdown_1d': 'Répartition des requêtes sur 24 heures', 'dashboard.breakdown_7d': 'Répartition des requêtes sur 7 jours', 'dashboard.breakdown_30d': 'Répartition des requêtes sur 30 jours', 'dashboard.breakdown_all': 'Répartition de toutes les requêtes', 'dashboard.breakdown_description': 'Consultez le trafic des fournisseurs et des identifiants {period}.', 'dashboard.successful_failed': '{successful} réussies / {failed} échouées', 'dashboard.success_rate': 'Taux de réussite', 'dashboard.no_traffic_yet': 'Aucun trafic pour le moment', 'dashboard.requests_succeeded': '{successful} requêtes réussies sur {total}.', 'dashboard.active_total_credentials': 'Identifiants actifs / total', 'dashboard.disabled_count': '{count} désactivés', 'dashboard.requests_per_credential': 'Requêtes par identifiant actif', 'dashboard.assigned_requests': '{count} requêtes attribuées', 'dashboard.tokens_per_request': 'Tokens par requête réussie', 'dashboard.input_output': 'Entrée {input} / sortie {output}', 'dashboard.cache_savings': 'En cache {cached} / économie estimée {savings}', 'dashboard.api_integration': 'Intégration API', 'dashboard.api_integration_description': 'Copiez la clé API et les URL de base des SDK utilisées par les clients compatibles.', 'dashboard.sdk_setup': 'Configuration des SDK', 'dashboard.sdk_setup_description': 'Choisissez un langage pour afficher la configuration client de chaque SDK pris en charge.', 'dashboard.client_language': 'Langage client', 'dashboard.historical_usage': 'Utilisation historique des identifiants', 'dashboard.historical_usage_description': 'Consultez le trafic anonymisé conservé pour les identifiants qui ne figurent plus dans le pool.', 'dashboard.no_credential': 'Aucun identifiant attribué', 'dashboard.requests_count': '{count} requêtes', 'dashboard.success_count': '{count} réussies / {failed} échouées', 'dashboard.succeeded_count': '{successful} réussies sur {total}', 'dashboard.no_traffic_recorded': 'Aucun trafic enregistré', 'dashboard.tokens_total': '{count} au total', 'dashboard.token_details': 'Entrée {input} / sortie {output} / économie estimée {savings}', 'dashboard.active_credentials_count': '{count} identifiant actif', 'dashboard.active_credentials_count_plural': '{count} identifiants actifs', 'dashboard.no_active_credentials': 'Aucun identifiant actif', 'dashboard.no_traffic': 'Aucun trafic'
    },
    id: {
        clear_all: 'Hapus semua', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Belum terhubung', 'logs.waiting': 'Menunggu log...', 'models.virtual_model': 'Model Virtual', 'models.not_configured': 'Belum dikonfigurasi', 'models.virtual_model_description': 'Gunakan omway di klien OpenAI, Anthropic, atau Google GenAI. Permintaan mencoba model yang dipilih secara berurutan.', 'models.provider_models': 'Model Penyedia', 'models.search_models': 'Cari model', 'models.unavailable_routes': 'Rute Model yang Tidak Tersedia', 'about.project': 'Proyek', 'about.project_description': 'Omni Gateway menyediakan satu bidang pengelolaan untuk merutekan permintaan alat pemrograman melalui format AI yang kompatibel, pool kredensial aktif, dan mekanisme fallback yang tangguh.', 'about.repository': 'Repositori', 'about.operating_model': 'Cara Kerja', 'about.operating_model_description': 'Kemampuan utama yang tersedia melalui lapisan perutean.', 'about.feature_routing': 'Orkestrasi model virtual dan failover otomatis cerdas', 'about.feature_tokens': 'Pembersihan sadar token dan visibilitas penggunaan', 'about.feature_credentials': 'Akun OAuth, kunci API, dan server model lokal dalam satu pool', 'about.feature_translation': 'Penerjemahan format OpenAI, Anthropic, Google GenAI, dan format native penyedia', 'dashboard.requests_period': 'Permintaan {period}', 'dashboard.tokens_period': 'Token {period}', 'dashboard.period_1d': 'dalam 24 jam terakhir', 'dashboard.period_7d': 'dalam 7 hari terakhir', 'dashboard.period_30d': 'dalam 30 hari terakhir', 'dashboard.period_all': 'sepanjang waktu yang tercatat', 'dashboard.breakdown_1d': 'Rincian Permintaan 24 Jam', 'dashboard.breakdown_7d': 'Rincian Permintaan 7 Hari', 'dashboard.breakdown_30d': 'Rincian Permintaan 30 Hari', 'dashboard.breakdown_all': 'Rincian Seluruh Permintaan', 'dashboard.breakdown_description': 'Tinjau trafik penyedia dan kredensial {period}.', 'dashboard.successful_failed': '{successful} berhasil / {failed} gagal', 'dashboard.success_rate': 'Tingkat keberhasilan', 'dashboard.no_traffic_yet': 'Belum ada trafik', 'dashboard.requests_succeeded': '{successful} dari {total} permintaan berhasil.', 'dashboard.active_total_credentials': 'Kredensial aktif / total', 'dashboard.disabled_count': '{count} dinonaktifkan', 'dashboard.requests_per_credential': 'Permintaan per kredensial aktif', 'dashboard.assigned_requests': '{count} permintaan dialokasikan', 'dashboard.tokens_per_request': 'Token per permintaan berhasil', 'dashboard.input_output': 'Input {input} / output {output}', 'dashboard.cache_savings': 'Cache {cached} / perkiraan penghematan {savings}', 'dashboard.api_integration': 'Integrasi API', 'dashboard.api_integration_description': 'Salin kunci API dan URL dasar SDK yang digunakan klien kompatibel.', 'dashboard.sdk_setup': 'Penyiapan SDK', 'dashboard.sdk_setup_description': 'Pilih bahasa untuk melihat konfigurasi klien setiap SDK yang didukung.', 'dashboard.client_language': 'Bahasa klien', 'dashboard.historical_usage': 'Riwayat Penggunaan Kredensial', 'dashboard.historical_usage_description': 'Tinjau trafik anonim tersimpan dari kredensial yang tidak lagi tersedia di pool.', 'dashboard.no_credential': 'Tidak ada kredensial yang ditetapkan', 'dashboard.requests_count': '{count} permintaan', 'dashboard.success_count': '{count} berhasil / {failed} gagal', 'dashboard.succeeded_count': '{successful} dari {total} berhasil', 'dashboard.no_traffic_recorded': 'Tidak ada trafik tercatat', 'dashboard.tokens_total': '{count} total', 'dashboard.token_details': 'Input {input} / output {output} / perkiraan penghematan {savings}', 'dashboard.active_credentials_count': '{count} kredensial aktif', 'dashboard.active_credentials_count_plural': '{count} kredensial aktif', 'dashboard.no_active_credentials': 'Tidak ada kredensial aktif', 'dashboard.no_traffic': 'Tidak ada trafik'
    },
    it: {
        clear_all: 'Cancella tutto', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Non connesso', 'logs.waiting': 'In attesa dei log...', 'models.virtual_model': 'Modello virtuale', 'models.not_configured': 'Non configurato', 'models.virtual_model_description': 'Usa omway nei client OpenAI, Anthropic o Google GenAI. Le richieste provano in ordine i modelli selezionati.', 'models.provider_models': 'Modelli dei provider', 'models.search_models': 'Cerca modelli', 'models.unavailable_routes': 'Percorsi modello non disponibili', 'about.project': 'Progetto', 'about.project_description': 'Omni Gateway offre un unico piano di gestione per instradare le richieste degli strumenti di sviluppo tra formati IA compatibili, pool di credenziali attive e meccanismi di fallback resilienti.', 'about.repository': 'Repository', 'about.operating_model': 'Modello operativo', 'about.operating_model_description': 'Funzionalità principali disponibili nel livello di routing.', 'about.feature_routing': 'Orchestrazione di modelli virtuali e failover automatico intelligente', 'about.feature_tokens': 'Pulizia basata sui token e visibilità dell’utilizzo', 'about.feature_credentials': 'Account OAuth, chiavi API e server di modelli locali in un unico pool', 'about.feature_translation': 'Traduzione dei formati OpenAI, Anthropic, Google GenAI e nativi dei provider', 'dashboard.requests_period': 'Richieste {period}', 'dashboard.tokens_period': 'Token {period}', 'dashboard.period_1d': 'nelle ultime 24 ore', 'dashboard.period_7d': 'negli ultimi 7 giorni', 'dashboard.period_30d': 'negli ultimi 30 giorni', 'dashboard.period_all': 'nell’intero periodo registrato', 'dashboard.breakdown_1d': 'Riepilogo richieste di 24 ore', 'dashboard.breakdown_7d': 'Riepilogo richieste di 7 giorni', 'dashboard.breakdown_30d': 'Riepilogo richieste di 30 giorni', 'dashboard.breakdown_all': 'Riepilogo richieste complessivo', 'dashboard.breakdown_description': 'Esamina il traffico di provider e credenziali {period}.', 'dashboard.successful_failed': '{successful} riuscite / {failed} non riuscite', 'dashboard.success_rate': 'Tasso di successo', 'dashboard.no_traffic_yet': 'Nessun traffico per ora', 'dashboard.requests_succeeded': '{successful} richieste riuscite su {total}.', 'dashboard.active_total_credentials': 'Credenziali attive / totali', 'dashboard.disabled_count': '{count} disabilitate', 'dashboard.requests_per_credential': 'Richieste per credenziale attiva', 'dashboard.assigned_requests': '{count} richieste assegnate', 'dashboard.tokens_per_request': 'Token per richiesta riuscita', 'dashboard.input_output': 'Input {input} / output {output}', 'dashboard.cache_savings': 'In cache {cached} / risparmio stimato {savings}', 'dashboard.api_integration': 'Integrazione API', 'dashboard.api_integration_description': 'Copia la chiave API e gli URL di base degli SDK usati dai client compatibili.', 'dashboard.sdk_setup': 'Configurazione SDK', 'dashboard.sdk_setup_description': 'Scegli un linguaggio per vedere la configurazione client di ogni SDK supportato.', 'dashboard.client_language': 'Linguaggio client', 'dashboard.historical_usage': 'Utilizzo storico delle credenziali', 'dashboard.historical_usage_description': 'Esamina il traffico anonimizzato conservato per le credenziali non più presenti nel pool.', 'dashboard.no_credential': 'Nessuna credenziale assegnata', 'dashboard.requests_count': '{count} richieste', 'dashboard.success_count': '{count} riuscite / {failed} non riuscite', 'dashboard.succeeded_count': '{successful} riuscite su {total}', 'dashboard.no_traffic_recorded': 'Nessun traffico registrato', 'dashboard.tokens_total': '{count} totali', 'dashboard.token_details': 'Input {input} / output {output} / risparmio stimato {savings}', 'dashboard.active_credentials_count': '{count} credenziale attiva', 'dashboard.active_credentials_count_plural': '{count} credenziali attive', 'dashboard.no_active_credentials': 'Nessuna credenziale attiva', 'dashboard.no_traffic': 'Nessun traffico'
    },
    ja: {
        clear_all: 'すべて消去', 'logs.websocket': 'WebSocket：', 'logs.not_connected': '未接続', 'logs.waiting': 'ログを待機しています...', 'models.virtual_model': '仮想モデル', 'models.not_configured': '未設定', 'models.virtual_model_description': 'OpenAI、Anthropic、Google GenAI のクライアントで omway を使用できます。選択したモデルを上から順に試します。', 'models.provider_models': 'プロバイダーモデル', 'models.search_models': 'モデルを検索', 'models.unavailable_routes': '利用できないモデルルート', 'about.project': 'プロジェクト', 'about.project_description': 'Omni Gateway は、互換性のある AI 形式、有効な認証情報プール、堅牢なフォールバック機構を横断して、コーディングツールのリクエストをルーティングする一元的な管理基盤です。', 'about.repository': 'リポジトリ', 'about.operating_model': '動作モデル', 'about.operating_model_description': 'ルーティング層で利用できる主な機能です。', 'about.feature_routing': '仮想モデルのオーケストレーションとインテリジェントな自動フェイルオーバー', 'about.feature_tokens': 'トークンを考慮した整理と使用状況の可視化', 'about.feature_credentials': 'OAuth アカウント、API キー、ローカルモデルサーバーを一つのプールで管理', 'about.feature_translation': 'OpenAI、Anthropic、Google GenAI、プロバイダー固有形式の変換', 'dashboard.requests_period': 'リクエスト（{period}）', 'dashboard.tokens_period': 'トークン（{period}）', 'dashboard.period_1d': '過去 24 時間', 'dashboard.period_7d': '過去 7 日間', 'dashboard.period_30d': '過去 30 日間', 'dashboard.period_all': '記録された全期間', 'dashboard.breakdown_1d': '24 時間のリクエスト内訳', 'dashboard.breakdown_7d': '7 日間のリクエスト内訳', 'dashboard.breakdown_30d': '30 日間のリクエスト内訳', 'dashboard.breakdown_all': '全期間のリクエスト内訳', 'dashboard.breakdown_description': '{period}のプロバイダーと認証情報のトラフィックを確認します。', 'dashboard.successful_failed': '成功 {successful} / 失敗 {failed}', 'dashboard.success_rate': '成功率', 'dashboard.no_traffic_yet': 'トラフィックはまだありません', 'dashboard.requests_succeeded': '{total} 件中 {successful} 件成功しました。', 'dashboard.active_total_credentials': '有効 / 全認証情報', 'dashboard.disabled_count': '{count} 件無効', 'dashboard.requests_per_credential': '有効な認証情報あたりのリクエスト数', 'dashboard.assigned_requests': '{count} 件割り当て済み', 'dashboard.tokens_per_request': '成功したリクエストあたりのトークン数', 'dashboard.input_output': '入力 {input} / 出力 {output}', 'dashboard.cache_savings': 'キャッシュ {cached} / 推定削減量 {savings}', 'dashboard.api_integration': 'API 連携', 'dashboard.api_integration_description': '互換クライアントで使用する API キーと SDK ベース URL をコピーします。', 'dashboard.sdk_setup': 'SDK の設定', 'dashboard.sdk_setup_description': '言語を選択して、対応 SDK ごとのクライアント設定を確認します。', 'dashboard.client_language': 'クライアント言語', 'dashboard.historical_usage': '認証情報の過去の使用状況', 'dashboard.historical_usage_description': 'プールから削除された認証情報について、保持された匿名トラフィックを確認します。', 'dashboard.no_credential': '認証情報が未割り当てです', 'dashboard.requests_count': '{count} 件のリクエスト', 'dashboard.success_count': '成功 {count} / 失敗 {failed}', 'dashboard.succeeded_count': '{total} 件中 {successful} 件成功', 'dashboard.no_traffic_recorded': 'トラフィックの記録なし', 'dashboard.tokens_total': '合計 {count}', 'dashboard.token_details': '入力 {input} / 出力 {output} / 推定削減量 {savings}', 'dashboard.active_credentials_count': '有効な認証情報 {count} 件', 'dashboard.active_credentials_count_plural': '有効な認証情報 {count} 件', 'dashboard.no_active_credentials': '有効な認証情報なし', 'dashboard.no_traffic': 'トラフィックなし'
    },
    ko: {
        clear_all: '모두 지우기', 'logs.websocket': 'WebSocket:', 'logs.not_connected': '연결되지 않음', 'logs.waiting': '로그를 기다리는 중...', 'models.virtual_model': '가상 모델', 'models.not_configured': '설정되지 않음', 'models.virtual_model_description': 'OpenAI, Anthropic 또는 Google GenAI 클라이언트에서 omway를 사용하세요. 요청은 선택한 모델을 위에서부터 차례로 시도합니다.', 'models.provider_models': '공급자 모델', 'models.search_models': '모델 검색', 'models.unavailable_routes': '사용할 수 없는 모델 경로', 'about.project': '프로젝트', 'about.project_description': 'Omni Gateway는 호환 AI 형식, 활성 자격 증명 풀, 안정적인 대체 경로에 걸쳐 코딩 도구 요청을 라우팅하는 단일 관리 영역을 제공합니다.', 'about.repository': '저장소', 'about.operating_model': '운영 방식', 'about.operating_model_description': '라우팅 계층에서 제공하는 핵심 기능입니다.', 'about.feature_routing': '가상 모델 오케스트레이션 및 지능형 자동 장애 조치', 'about.feature_tokens': '토큰 기반 정리 및 사용량 가시성', 'about.feature_credentials': 'OAuth 계정, API 키, 로컬 모델 서버를 하나의 풀에서 관리', 'about.feature_translation': 'OpenAI, Anthropic, Google GenAI 및 공급자 고유 형식 변환', 'dashboard.requests_period': '요청 수({period})', 'dashboard.tokens_period': '토큰 수({period})', 'dashboard.period_1d': '최근 24시간', 'dashboard.period_7d': '최근 7일', 'dashboard.period_30d': '최근 30일', 'dashboard.period_all': '전체 기록 기간', 'dashboard.breakdown_1d': '24시간 요청 내역', 'dashboard.breakdown_7d': '7일 요청 내역', 'dashboard.breakdown_30d': '30일 요청 내역', 'dashboard.breakdown_all': '전체 요청 내역', 'dashboard.breakdown_description': '{period}의 공급자 및 자격 증명 트래픽을 확인합니다.', 'dashboard.successful_failed': '성공 {successful} / 실패 {failed}', 'dashboard.success_rate': '성공률', 'dashboard.no_traffic_yet': '아직 트래픽이 없습니다', 'dashboard.requests_succeeded': '요청 {total}건 중 {successful}건 성공했습니다.', 'dashboard.active_total_credentials': '활성 / 전체 자격 증명', 'dashboard.disabled_count': '{count}개 비활성', 'dashboard.requests_per_credential': '활성 자격 증명당 요청 수', 'dashboard.assigned_requests': '{count}개 요청 할당됨', 'dashboard.tokens_per_request': '성공한 요청당 토큰 수', 'dashboard.input_output': '입력 {input} / 출력 {output}', 'dashboard.cache_savings': '캐시 {cached} / 예상 절감 {savings}', 'dashboard.api_integration': 'API 연동', 'dashboard.api_integration_description': '호환 클라이언트에서 사용하는 API 키와 SDK 기본 URL을 복사합니다.', 'dashboard.sdk_setup': 'SDK 설정', 'dashboard.sdk_setup_description': '언어를 선택하여 지원되는 SDK별 클라이언트 설정을 확인합니다.', 'dashboard.client_language': '클라이언트 언어', 'dashboard.historical_usage': '과거 자격 증명 사용량', 'dashboard.historical_usage_description': '풀에서 제거된 자격 증명의 보관된 익명 트래픽을 확인합니다.', 'dashboard.no_credential': '자격 증명이 할당되지 않음', 'dashboard.requests_count': '요청 {count}건', 'dashboard.success_count': '성공 {count} / 실패 {failed}', 'dashboard.succeeded_count': '{total}건 중 {successful}건 성공', 'dashboard.no_traffic_recorded': '기록된 트래픽 없음', 'dashboard.tokens_total': '총 {count}', 'dashboard.token_details': '입력 {input} / 출력 {output} / 예상 절감 {savings}', 'dashboard.active_credentials_count': '활성 자격 증명 {count}개', 'dashboard.active_credentials_count_plural': '활성 자격 증명 {count}개', 'dashboard.no_active_credentials': '활성 자격 증명 없음', 'dashboard.no_traffic': '트래픽 없음'
    },
    pt: {
        clear_all: 'Limpar tudo', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Não conectado', 'logs.waiting': 'Aguardando logs...', 'models.virtual_model': 'Modelo virtual', 'models.not_configured': 'Não configurado', 'models.virtual_model_description': 'Use omway em clientes OpenAI, Anthropic ou Google GenAI. As solicitações tentam os modelos selecionados em ordem.', 'models.provider_models': 'Modelos dos provedores', 'models.search_models': 'Pesquisar modelos', 'models.unavailable_routes': 'Rotas de modelo indisponíveis', 'about.project': 'Projeto', 'about.project_description': 'O Omni Gateway oferece um único plano de gerenciamento para rotear solicitações de ferramentas de programação entre formatos de IA compatíveis, pools de credenciais ativas e mecanismos de fallback resilientes.', 'about.repository': 'Repositório', 'about.operating_model': 'Modelo operacional', 'about.operating_model_description': 'Principais recursos disponíveis na camada de roteamento.', 'about.feature_routing': 'Orquestração de modelos virtuais e failover automático inteligente', 'about.feature_tokens': 'Limpeza baseada em tokens e visibilidade de uso', 'about.feature_credentials': 'Contas OAuth, chaves de API e servidores de modelos locais em um só pool', 'about.feature_translation': 'Tradução de formatos OpenAI, Anthropic, Google GenAI e nativos dos provedores', 'dashboard.requests_period': 'Solicitações {period}', 'dashboard.tokens_period': 'Tokens {period}', 'dashboard.period_1d': 'nas últimas 24 horas', 'dashboard.period_7d': 'nos últimos 7 dias', 'dashboard.period_30d': 'nos últimos 30 dias', 'dashboard.period_all': 'em todo o período registrado', 'dashboard.breakdown_1d': 'Detalhamento das solicitações em 24 horas', 'dashboard.breakdown_7d': 'Detalhamento das solicitações em 7 dias', 'dashboard.breakdown_30d': 'Detalhamento das solicitações em 30 dias', 'dashboard.breakdown_all': 'Detalhamento de todas as solicitações', 'dashboard.breakdown_description': 'Confira o tráfego de provedores e credenciais {period}.', 'dashboard.successful_failed': '{successful} bem-sucedidas / {failed} com falha', 'dashboard.success_rate': 'Taxa de sucesso', 'dashboard.no_traffic_yet': 'Ainda não há tráfego', 'dashboard.requests_succeeded': '{successful} de {total} solicitações foram bem-sucedidas.', 'dashboard.active_total_credentials': 'Credenciais ativas / totais', 'dashboard.disabled_count': '{count} desativadas', 'dashboard.requests_per_credential': 'Solicitações por credencial ativa', 'dashboard.assigned_requests': '{count} solicitações atribuídas', 'dashboard.tokens_per_request': 'Tokens por solicitação bem-sucedida', 'dashboard.input_output': 'Entrada {input} / saída {output}', 'dashboard.cache_savings': 'Em cache {cached} / economia estimada {savings}', 'dashboard.api_integration': 'Integração da API', 'dashboard.api_integration_description': 'Copie a chave da API e as URLs base dos SDKs usadas pelos clientes compatíveis.', 'dashboard.sdk_setup': 'Configuração dos SDKs', 'dashboard.sdk_setup_description': 'Escolha uma linguagem para ver a configuração de cliente de cada SDK compatível.', 'dashboard.client_language': 'Linguagem do cliente', 'dashboard.historical_usage': 'Uso histórico das credenciais', 'dashboard.historical_usage_description': 'Confira o tráfego anonimizado mantido para credenciais que não estão mais no pool.', 'dashboard.no_credential': 'Nenhuma credencial atribuída', 'dashboard.requests_count': '{count} solicitações', 'dashboard.success_count': '{count} bem-sucedidas / {failed} com falha', 'dashboard.succeeded_count': '{successful} de {total} bem-sucedidas', 'dashboard.no_traffic_recorded': 'Nenhum tráfego registrado', 'dashboard.tokens_total': '{count} no total', 'dashboard.token_details': 'Entrada {input} / saída {output} / economia estimada {savings}', 'dashboard.active_credentials_count': '{count} credencial ativa', 'dashboard.active_credentials_count_plural': '{count} credenciais ativas', 'dashboard.no_active_credentials': 'Nenhuma credencial ativa', 'dashboard.no_traffic': 'Sem tráfego'
    },
    ru: {
        clear_all: 'Очистить всё', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Нет подключения', 'logs.waiting': 'Ожидание записей журнала...', 'models.virtual_model': 'Виртуальная модель', 'models.not_configured': 'Не настроено', 'models.virtual_model_description': 'Используйте omway в клиентах OpenAI, Anthropic или Google GenAI. Запросы последовательно направляются выбранным моделям.', 'models.provider_models': 'Модели провайдеров', 'models.search_models': 'Поиск моделей', 'models.unavailable_routes': 'Недоступные маршруты моделей', 'about.project': 'Проект', 'about.project_description': 'Omni Gateway предоставляет единую панель управления маршрутизацией запросов инструментов разработки между совместимыми форматами ИИ, активными пулами учётных данных и устойчивыми механизмами резервирования.', 'about.repository': 'Репозиторий', 'about.operating_model': 'Принцип работы', 'about.operating_model_description': 'Основные возможности уровня маршрутизации.', 'about.feature_routing': 'Оркестрация виртуальных моделей и интеллектуальное автоматическое переключение', 'about.feature_tokens': 'Очистка с учётом токенов и контроль использования', 'about.feature_credentials': 'Учётные записи OAuth, ключи API и локальные серверы моделей в одном пуле', 'about.feature_translation': 'Преобразование форматов OpenAI, Anthropic, Google GenAI и собственных форматов провайдеров', 'dashboard.requests_period': 'Запросы {period}', 'dashboard.tokens_period': 'Токены {period}', 'dashboard.period_1d': 'за последние 24 часа', 'dashboard.period_7d': 'за последние 7 дней', 'dashboard.period_30d': 'за последние 30 дней', 'dashboard.period_all': 'за всё время наблюдения', 'dashboard.breakdown_1d': 'Статистика запросов за 24 часа', 'dashboard.breakdown_7d': 'Статистика запросов за 7 дней', 'dashboard.breakdown_30d': 'Статистика запросов за 30 дней', 'dashboard.breakdown_all': 'Статистика запросов за всё время', 'dashboard.breakdown_description': 'Просмотр трафика провайдеров и учётных данных {period}.', 'dashboard.successful_failed': 'успешно: {successful} / с ошибкой: {failed}', 'dashboard.success_rate': 'Доля успешных запросов', 'dashboard.no_traffic_yet': 'Трафика пока нет', 'dashboard.requests_succeeded': 'Успешно выполнено {successful} из {total} запросов.', 'dashboard.active_total_credentials': 'Активные / все учётные данные', 'dashboard.disabled_count': 'отключено: {count}', 'dashboard.requests_per_credential': 'Запросов на активные учётные данные', 'dashboard.assigned_requests': 'назначено запросов: {count}', 'dashboard.tokens_per_request': 'Токенов на успешный запрос', 'dashboard.input_output': 'Ввод: {input} / вывод: {output}', 'dashboard.cache_savings': 'Из кэша: {cached} / оценка экономии: {savings}', 'dashboard.api_integration': 'Интеграция API', 'dashboard.api_integration_description': 'Скопируйте ключ API и базовые URL SDK для совместимых клиентов.', 'dashboard.sdk_setup': 'Настройка SDK', 'dashboard.sdk_setup_description': 'Выберите язык, чтобы просмотреть конфигурацию клиента для каждого поддерживаемого SDK.', 'dashboard.client_language': 'Язык клиента', 'dashboard.historical_usage': 'История использования учётных данных', 'dashboard.historical_usage_description': 'Просмотр сохранённого анонимизированного трафика учётных данных, которых больше нет в пуле.', 'dashboard.no_credential': 'Учётные данные не назначены', 'dashboard.requests_count': 'Запросов: {count}', 'dashboard.success_count': 'успешно: {count} / с ошибкой: {failed}', 'dashboard.succeeded_count': 'успешно: {successful} из {total}', 'dashboard.no_traffic_recorded': 'Трафик не зафиксирован', 'dashboard.tokens_total': 'всего: {count}', 'dashboard.token_details': 'Ввод: {input} / вывод: {output} / оценка экономии: {savings}', 'dashboard.active_credentials_count': 'Активных учётных данных: {count}', 'dashboard.active_credentials_count_plural': 'Активных учётных данных: {count}', 'dashboard.no_active_credentials': 'Нет активных учётных данных', 'dashboard.no_traffic': 'Нет трафика'
    },
    th: {
        clear_all: 'ล้างทั้งหมด', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'ยังไม่เชื่อมต่อ', 'logs.waiting': 'กำลังรอบันทึก...', 'models.virtual_model': 'โมเดลเสมือน', 'models.not_configured': 'ยังไม่ได้ตั้งค่า', 'models.virtual_model_description': 'ใช้ omway ในไคลเอนต์ OpenAI, Anthropic หรือ Google GenAI โดยระบบจะลองโมเดลที่เลือกตามลำดับ', 'models.provider_models': 'โมเดลของผู้ให้บริการ', 'models.search_models': 'ค้นหาโมเดล', 'models.unavailable_routes': 'เส้นทางโมเดลที่ใช้ไม่ได้', 'about.project': 'โครงการ', 'about.project_description': 'Omni Gateway เป็นศูนย์กลางเดียวสำหรับจัดการการกำหนดเส้นทางคำขอจากเครื่องมือเขียนโค้ดข้ามรูปแบบ AI ที่รองรับ พูลข้อมูลรับรองที่ใช้งานอยู่ และกลไกสำรองที่ยืดหยุ่น', 'about.repository': 'ที่เก็บโค้ด', 'about.operating_model': 'รูปแบบการทำงาน', 'about.operating_model_description': 'ความสามารถหลักที่มีในชั้นการกำหนดเส้นทาง', 'about.feature_routing': 'การจัดการโมเดลเสมือนและการสลับเส้นทางอัตโนมัติอย่างชาญฉลาด', 'about.feature_tokens': 'การลดข้อมูลโดยคำนึงถึงโทเค็นและการมองเห็นการใช้งาน', 'about.feature_credentials': 'บัญชี OAuth, คีย์ API และเซิร์ฟเวอร์โมเดลภายในเครื่องในพูลเดียว', 'about.feature_translation': 'การแปลงรูปแบบ OpenAI, Anthropic, Google GenAI และรูปแบบดั้งเดิมของผู้ให้บริการ', 'dashboard.requests_period': 'คำขอ ({period})', 'dashboard.tokens_period': 'โทเค็น ({period})', 'dashboard.period_1d': '24 ชั่วโมงที่ผ่านมา', 'dashboard.period_7d': '7 วันที่ผ่านมา', 'dashboard.period_30d': '30 วันที่ผ่านมา', 'dashboard.period_all': 'ตลอดช่วงเวลาที่บันทึก', 'dashboard.breakdown_1d': 'รายละเอียดคำขอใน 24 ชั่วโมง', 'dashboard.breakdown_7d': 'รายละเอียดคำขอใน 7 วัน', 'dashboard.breakdown_30d': 'รายละเอียดคำขอใน 30 วัน', 'dashboard.breakdown_all': 'รายละเอียดคำขอทั้งหมด', 'dashboard.breakdown_description': 'ตรวจสอบการรับส่งข้อมูลของผู้ให้บริการและข้อมูลรับรองในช่วง{period}', 'dashboard.successful_failed': 'สำเร็จ {successful} / ล้มเหลว {failed}', 'dashboard.success_rate': 'อัตราความสำเร็จ', 'dashboard.no_traffic_yet': 'ยังไม่มีการรับส่งข้อมูล', 'dashboard.requests_succeeded': 'สำเร็จ {successful} จาก {total} คำขอ', 'dashboard.active_total_credentials': 'ข้อมูลรับรองที่ใช้งาน / ทั้งหมด', 'dashboard.disabled_count': 'ปิดใช้งาน {count} รายการ', 'dashboard.requests_per_credential': 'คำขอต่อข้อมูลรับรองที่ใช้งานอยู่', 'dashboard.assigned_requests': 'กำหนดแล้ว {count} คำขอ', 'dashboard.tokens_per_request': 'โทเค็นต่อคำขอที่สำเร็จ', 'dashboard.input_output': 'อินพุต {input} / เอาต์พุต {output}', 'dashboard.cache_savings': 'แคช {cached} / ประหยัดโดยประมาณ {savings}', 'dashboard.api_integration': 'การเชื่อมต่อ API', 'dashboard.api_integration_description': 'คัดลอกคีย์ API และ URL หลักของ SDK สำหรับไคลเอนต์ที่รองรับ', 'dashboard.sdk_setup': 'การตั้งค่า SDK', 'dashboard.sdk_setup_description': 'เลือกภาษาเพื่อดูการกำหนดค่าไคลเอนต์ของ SDK ที่รองรับแต่ละรายการ', 'dashboard.client_language': 'ภาษาของไคลเอนต์', 'dashboard.historical_usage': 'ประวัติการใช้ข้อมูลรับรอง', 'dashboard.historical_usage_description': 'ตรวจสอบการรับส่งข้อมูลแบบไม่ระบุตัวตนของข้อมูลรับรองที่ไม่มีอยู่ในพูลแล้ว', 'dashboard.no_credential': 'ยังไม่ได้กำหนดข้อมูลรับรอง', 'dashboard.requests_count': '{count} คำขอ', 'dashboard.success_count': 'สำเร็จ {count} / ล้มเหลว {failed}', 'dashboard.succeeded_count': 'สำเร็จ {successful} จาก {total}', 'dashboard.no_traffic_recorded': 'ไม่มีการรับส่งข้อมูลที่บันทึกไว้', 'dashboard.tokens_total': 'รวม {count}', 'dashboard.token_details': 'อินพุต {input} / เอาต์พุต {output} / ประหยัดโดยประมาณ {savings}', 'dashboard.active_credentials_count': 'ข้อมูลรับรองที่ใช้งานอยู่ {count} รายการ', 'dashboard.active_credentials_count_plural': 'ข้อมูลรับรองที่ใช้งานอยู่ {count} รายการ', 'dashboard.no_active_credentials': 'ไม่มีข้อมูลรับรองที่ใช้งานอยู่', 'dashboard.no_traffic': 'ไม่มีการรับส่งข้อมูล'
    },
    tr: {
        clear_all: 'Tümünü temizle', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Bağlı değil', 'logs.waiting': 'Günlükler bekleniyor...', 'models.virtual_model': 'Sanal Model', 'models.not_configured': 'Yapılandırılmadı', 'models.virtual_model_description': 'omway modelini OpenAI, Anthropic veya Google GenAI istemcilerinde kullanın. İstekler seçili modelleri yukarıdan aşağıya dener.', 'models.provider_models': 'Sağlayıcı Modelleri', 'models.search_models': 'Model ara', 'models.unavailable_routes': 'Kullanılamayan Model Rotaları', 'about.project': 'Proje', 'about.project_description': 'Omni Gateway; kodlama araçlarından gelen istekleri uyumlu yapay zekâ biçimleri, etkin kimlik bilgisi havuzları ve dayanıklı geri dönüş mekanizmaları arasında yönlendirmek için tek bir yönetim düzlemi sunar.', 'about.repository': 'Depo', 'about.operating_model': 'Çalışma Modeli', 'about.operating_model_description': 'Yönlendirme katmanında sunulan temel özellikler.', 'about.feature_routing': 'Sanal model orkestrasyonu ve akıllı otomatik yük devretme', 'about.feature_tokens': 'Belirteç duyarlı temizleme ve kullanım görünürlüğü', 'about.feature_credentials': 'OAuth hesapları, API anahtarları ve yerel model sunucuları tek havuzda', 'about.feature_translation': 'OpenAI, Anthropic, Google GenAI ve sağlayıcıya özgü biçim dönüşümü', 'dashboard.requests_period': 'İstekler ({period})', 'dashboard.tokens_period': 'Belirteçler ({period})', 'dashboard.period_1d': 'son 24 saatte', 'dashboard.period_7d': 'son 7 günde', 'dashboard.period_30d': 'son 30 günde', 'dashboard.period_all': 'kaydedilen tüm zaman boyunca', 'dashboard.breakdown_1d': '24 Saatlik İstek Dağılımı', 'dashboard.breakdown_7d': '7 Günlük İstek Dağılımı', 'dashboard.breakdown_30d': '30 Günlük İstek Dağılımı', 'dashboard.breakdown_all': 'Tüm Zamanların İstek Dağılımı', 'dashboard.breakdown_description': 'Sağlayıcı ve kimlik bilgisi trafiğini {period} inceleyin.', 'dashboard.successful_failed': '{successful} başarılı / {failed} başarısız', 'dashboard.success_rate': 'Başarı oranı', 'dashboard.no_traffic_yet': 'Henüz trafik yok', 'dashboard.requests_succeeded': '{total} isteğin {successful} tanesi başarılı oldu.', 'dashboard.active_total_credentials': 'Etkin / toplam kimlik bilgileri', 'dashboard.disabled_count': '{count} devre dışı', 'dashboard.requests_per_credential': 'Etkin kimlik bilgisi başına istek', 'dashboard.assigned_requests': '{count} istek atandı', 'dashboard.tokens_per_request': 'Başarılı istek başına belirteç', 'dashboard.input_output': 'Girdi {input} / çıktı {output}', 'dashboard.cache_savings': 'Önbellek {cached} / tahmini tasarruf {savings}', 'dashboard.api_integration': 'API Entegrasyonu', 'dashboard.api_integration_description': 'Uyumlu istemcilerin kullandığı API anahtarını ve SDK temel URL’lerini kopyalayın.', 'dashboard.sdk_setup': 'SDK Kurulumu', 'dashboard.sdk_setup_description': 'Desteklenen her SDK için istemci yapılandırmasını görmek üzere bir dil seçin.', 'dashboard.client_language': 'İstemci dili', 'dashboard.historical_usage': 'Geçmiş Kimlik Bilgisi Kullanımı', 'dashboard.historical_usage_description': 'Artık havuzda bulunmayan kimlik bilgilerinin saklanan anonim trafiğini inceleyin.', 'dashboard.no_credential': 'Kimlik bilgisi atanmadı', 'dashboard.requests_count': '{count} istek', 'dashboard.success_count': '{count} başarılı / {failed} başarısız', 'dashboard.succeeded_count': '{total} isteğin {successful} tanesi başarılı', 'dashboard.no_traffic_recorded': 'Kayıtlı trafik yok', 'dashboard.tokens_total': 'Toplam {count}', 'dashboard.token_details': 'Girdi {input} / çıktı {output} / tahmini tasarruf {savings}', 'dashboard.active_credentials_count': '{count} etkin kimlik bilgisi', 'dashboard.active_credentials_count_plural': '{count} etkin kimlik bilgisi', 'dashboard.no_active_credentials': 'Etkin kimlik bilgisi yok', 'dashboard.no_traffic': 'Trafik yok'
    },
    vi: {
        clear_all: 'Xóa tất cả', 'logs.websocket': 'WebSocket:', 'logs.not_connected': 'Chưa kết nối', 'logs.waiting': 'Đang chờ nhật ký...', 'models.virtual_model': 'Mô hình ảo', 'models.not_configured': 'Chưa cấu hình', 'models.virtual_model_description': 'Dùng omway trong ứng dụng khách OpenAI, Anthropic hoặc Google GenAI. Yêu cầu sẽ lần lượt thử các mô hình đã chọn theo thứ tự.', 'models.provider_models': 'Mô hình của nhà cung cấp', 'models.search_models': 'Tìm mô hình', 'models.unavailable_routes': 'Tuyến mô hình không khả dụng', 'about.project': 'Dự án', 'about.project_description': 'Omni Gateway cung cấp một mặt phẳng quản trị duy nhất để định tuyến yêu cầu từ công cụ lập trình qua các định dạng AI tương thích, kho thông tin xác thực đang hoạt động và cơ chế dự phòng bền bỉ.', 'about.repository': 'Kho mã nguồn', 'about.operating_model': 'Mô hình vận hành', 'about.operating_model_description': 'Các năng lực cốt lõi được cung cấp qua tầng định tuyến.', 'about.feature_routing': 'Điều phối mô hình ảo và tự động chuyển tuyến dự phòng thông minh', 'about.feature_tokens': 'Làm gọn theo token và theo dõi mức sử dụng', 'about.feature_credentials': 'Tài khoản OAuth, khóa API và máy chủ mô hình cục bộ trong cùng một kho', 'about.feature_translation': 'Chuyển đổi định dạng OpenAI, Anthropic, Google GenAI và định dạng gốc của nhà cung cấp', 'dashboard.requests_period': 'Yêu cầu {period}', 'dashboard.tokens_period': 'Token {period}', 'dashboard.period_1d': 'trong 24 giờ qua', 'dashboard.period_7d': 'trong 7 ngày qua', 'dashboard.period_30d': 'trong 30 ngày qua', 'dashboard.period_all': 'trong toàn bộ thời gian đã ghi nhận', 'dashboard.breakdown_1d': 'Phân tích yêu cầu trong 24 giờ', 'dashboard.breakdown_7d': 'Phân tích yêu cầu trong 7 ngày', 'dashboard.breakdown_30d': 'Phân tích yêu cầu trong 30 ngày', 'dashboard.breakdown_all': 'Phân tích toàn bộ yêu cầu', 'dashboard.breakdown_description': 'Xem lưu lượng của nhà cung cấp và thông tin xác thực {period}.', 'dashboard.successful_failed': '{successful} thành công / {failed} thất bại', 'dashboard.success_rate': 'Tỷ lệ thành công', 'dashboard.no_traffic_yet': 'Chưa có lưu lượng', 'dashboard.requests_succeeded': '{successful} trong tổng số {total} yêu cầu đã thành công.', 'dashboard.active_total_credentials': 'Thông tin xác thực hoạt động / tổng số', 'dashboard.disabled_count': '{count} đã tắt', 'dashboard.requests_per_credential': 'Yêu cầu trên mỗi thông tin xác thực hoạt động', 'dashboard.assigned_requests': '{count} yêu cầu đã được phân bổ', 'dashboard.tokens_per_request': 'Token trên mỗi yêu cầu thành công', 'dashboard.input_output': 'Đầu vào {input} / đầu ra {output}', 'dashboard.cache_savings': 'Đã lưu đệm {cached} / ước tính tiết kiệm {savings}', 'dashboard.api_integration': 'Tích hợp API', 'dashboard.api_integration_description': 'Sao chép khóa API và URL cơ sở của SDK để dùng với các ứng dụng khách tương thích.', 'dashboard.sdk_setup': 'Thiết lập SDK', 'dashboard.sdk_setup_description': 'Chọn ngôn ngữ để xem cấu hình ứng dụng khách cho từng SDK được hỗ trợ.', 'dashboard.client_language': 'Ngôn ngữ ứng dụng khách', 'dashboard.historical_usage': 'Lịch sử sử dụng thông tin xác thực', 'dashboard.historical_usage_description': 'Xem lưu lượng ẩn danh được lưu lại từ những thông tin xác thực không còn trong kho.', 'dashboard.no_credential': 'Chưa phân bổ thông tin xác thực', 'dashboard.requests_count': '{count} yêu cầu', 'dashboard.success_count': '{count} thành công / {failed} thất bại', 'dashboard.succeeded_count': '{successful} trong tổng số {total} thành công', 'dashboard.no_traffic_recorded': 'Chưa ghi nhận lưu lượng', 'dashboard.tokens_total': 'Tổng cộng {count}', 'dashboard.token_details': 'Đầu vào {input} / đầu ra {output} / ước tính tiết kiệm {savings}', 'dashboard.active_credentials_count': '{count} thông tin xác thực đang hoạt động', 'dashboard.active_credentials_count_plural': '{count} thông tin xác thực đang hoạt động', 'dashboard.no_active_credentials': 'Không có thông tin xác thực đang hoạt động', 'dashboard.no_traffic': 'Không có lưu lượng'
    }
};

const UPDATE_GUIDE_KEYS = ['about.update_guide_link'];

const UPDATE_GUIDE_COPY = {
    en: 'Read the update guide before upgrading.',
    'zh-CN': '升级前请阅读更新指南。',
    'zh-TW': '升級前請閱讀更新指南。',
    de: 'Lesen Sie vor dem Upgrade die Aktualisierungsanleitung.',
    es: 'Consulta la guía de actualización antes de actualizar.',
    fr: 'Consultez le guide de mise à jour avant de procéder à la mise à niveau.',
    id: 'Baca panduan pembaruan sebelum melakukan pembaruan.',
    it: 'Consulta la guida all’aggiornamento prima di aggiornare.',
    ja: 'アップグレード前に更新ガイドを確認してください。',
    ko: '업그레이드하기 전에 업데이트 가이드를 확인하세요.',
    pt: 'Leia o guia de atualização antes de atualizar.',
    ru: 'Перед обновлением ознакомьтесь с руководством по обновлению.',
    th: 'โปรดอ่านคู่มือการอัปเดตก่อนอัปเกรด',
    tr: 'Yükseltmeden önce güncelleme kılavuzunu okuyun.',
    vi: 'Đọc hướng dẫn cập nhật trước khi nâng cấp.',
};

for (const [locale, value] of Object.entries(UPDATE_GUIDE_COPY)) {
    PAGE_LOCALE_TRANSLATIONS[locale]['about.update_guide_link'] = value;
}

const SETTINGS_PAGE_KEYS = [
    'settings.storage_note', 'settings.server_access', 'settings.server_access_description', 'settings.bind_host', 'settings.port', 'settings.listener_restart_hint',
    'settings.translation_runtime', 'settings.translation_runtime_description', 'settings.flatten_instructions', 'settings.return_reasoning', 'settings.recovery_attempts',
    'settings.context_optimization', 'settings.context_optimization_description', 'settings.compress_history', 'settings.compression_threshold', 'settings.compression_target', 'settings.recent_turns',
    'settings.console_access', 'settings.console_access_description', 'settings.configured', 'settings.current_password', 'settings.new_password', 'settings.password_unchanged', 'settings.confirm_console_password', 'settings.update_password',
    'settings.failover_policy', 'settings.failover_policy_description', 'settings.auto_disable', 'settings.auto_disable_codes', 'settings.retry_alternate', 'settings.maximum_retries', 'settings.retry_interval',
    'settings.runtime_logs', 'settings.runtime_logs_description', 'settings.log_level', 'settings.log_file_size', 'settings.log_backups', 'settings.log_rotation_hint',
    'settings.storage_proxy', 'settings.storage_proxy_description', 'settings.credentials_directory', 'settings.outbound_proxy', 'settings.proxy_hint', 'settings.credentials_restart_hint',
    'settings.routing_policy', 'settings.routing_policy_description', 'settings.credential_selection', 'settings.balanced', 'settings.provider_priority', 'settings.preferred_provider', 'settings.automatic', 'settings.inference_timeout', 'settings.routing_fallback_hint',
    'settings.code_assist', 'settings.code_assist_description', 'settings.keep_alive', 'settings.keep_alive_description', 'settings.keep_alive_url', 'settings.use_current_url', 'settings.keep_alive_interval'
];

const SETTINGS_PAGE_VALUES = {
    en: [
        'Values saved here are stored locally unless they are managed by the runtime environment. Provider-specific settings are managed from the Providers page.', 'Server Access', 'Control the network interface used by the service after its next restart.', 'Bind host', 'Port', 'Listener changes require an application restart. Docker port publishing must be updated separately.',
        'Translation and Runtime', 'Adjust compatibility translation and response recovery behavior.', 'Flatten system instructions for compatibility', 'Return reasoning content when available', 'Truncation recovery attempts',
        'Context Optimization', 'Reduce oversized conversation history while preserving system instructions, tool definitions, and recent turns.', 'Compress oversized conversation history', 'Compression threshold in tokens', 'Target size in tokens', 'Recent turns to preserve',
        'Console Access', 'Change the console password without revealing its current value.', 'Configured', 'Current console password', 'New console password', 'Leave blank to keep unchanged', 'Confirm console password', 'Update password',
        'Failover Policy', 'Define automatic disabling, retries, and alternate credential behavior.', 'Auto-disable credentials for configured error codes', 'Auto-disable error codes', 'Retry failed requests with alternate credentials', 'Maximum retries', 'Retry interval in seconds',
        'Runtime Logs', 'Control server-side verbosity and bounded file retention.', 'Log level', 'Maximum file size in MB', 'Retained backup files', 'Logs rotate automatically when the active file reaches the configured size.',
        'Storage and Proxy', 'Set credential storage and outbound network routing.', 'Credentials directory', 'Outbound proxy', 'Use the proxy when the server cannot reach OAuth or provider APIs directly.', 'Changing the credentials directory requires an application restart.',
        'Routing Policy', 'Balance healthy credentials automatically or prefer one provider while retaining fallback.', 'Credential selection', 'Balanced', 'Provider priority', 'Preferred provider', 'Automatic', 'Inference timeout in seconds', 'If the preferred provider is unavailable or incompatible with a model, routing continues through another healthy provider.',
        'Code Assist Compatibility', 'Optional legacy client and endpoint compatibility.', 'Hosted Keep-Alive', 'Optional periodic requests for hosting platforms that suspend idle services.', 'Keep-alive URL', 'Use current URL', 'Keep-alive interval in seconds'
    ],
    vi: [
        'Các giá trị tại đây được lưu cục bộ, trừ khi môi trường chạy quản lý chúng. Cài đặt riêng của từng nhà cung cấp nằm tại trang Nhà cung cấp.', 'Truy cập máy chủ', 'Kiểm soát giao diện mạng mà dịch vụ sử dụng sau lần khởi động tiếp theo.', 'Địa chỉ lắng nghe', 'Cổng', 'Thay đổi trình lắng nghe cần khởi động lại ứng dụng. Cấu hình ánh xạ cổng Docker phải được cập nhật riêng.',
        'Chuyển đổi và thời gian chạy', 'Điều chỉnh khả năng tương thích định dạng và cơ chế khôi phục phản hồi.', 'Gộp chỉ dẫn hệ thống để tăng khả năng tương thích', 'Trả về nội dung suy luận khi có', 'Số lần thử khôi phục phản hồi bị cắt',
        'Tối ưu ngữ cảnh', 'Rút gọn lịch sử hội thoại quá dài nhưng vẫn giữ chỉ dẫn hệ thống, định nghĩa công cụ và các lượt trao đổi gần đây.', 'Nén lịch sử hội thoại quá dài', 'Ngưỡng nén tính theo token', 'Kích thước mục tiêu tính theo token', 'Số lượt gần đây cần giữ lại',
        'Truy cập bảng điều khiển', 'Đổi mật khẩu bảng điều khiển mà không hiển thị giá trị hiện tại.', 'Đã cấu hình', 'Mật khẩu bảng điều khiển hiện tại', 'Mật khẩu bảng điều khiển mới', 'Để trống nếu không muốn thay đổi', 'Xác nhận mật khẩu bảng điều khiển', 'Cập nhật mật khẩu',
        'Chính sách dự phòng', 'Thiết lập cơ chế tự động vô hiệu hóa, thử lại và chuyển sang thông tin xác thực khác.', 'Tự động tắt thông tin xác thực khi gặp mã lỗi đã cấu hình', 'Mã lỗi dùng để tự động tắt', 'Thử lại yêu cầu thất bại bằng thông tin xác thực khác', 'Số lần thử lại tối đa', 'Khoảng nghỉ giữa các lần thử, tính bằng giây',
        'Nhật ký thời gian chạy', 'Kiểm soát mức độ chi tiết ở phía máy chủ và giới hạn số tệp lưu lại.', 'Mức nhật ký', 'Kích thước tệp tối đa, tính bằng MB', 'Số tệp sao lưu giữ lại', 'Nhật ký tự động luân chuyển khi tệp hiện tại đạt kích thước đã cấu hình.',
        'Lưu trữ và proxy', 'Thiết lập nơi lưu thông tin xác thực và tuyến mạng đi ra.', 'Thư mục thông tin xác thực', 'Proxy kết nối ra ngoài', 'Dùng proxy khi máy chủ không thể kết nối trực tiếp tới OAuth hoặc API của nhà cung cấp.', 'Thay đổi thư mục thông tin xác thực cần khởi động lại ứng dụng.',
        'Chính sách định tuyến', 'Tự động cân bằng các thông tin xác thực khỏe mạnh hoặc ưu tiên một nhà cung cấp nhưng vẫn giữ tuyến dự phòng.', 'Cách chọn thông tin xác thực', 'Cân bằng', 'Ưu tiên nhà cung cấp', 'Nhà cung cấp ưu tiên', 'Tự động', 'Thời gian chờ suy luận, tính bằng giây', 'Nếu nhà cung cấp ưu tiên không khả dụng hoặc không hỗ trợ mô hình, hệ thống tiếp tục định tuyến qua một nhà cung cấp khỏe mạnh khác.',
        'Tương thích Code Assist', 'Khả năng tương thích tùy chọn với ứng dụng khách và endpoint cũ.', 'Duy trì hoạt động trên nền tảng lưu trữ', 'Gửi yêu cầu định kỳ cho các nền tảng tạm dừng dịch vụ khi không hoạt động.', 'URL duy trì hoạt động', 'Dùng URL hiện tại', 'Chu kỳ duy trì hoạt động, tính bằng giây'
    ],
    'zh-CN': [
        '除非由运行环境管理，否则此处保存的值会存储在本地。各提供商的专属设置请在“提供商”页面管理。', '服务器访问', '控制服务在下次启动后使用的网络接口。', '监听地址', '端口', '修改监听设置后必须重启应用。Docker 端口映射需要单独更新。',
        '格式转换与运行时', '调整兼容性转换和响应恢复行为。', '合并系统指令以提高兼容性', '在可用时返回推理内容', '截断恢复尝试次数',
        '上下文优化', '缩减过长的对话历史，同时保留系统指令、工具定义和最近的对话轮次。', '压缩过长的对话历史', '压缩阈值（令牌）', '目标大小（令牌）', '保留的最近对话轮次',
        '控制台访问', '更改控制台密码，但不会显示当前密码。', '已配置', '当前控制台密码', '新控制台密码', '留空则保持不变', '确认控制台密码', '更新密码',
        '故障转移策略', '定义自动停用、重试和备用凭据行为。', '遇到指定错误码时自动停用凭据', '自动停用错误码', '使用其他凭据重试失败的请求', '最大重试次数', '重试间隔（秒）',
        '运行时日志', '控制服务器日志详细程度和保留文件数量。', '日志级别', '最大文件大小（MB）', '保留的备份文件', '当前日志文件达到指定大小后会自动轮换。',
        '存储与代理', '设置凭据存储位置和出站网络路由。', '凭据目录', '出站代理', '服务器无法直接访问 OAuth 或提供商 API 时使用代理。', '更改凭据目录后必须重启应用。',
        '路由策略', '自动平衡健康凭据，或在保留故障转移的同时优先使用某个提供商。', '凭据选择方式', '均衡', '提供商优先级', '首选提供商', '自动', '推理超时（秒）', '如果首选提供商不可用或不支持某个模型，系统会继续通过其他健康的提供商进行路由。',
        'Code Assist 兼容性', '可选的旧版客户端与 endpoint 兼容设置。', '托管平台保活', '为会暂停空闲服务的托管平台定期发送可选请求。', '保活 URL', '使用当前 URL', '保活间隔（秒）'
    ],
    'zh-TW': [
        '除非由執行環境管理，否則此處儲存的值會保存在本機。各供應商的專屬設定請在「供應商」頁面管理。', '伺服器存取', '控制服務在下次啟動後使用的網路介面。', '監聽位址', '連接埠', '修改監聽設定後必須重新啟動應用程式。Docker 連接埠對應需要另外更新。',
        '格式轉換與執行階段', '調整相容性轉換與回應復原行為。', '合併系統指示以提高相容性', '可用時傳回推理內容', '截斷復原嘗試次數',
        '內容最佳化', '縮減過長的對話記錄，同時保留系統指示、工具定義與最近的對話輪次。', '壓縮過長的對話記錄', '壓縮門檻（權杖）', '目標大小（權杖）', '保留的最近對話輪次',
        '主控台存取', '變更主控台密碼，但不顯示目前的密碼。', '已設定', '目前的主控台密碼', '新的主控台密碼', '留空則維持不變', '確認主控台密碼', '更新密碼',
        '容錯策略', '設定自動停用、重試與替代憑證行為。', '遇到指定錯誤碼時自動停用憑證', '自動停用錯誤碼', '使用其他憑證重試失敗的請求', '最大重試次數', '重試間隔（秒）',
        '執行階段日誌', '控制伺服器日誌詳細程度與保留檔案數量。', '日誌層級', '檔案大小上限（MB）', '保留的備份檔案', '目前的日誌檔達到指定大小後會自動輪替。',
        '儲存與 Proxy', '設定憑證儲存位置與對外網路路由。', '憑證目錄', '對外 Proxy', '伺服器無法直接存取 OAuth 或供應商 API 時使用 Proxy。', '變更憑證目錄後必須重新啟動應用程式。',
        '路由策略', '自動平衡健康憑證，或在保留容錯的同時優先使用某個供應商。', '憑證選取方式', '平衡', '供應商優先順序', '偏好的供應商', '自動', '推理逾時（秒）', '如果偏好的供應商無法使用或不支援某個模型，系統會繼續透過其他健康的供應商路由。',
        'Code Assist 相容性', '選用的舊版用戶端與 endpoint 相容設定。', '託管平台保活', '為會暫停閒置服務的託管平台定期傳送選用請求。', '保活 URL', '使用目前 URL', '保活間隔（秒）'
    ],
    de: [
        'Hier gespeicherte Werte werden lokal abgelegt, sofern sie nicht von der Laufzeitumgebung verwaltet werden. Provider-spezifische Einstellungen finden Sie auf der Seite „Provider“.', 'Serverzugriff', 'Legt die Netzwerkschnittstelle fest, die der Dienst nach dem nächsten Neustart verwendet.', 'Bind-Adresse', 'Port', 'Änderungen am Listener erfordern einen Anwendungsneustart. Die Docker-Portfreigabe muss separat angepasst werden.',
        'Übersetzung und Laufzeit', 'Kompatibilitätsübersetzung und Wiederherstellung von Antworten anpassen.', 'Systemanweisungen für bessere Kompatibilität zusammenführen', 'Denk- und Begründungsinhalte zurückgeben, wenn verfügbar', 'Wiederherstellungsversuche bei abgeschnittenen Antworten',
        'Kontextoptimierung', 'Zu lange Gesprächsverläufe kürzen und dabei Systemanweisungen, Werkzeugdefinitionen und die neuesten Gesprächsrunden erhalten.', 'Zu lange Gesprächsverläufe komprimieren', 'Komprimierungsschwelle in Token', 'Zielgröße in Token', 'Zu erhaltende letzte Gesprächsrunden',
        'Konsolenzugriff', 'Konsolenpasswort ändern, ohne den aktuellen Wert anzuzeigen.', 'Konfiguriert', 'Aktuelles Konsolenpasswort', 'Neues Konsolenpasswort', 'Leer lassen, um es nicht zu ändern', 'Konsolenpasswort bestätigen', 'Passwort aktualisieren',
        'Failover-Richtlinie', 'Automatische Deaktivierung, Wiederholungen und alternative Zugänge festlegen.', 'Zugänge bei festgelegten Fehlercodes automatisch deaktivieren', 'Fehlercodes für automatische Deaktivierung', 'Fehlgeschlagene Anfragen mit alternativen Zugängen wiederholen', 'Maximale Wiederholungen', 'Wiederholungsintervall in Sekunden',
        'Laufzeitprotokolle', 'Serverseitige Detailtiefe und begrenzte Dateiaufbewahrung steuern.', 'Protokollstufe', 'Maximale Dateigröße in MB', 'Aufbewahrte Sicherungsdateien', 'Protokolle werden automatisch rotiert, sobald die aktive Datei die konfigurierte Größe erreicht.',
        'Speicher und Proxy', 'Speicherort der Zugangsdaten und ausgehendes Netzwerk-Routing festlegen.', 'Verzeichnis für Zugangsdaten', 'Ausgehender Proxy', 'Proxy verwenden, wenn der Server OAuth- oder Provider-APIs nicht direkt erreichen kann.', 'Eine Änderung des Verzeichnisses erfordert einen Anwendungsneustart.',
        'Routing-Richtlinie', 'Gesunde Zugänge automatisch ausgleichen oder einen Provider mit weiterhin aktivem Fallback bevorzugen.', 'Auswahl der Zugangsdaten', 'Ausgewogen', 'Provider-Priorität', 'Bevorzugter Provider', 'Automatisch', 'Zeitlimit für Inferenz in Sekunden', 'Ist der bevorzugte Provider nicht verfügbar oder mit einem Modell inkompatibel, wird über einen anderen gesunden Provider weitergeleitet.',
        'Code-Assist-Kompatibilität', 'Optionale Kompatibilität mit älteren Clients und Endpunkten.', 'Keep-Alive für Hosting', 'Optionale regelmäßige Anfragen für Hosting-Plattformen, die inaktive Dienste anhalten.', 'Keep-Alive-URL', 'Aktuelle URL verwenden', 'Keep-Alive-Intervall in Sekunden'
    ],
    es: [
        'Los valores guardados aquí se almacenan localmente, salvo que el entorno de ejecución los administre. La configuración específica de cada proveedor se gestiona en la página Proveedores.', 'Acceso al servidor', 'Controla la interfaz de red que usará el servicio después del próximo reinicio.', 'Dirección de escucha', 'Puerto', 'Los cambios del listener requieren reiniciar la aplicación. La publicación de puertos de Docker debe actualizarse por separado.',
        'Traducción y ejecución', 'Ajusta la traducción de compatibilidad y la recuperación de respuestas.', 'Combinar instrucciones del sistema para mejorar la compatibilidad', 'Devolver el contenido de razonamiento cuando esté disponible', 'Intentos de recuperación de respuestas truncadas',
        'Optimización del contexto', 'Reduce historiales de conversación demasiado largos conservando las instrucciones del sistema, las definiciones de herramientas y los turnos recientes.', 'Comprimir historiales de conversación demasiado largos', 'Umbral de compresión en tokens', 'Tamaño objetivo en tokens', 'Turnos recientes que se conservarán',
        'Acceso a la consola', 'Cambia la contraseña de la consola sin mostrar su valor actual.', 'Configurada', 'Contraseña actual de la consola', 'Nueva contraseña de la consola', 'Déjalo en blanco para no cambiarla', 'Confirmar contraseña de la consola', 'Actualizar contraseña',
        'Política de conmutación', 'Define la desactivación automática, los reintentos y el uso de credenciales alternativas.', 'Desactivar credenciales automáticamente para los códigos de error configurados', 'Códigos de error para desactivación automática', 'Reintentar solicitudes fallidas con credenciales alternativas', 'Máximo de reintentos', 'Intervalo entre reintentos en segundos',
        'Registros de ejecución', 'Controla el nivel de detalle del servidor y la retención limitada de archivos.', 'Nivel de registro', 'Tamaño máximo del archivo en MB', 'Archivos de copia de seguridad conservados', 'Los registros rotan automáticamente cuando el archivo activo alcanza el tamaño configurado.',
        'Almacenamiento y proxy', 'Configura el almacenamiento de credenciales y el enrutamiento de red saliente.', 'Directorio de credenciales', 'Proxy saliente', 'Usa el proxy cuando el servidor no pueda acceder directamente a OAuth o a las API de los proveedores.', 'Cambiar el directorio de credenciales requiere reiniciar la aplicación.',
        'Política de enrutamiento', 'Equilibra automáticamente las credenciales disponibles o prioriza un proveedor manteniendo el respaldo.', 'Selección de credenciales', 'Equilibrada', 'Prioridad del proveedor', 'Proveedor preferido', 'Automático', 'Tiempo de espera de inferencia en segundos', 'Si el proveedor preferido no está disponible o no admite un modelo, el enrutamiento continúa mediante otro proveedor disponible.',
        'Compatibilidad con Code Assist', 'Compatibilidad opcional con clientes y endpoints antiguos.', 'Keep-alive para alojamiento', 'Solicitudes periódicas opcionales para plataformas que suspenden servicios inactivos.', 'URL de keep-alive', 'Usar URL actual', 'Intervalo de keep-alive en segundos'
    ],
    fr: [
        'Les valeurs enregistrées ici sont stockées localement, sauf si l’environnement d’exécution les gère. Les réglages propres à chaque fournisseur se trouvent sur la page Fournisseurs.', 'Accès au serveur', 'Définit l’interface réseau utilisée par le service après son prochain redémarrage.', 'Adresse d’écoute', 'Port', 'Les modifications du service d’écoute nécessitent un redémarrage. La publication du port Docker doit être mise à jour séparément.',
        'Traduction et exécution', 'Réglez la traduction de compatibilité et la récupération des réponses.', 'Fusionner les instructions système pour améliorer la compatibilité', 'Renvoyer le contenu de raisonnement lorsqu’il est disponible', 'Tentatives de récupération après troncature',
        'Optimisation du contexte', 'Réduisez les historiques trop longs tout en conservant les instructions système, les définitions d’outils et les échanges récents.', 'Compresser les historiques de conversation trop longs', 'Seuil de compression en tokens', 'Taille cible en tokens', 'Échanges récents à conserver',
        'Accès à la console', 'Modifiez le mot de passe de la console sans afficher sa valeur actuelle.', 'Configuré', 'Mot de passe actuel de la console', 'Nouveau mot de passe de la console', 'Laissez vide pour ne pas le modifier', 'Confirmer le mot de passe de la console', 'Mettre à jour le mot de passe',
        'Politique de basculement', 'Définissez la désactivation automatique, les nouvelles tentatives et le recours à d’autres identifiants.', 'Désactiver automatiquement les identifiants pour les codes d’erreur configurés', 'Codes d’erreur de désactivation automatique', 'Relancer les requêtes échouées avec d’autres identifiants', 'Nombre maximal de tentatives', 'Intervalle entre les tentatives en secondes',
        'Journaux d’exécution', 'Contrôlez le niveau de détail côté serveur et la rétention limitée des fichiers.', 'Niveau de journalisation', 'Taille maximale du fichier en Mo', 'Fichiers de sauvegarde conservés', 'Les journaux changent automatiquement de fichier lorsque le fichier actif atteint la taille configurée.',
        'Stockage et proxy', 'Configurez le stockage des identifiants et le routage réseau sortant.', 'Répertoire des identifiants', 'Proxy sortant', 'Utilisez le proxy lorsque le serveur ne peut pas joindre directement OAuth ou les API des fournisseurs.', 'La modification du répertoire des identifiants nécessite un redémarrage.',
        'Politique de routage', 'Répartissez automatiquement la charge entre les identifiants disponibles ou privilégiez un fournisseur tout en conservant le basculement.', 'Sélection des identifiants', 'Équilibrée', 'Priorité du fournisseur', 'Fournisseur privilégié', 'Automatique', 'Délai d’inférence en secondes', 'Si le fournisseur privilégié est indisponible ou incompatible avec un modèle, le routage se poursuit via un autre fournisseur disponible.',
        'Compatibilité Code Assist', 'Compatibilité facultative avec les anciens clients et endpoints.', 'Keep-alive pour l’hébergement', 'Requêtes périodiques facultatives pour les plateformes qui suspendent les services inactifs.', 'URL de keep-alive', 'Utiliser l’URL actuelle', 'Intervalle de keep-alive en secondes'
    ],
    id: [
        'Nilai yang disimpan di sini tersimpan secara lokal kecuali dikelola oleh lingkungan runtime. Pengaturan khusus penyedia dikelola dari halaman Penyedia.', 'Akses Server', 'Atur antarmuka jaringan yang digunakan layanan setelah dimulai ulang.', 'Alamat bind', 'Port', 'Perubahan listener memerlukan mulai ulang aplikasi. Publikasi port Docker harus diperbarui secara terpisah.',
        'Penerjemahan dan Runtime', 'Atur penerjemahan kompatibilitas dan pemulihan respons.', 'Gabungkan instruksi sistem untuk kompatibilitas', 'Kembalikan konten penalaran jika tersedia', 'Percobaan pemulihan respons terpotong',
        'Optimasi Konteks', 'Ringkas riwayat percakapan yang terlalu panjang sambil mempertahankan instruksi sistem, definisi alat, dan giliran terbaru.', 'Kompres riwayat percakapan yang terlalu panjang', 'Ambang kompresi dalam token', 'Ukuran target dalam token', 'Giliran terbaru yang dipertahankan',
        'Akses Konsol', 'Ubah kata sandi konsol tanpa menampilkan nilai saat ini.', 'Sudah dikonfigurasi', 'Kata sandi konsol saat ini', 'Kata sandi konsol baru', 'Biarkan kosong agar tidak berubah', 'Konfirmasi kata sandi konsol', 'Perbarui kata sandi',
        'Kebijakan Failover', 'Atur penonaktifan otomatis, percobaan ulang, dan penggunaan kredensial alternatif.', 'Nonaktifkan kredensial otomatis untuk kode kesalahan yang dikonfigurasi', 'Kode kesalahan penonaktifan otomatis', 'Ulangi permintaan gagal dengan kredensial alternatif', 'Percobaan ulang maksimum', 'Jeda percobaan ulang dalam detik',
        'Log Runtime', 'Atur tingkat detail server dan batas penyimpanan file.', 'Level log', 'Ukuran file maksimum dalam MB', 'File cadangan yang dipertahankan', 'Log dirotasi otomatis saat file aktif mencapai ukuran yang ditetapkan.',
        'Penyimpanan dan Proxy', 'Atur penyimpanan kredensial dan perutean jaringan keluar.', 'Direktori kredensial', 'Proxy keluar', 'Gunakan proxy saat server tidak dapat menjangkau OAuth atau API penyedia secara langsung.', 'Perubahan direktori kredensial memerlukan mulai ulang aplikasi.',
        'Kebijakan Perutean', 'Seimbangkan kredensial sehat secara otomatis atau utamakan satu penyedia sambil tetap mempertahankan fallback.', 'Pemilihan kredensial', 'Seimbang', 'Prioritas penyedia', 'Penyedia pilihan', 'Otomatis', 'Batas waktu inferensi dalam detik', 'Jika penyedia pilihan tidak tersedia atau tidak mendukung model, perutean dilanjutkan melalui penyedia sehat lainnya.',
        'Kompatibilitas Code Assist', 'Kompatibilitas opsional untuk klien dan endpoint lama.', 'Keep-Alive Hosting', 'Permintaan berkala opsional untuk platform hosting yang menangguhkan layanan saat tidak aktif.', 'URL keep-alive', 'Gunakan URL saat ini', 'Interval keep-alive dalam detik'
    ],
    it: [
        'I valori salvati qui sono archiviati localmente, a meno che non siano gestiti dall’ambiente di runtime. Le impostazioni specifiche dei provider si gestiscono dalla pagina Provider.', 'Accesso al server', 'Controlla l’interfaccia di rete usata dal servizio dopo il prossimo riavvio.', 'Indirizzo di ascolto', 'Porta', 'Le modifiche al listener richiedono il riavvio dell’applicazione. La pubblicazione della porta Docker va aggiornata separatamente.',
        'Traduzione e runtime', 'Regola la traduzione di compatibilità e il recupero delle risposte.', 'Unisci le istruzioni di sistema per la compatibilità', 'Restituisci il contenuto di ragionamento quando disponibile', 'Tentativi di recupero delle risposte troncate',
        'Ottimizzazione del contesto', 'Riduci cronologie troppo lunghe mantenendo istruzioni di sistema, definizioni degli strumenti e turni recenti.', 'Comprimi le cronologie di conversazione troppo lunghe', 'Soglia di compressione in token', 'Dimensione obiettivo in token', 'Turni recenti da conservare',
        'Accesso alla console', 'Modifica la password della console senza mostrarne il valore attuale.', 'Configurata', 'Password attuale della console', 'Nuova password della console', 'Lascia vuoto per non modificarla', 'Conferma password della console', 'Aggiorna password',
        'Criteri di failover', 'Definisci disattivazione automatica, nuovi tentativi e uso di credenziali alternative.', 'Disattiva automaticamente le credenziali per i codici di errore configurati', 'Codici di errore per la disattivazione automatica', 'Riprova le richieste non riuscite con credenziali alternative', 'Numero massimo di tentativi', 'Intervallo tra i tentativi in secondi',
        'Log di runtime', 'Controlla il livello di dettaglio del server e la conservazione limitata dei file.', 'Livello di log', 'Dimensione massima del file in MB', 'File di backup conservati', 'I log ruotano automaticamente quando il file attivo raggiunge la dimensione configurata.',
        'Archiviazione e proxy', 'Configura l’archiviazione delle credenziali e il routing di rete in uscita.', 'Directory delle credenziali', 'Proxy in uscita', 'Usa il proxy quando il server non può raggiungere direttamente OAuth o le API dei provider.', 'La modifica della directory richiede il riavvio dell’applicazione.',
        'Criteri di routing', 'Bilancia automaticamente le credenziali disponibili o privilegia un provider mantenendo il fallback.', 'Selezione delle credenziali', 'Bilanciata', 'Priorità del provider', 'Provider preferito', 'Automatica', 'Timeout di inferenza in secondi', 'Se il provider preferito non è disponibile o non supporta un modello, il routing continua tramite un altro provider disponibile.',
        'Compatibilità Code Assist', 'Compatibilità facoltativa con client ed endpoint meno recenti.', 'Keep-alive per hosting', 'Richieste periodiche facoltative per piattaforme che sospendono i servizi inattivi.', 'URL keep-alive', 'Usa URL attuale', 'Intervallo keep-alive in secondi'
    ],
    ja: [
        'ここで保存した値は、実行環境で管理されていない限りローカルに保存されます。プロバイダー固有の設定はプロバイダーページで管理します。', 'サーバーアクセス', '次回の再起動後にサービスが使用するネットワークインターフェースを設定します。', '待ち受けアドレス', 'ポート', 'リスナーの変更にはアプリケーションの再起動が必要です。Docker のポート公開設定は別途変更してください。',
        '変換とランタイム', '互換性のための形式変換と応答復旧の動作を調整します。', '互換性のためにシステム指示を統合する', '利用可能な場合は推論内容を返す', '切り詰められた応答の復旧回数',
        'コンテキストの最適化', 'システム指示、ツール定義、最近のやり取りを保持しながら、長すぎる会話履歴を短縮します。', '長すぎる会話履歴を圧縮する', '圧縮を開始するトークン数', '圧縮後の目標トークン数', '保持する最近の会話ターン数',
        'コンソールアクセス', '現在の値を表示せずにコンソールのパスワードを変更します。', '設定済み', '現在のコンソールパスワード', '新しいコンソールパスワード', '変更しない場合は空欄', 'コンソールパスワードの確認', 'パスワードを更新',
        'フェイルオーバーポリシー', '自動無効化、再試行、代替認証情報の動作を設定します。', '指定したエラーコードで認証情報を自動的に無効化する', '自動無効化の対象エラーコード', '失敗したリクエストを別の認証情報で再試行する', '最大再試行回数', '再試行間隔（秒）',
        'ランタイムログ', 'サーバー側のログ詳細度とファイル保持数を設定します。', 'ログレベル', '最大ファイルサイズ（MB）', '保持するバックアップファイル数', '現在のログファイルが指定サイズに達すると自動的にローテーションします。',
        'ストレージとプロキシ', '認証情報の保存先と外向きネットワーク経路を設定します。', '認証情報ディレクトリ', '外向きプロキシ', 'サーバーから OAuth またはプロバイダー API に直接接続できない場合にプロキシを使用します。', '認証情報ディレクトリの変更にはアプリケーションの再起動が必要です。',
        'ルーティングポリシー', '正常な認証情報を自動的に分散するか、フォールバックを維持したまま特定のプロバイダーを優先します。', '認証情報の選択方法', '均等', 'プロバイダー優先', '優先プロバイダー', '自動', '推論タイムアウト（秒）', '優先プロバイダーが利用できない、またはモデルに対応していない場合は、別の正常なプロバイダーでルーティングを続行します。',
        'Code Assist 互換性', '旧クライアントおよび endpoint との互換性を必要に応じて有効にします。', 'ホスティング向け Keep-Alive', 'アイドル状態のサービスを停止するホスティング環境に、必要に応じて定期リクエストを送信します。', 'Keep-Alive URL', '現在の URL を使用', 'Keep-Alive 間隔（秒）'
    ],
    ko: [
        '여기에 저장한 값은 런타임 환경에서 관리하지 않는 한 로컬에 보관됩니다. 공급자별 설정은 공급자 페이지에서 관리합니다.', '서버 접근', '다음 재시작 후 서비스가 사용할 네트워크 인터페이스를 설정합니다.', '바인드 주소', '포트', '리스너 변경 사항을 적용하려면 애플리케이션을 다시 시작해야 합니다. Docker 포트 게시 설정은 별도로 변경해야 합니다.',
        '변환 및 런타임', '호환성 변환과 응답 복구 동작을 조정합니다.', '호환성을 위해 시스템 지침 통합', '사용 가능한 경우 추론 내용 반환', '잘린 응답 복구 시도 횟수',
        '컨텍스트 최적화', '시스템 지침, 도구 정의, 최근 대화를 유지하면서 지나치게 긴 대화 기록을 줄입니다.', '지나치게 긴 대화 기록 압축', '압축 임계값(토큰)', '목표 크기(토큰)', '보존할 최근 대화 턴',
        '콘솔 접근', '현재 값을 노출하지 않고 콘솔 비밀번호를 변경합니다.', '설정됨', '현재 콘솔 비밀번호', '새 콘솔 비밀번호', '변경하지 않으려면 비워 두세요', '콘솔 비밀번호 확인', '비밀번호 업데이트',
        '장애 조치 정책', '자동 비활성화, 재시도 및 대체 자격 증명 동작을 설정합니다.', '지정한 오류 코드에서 자격 증명 자동 비활성화', '자동 비활성화 오류 코드', '실패한 요청을 다른 자격 증명으로 재시도', '최대 재시도 횟수', '재시도 간격(초)',
        '런타임 로그', '서버 로그의 상세 수준과 제한된 파일 보존을 설정합니다.', '로그 수준', '최대 파일 크기(MB)', '보존할 백업 파일', '활성 로그 파일이 지정 크기에 도달하면 자동으로 순환됩니다.',
        '저장소 및 프록시', '자격 증명 저장 위치와 외부 네트워크 경로를 설정합니다.', '자격 증명 디렉터리', '외부 프록시', '서버가 OAuth 또는 공급자 API에 직접 연결할 수 없을 때 프록시를 사용합니다.', '자격 증명 디렉터리를 변경하면 애플리케이션을 다시 시작해야 합니다.',
        '라우팅 정책', '정상 자격 증명을 자동으로 분산하거나 장애 조치를 유지하면서 특정 공급자를 우선합니다.', '자격 증명 선택', '균형', '공급자 우선순위', '선호 공급자', '자동', '추론 제한 시간(초)', '선호 공급자를 사용할 수 없거나 모델과 호환되지 않으면 다른 정상 공급자를 통해 계속 라우팅합니다.',
        'Code Assist 호환성', '이전 클라이언트 및 endpoint와의 선택적 호환성입니다.', '호스팅 Keep-Alive', '유휴 서비스를 중단하는 호스팅 플랫폼에 선택적으로 주기적인 요청을 보냅니다.', 'Keep-Alive URL', '현재 URL 사용', 'Keep-Alive 간격(초)'
    ],
    pt: [
        'Os valores salvos aqui ficam armazenados localmente, exceto quando o ambiente de execução os gerencia. As configurações específicas de cada provedor ficam na página Provedores.', 'Acesso ao servidor', 'Controla a interface de rede usada pelo serviço após a próxima reinicialização.', 'Endereço de escuta', 'Porta', 'Alterações no listener exigem reiniciar o aplicativo. A publicação da porta do Docker deve ser atualizada separadamente.',
        'Tradução e execução', 'Ajuste a tradução de compatibilidade e a recuperação de respostas.', 'Unificar instruções do sistema para compatibilidade', 'Retornar o conteúdo de raciocínio quando disponível', 'Tentativas de recuperação de respostas truncadas',
        'Otimização de contexto', 'Reduza históricos de conversa muito longos preservando instruções do sistema, definições de ferramentas e interações recentes.', 'Comprimir históricos de conversa muito longos', 'Limite de compressão em tokens', 'Tamanho desejado em tokens', 'Interações recentes a preservar',
        'Acesso ao console', 'Altere a senha do console sem revelar o valor atual.', 'Configurada', 'Senha atual do console', 'Nova senha do console', 'Deixe em branco para não alterar', 'Confirmar senha do console', 'Atualizar senha',
        'Política de failover', 'Defina desativação automática, novas tentativas e uso de credenciais alternativas.', 'Desativar automaticamente credenciais nos códigos de erro configurados', 'Códigos de erro para desativação automática', 'Repetir solicitações com falha usando credenciais alternativas', 'Máximo de tentativas', 'Intervalo entre tentativas em segundos',
        'Logs de execução', 'Controle o nível de detalhes do servidor e a retenção limitada de arquivos.', 'Nível de log', 'Tamanho máximo do arquivo em MB', 'Arquivos de backup mantidos', 'Os logs são alternados automaticamente quando o arquivo ativo atinge o tamanho configurado.',
        'Armazenamento e proxy', 'Configure o armazenamento de credenciais e o roteamento de rede de saída.', 'Diretório de credenciais', 'Proxy de saída', 'Use o proxy quando o servidor não puder acessar diretamente o OAuth ou as APIs dos provedores.', 'A alteração do diretório exige reiniciar o aplicativo.',
        'Política de roteamento', 'Equilibre automaticamente as credenciais disponíveis ou priorize um provedor mantendo o fallback.', 'Seleção de credenciais', 'Equilibrada', 'Prioridade do provedor', 'Provedor preferencial', 'Automático', 'Tempo limite de inferência em segundos', 'Se o provedor preferencial estiver indisponível ou não aceitar um modelo, o roteamento continuará por outro provedor disponível.',
        'Compatibilidade com Code Assist', 'Compatibilidade opcional com clientes e endpoints antigos.', 'Keep-alive de hospedagem', 'Solicitações periódicas opcionais para plataformas que suspendem serviços ociosos.', 'URL de keep-alive', 'Usar URL atual', 'Intervalo de keep-alive em segundos'
    ],
    ru: [
        'Сохранённые здесь значения хранятся локально, если ими не управляет среда выполнения. Настройки отдельных провайдеров находятся на странице «Провайдеры».', 'Доступ к серверу', 'Задаёт сетевой интерфейс, который служба будет использовать после следующего перезапуска.', 'Адрес прослушивания', 'Порт', 'Изменения слушателя требуют перезапуска приложения. Публикацию порта Docker нужно обновить отдельно.',
        'Преобразование и среда выполнения', 'Настройте преобразование для совместимости и восстановление ответов.', 'Объединять системные инструкции для совместимости', 'Возвращать содержимое рассуждений, когда оно доступно', 'Попытки восстановления усечённого ответа',
        'Оптимизация контекста', 'Сокращайте слишком длинную историю диалога, сохраняя системные инструкции, определения инструментов и последние сообщения.', 'Сжимать слишком длинную историю диалога', 'Порог сжатия в токенах', 'Целевой размер в токенах', 'Сохраняемые последние ходы диалога',
        'Доступ к консоли', 'Измените пароль консоли, не раскрывая его текущее значение.', 'Настроен', 'Текущий пароль консоли', 'Новый пароль консоли', 'Оставьте пустым, чтобы не менять', 'Подтвердите пароль консоли', 'Обновить пароль',
        'Политика отказоустойчивости', 'Настройте автоматическое отключение, повторные попытки и использование других учётных данных.', 'Автоматически отключать учётные данные при указанных кодах ошибок', 'Коды ошибок для автоматического отключения', 'Повторять неудачные запросы с другими учётными данными', 'Максимум повторных попыток', 'Интервал между попытками в секундах',
        'Журналы среды выполнения', 'Настройте подробность серверных журналов и ограниченное хранение файлов.', 'Уровень журналирования', 'Максимальный размер файла в МБ', 'Сохраняемые резервные файлы', 'При достижении заданного размера активный файл журнала автоматически ротируется.',
        'Хранилище и прокси', 'Настройте хранение учётных данных и исходящую сетевую маршрутизацию.', 'Каталог учётных данных', 'Исходящий прокси', 'Используйте прокси, если сервер не может напрямую обратиться к OAuth или API провайдеров.', 'Изменение каталога требует перезапуска приложения.',
        'Политика маршрутизации', 'Автоматически распределяйте запросы между доступными учётными данными или отдавайте приоритет провайдеру, сохраняя резервный маршрут.', 'Выбор учётных данных', 'Сбалансированный', 'Приоритет провайдера', 'Предпочтительный провайдер', 'Автоматически', 'Тайм-аут вывода в секундах', 'Если предпочтительный провайдер недоступен или не поддерживает модель, запрос будет направлен другому доступному провайдеру.',
        'Совместимость с Code Assist', 'Необязательная совместимость со старыми клиентами и endpoint.', 'Keep-Alive для хостинга', 'Необязательные периодические запросы для платформ, приостанавливающих неактивные службы.', 'URL Keep-Alive', 'Использовать текущий URL', 'Интервал Keep-Alive в секундах'
    ],
    th: [
        'ค่าที่บันทึกที่นี่จะเก็บไว้ในเครื่อง เว้นแต่สภาพแวดล้อมรันไทม์เป็นผู้จัดการ การตั้งค่าเฉพาะผู้ให้บริการอยู่ในหน้าผู้ให้บริการ', 'การเข้าถึงเซิร์ฟเวอร์', 'กำหนดอินเทอร์เฟซเครือข่ายที่บริการจะใช้หลังจากเริ่มใหม่ครั้งถัดไป', 'ที่อยู่สำหรับรับการเชื่อมต่อ', 'พอร์ต', 'การเปลี่ยน listener ต้องเริ่มแอปพลิเคชันใหม่ และต้องแก้การเผยแพร่พอร์ต Docker แยกต่างหาก',
        'การแปลงและรันไทม์', 'ปรับการแปลงเพื่อความเข้ากันได้และการกู้คืนการตอบกลับ', 'รวมคำสั่งระบบเพื่อความเข้ากันได้', 'ส่งคืนเนื้อหาการให้เหตุผลเมื่อมี', 'จำนวนครั้งที่กู้คืนการตอบกลับที่ถูกตัด',
        'การปรับบริบทให้เหมาะสม', 'ลดประวัติการสนทนาที่ยาวเกินไปโดยยังคงคำสั่งระบบ นิยามเครื่องมือ และข้อความล่าสุด', 'บีบอัดประวัติการสนทนาที่ยาวเกินไป', 'เกณฑ์การบีบอัดเป็นโทเค็น', 'ขนาดเป้าหมายเป็นโทเค็น', 'จำนวนรอบสนทนาล่าสุดที่เก็บไว้',
        'การเข้าถึงคอนโซล', 'เปลี่ยนรหัสผ่านคอนโซลโดยไม่แสดงค่าปัจจุบัน', 'ตั้งค่าแล้ว', 'รหัสผ่านคอนโซลปัจจุบัน', 'รหัสผ่านคอนโซลใหม่', 'เว้นว่างไว้หากไม่ต้องการเปลี่ยน', 'ยืนยันรหัสผ่านคอนโซล', 'อัปเดตรหัสผ่าน',
        'นโยบายสำรอง', 'กำหนดการปิดใช้งานอัตโนมัติ การลองใหม่ และการใช้ข้อมูลรับรองสำรอง', 'ปิดใช้งานข้อมูลรับรองอัตโนมัติเมื่อพบรหัสข้อผิดพลาดที่กำหนด', 'รหัสข้อผิดพลาดสำหรับปิดใช้งานอัตโนมัติ', 'ลองคำขอที่ล้มเหลวใหม่ด้วยข้อมูลรับรองอื่น', 'จำนวนครั้งที่ลองใหม่สูงสุด', 'ช่วงเวลาลองใหม่เป็นวินาที',
        'บันทึกรันไทม์', 'กำหนดระดับรายละเอียดฝั่งเซิร์ฟเวอร์และจำนวนไฟล์ที่เก็บไว้', 'ระดับบันทึก', 'ขนาดไฟล์สูงสุดเป็น MB', 'ไฟล์สำรองที่เก็บไว้', 'ระบบจะหมุนเวียนบันทึกอัตโนมัติเมื่อไฟล์ปัจจุบันถึงขนาดที่กำหนด',
        'พื้นที่จัดเก็บและพร็อกซี', 'กำหนดที่เก็บข้อมูลรับรองและเส้นทางเครือข่ายขาออก', 'ไดเรกทอรีข้อมูลรับรอง', 'พร็อกซีขาออก', 'ใช้พร็อกซีเมื่อเซิร์ฟเวอร์เข้าถึง OAuth หรือ API ของผู้ให้บริการโดยตรงไม่ได้', 'การเปลี่ยนไดเรกทอรีข้อมูลรับรองต้องเริ่มแอปพลิเคชันใหม่',
        'นโยบายการกำหนดเส้นทาง', 'กระจายคำขอระหว่างข้อมูลรับรองที่พร้อมใช้งานโดยอัตโนมัติ หรือให้ความสำคัญกับผู้ให้บริการหนึ่งรายโดยยังคงเส้นทางสำรอง', 'การเลือกข้อมูลรับรอง', 'สมดุล', 'ลำดับความสำคัญของผู้ให้บริการ', 'ผู้ให้บริการที่ต้องการ', 'อัตโนมัติ', 'เวลาหมดอายุการอนุมานเป็นวินาที', 'หากผู้ให้บริการที่ต้องการใช้ไม่ได้หรือไม่รองรับโมเดล ระบบจะกำหนดเส้นทางผ่านผู้ให้บริการอื่นที่พร้อมใช้งาน',
        'ความเข้ากันได้กับ Code Assist', 'รองรับไคลเอนต์และ endpoint รุ่นเก่าแบบเลือกใช้', 'Keep-Alive สำหรับโฮสติ้ง', 'ส่งคำขอเป็นระยะสำหรับแพลตฟอร์มที่หยุดบริการเมื่อไม่มีการใช้งาน', 'URL Keep-Alive', 'ใช้ URL ปัจจุบัน', 'ช่วงเวลา Keep-Alive เป็นวินาที'
    ],
    tr: [
        'Burada kaydedilen değerler çalışma ortamı tarafından yönetilmiyorsa yerel olarak saklanır. Sağlayıcıya özgü ayarlar Sağlayıcılar sayfasından yönetilir.', 'Sunucu Erişimi', 'Hizmetin bir sonraki yeniden başlatmadan sonra kullanacağı ağ arabirimini belirler.', 'Dinleme adresi', 'Bağlantı noktası', 'Dinleyici değişiklikleri uygulamanın yeniden başlatılmasını gerektirir. Docker bağlantı noktası yayını ayrıca güncellenmelidir.',
        'Dönüştürme ve Çalışma Zamanı', 'Uyumluluk dönüştürmesini ve yanıt kurtarma davranışını ayarlayın.', 'Uyumluluk için sistem talimatlarını birleştir', 'Varsa akıl yürütme içeriğini döndür', 'Kesilen yanıtı kurtarma denemeleri',
        'Bağlam Optimizasyonu', 'Sistem talimatlarını, araç tanımlarını ve son konuşma turlarını koruyarak fazla uzun konuşma geçmişini kısaltın.', 'Fazla uzun konuşma geçmişini sıkıştır', 'Belirteç cinsinden sıkıştırma eşiği', 'Belirteç cinsinden hedef boyut', 'Korunacak son konuşma turları',
        'Konsol Erişimi', 'Mevcut değeri göstermeden konsol parolasını değiştirin.', 'Yapılandırıldı', 'Mevcut konsol parolası', 'Yeni konsol parolası', 'Değiştirmemek için boş bırakın', 'Konsol parolasını doğrulayın', 'Parolayı güncelle',
        'Yük Devretme Politikası', 'Otomatik devre dışı bırakma, yeniden deneme ve alternatif kimlik bilgisi davranışını belirleyin.', 'Yapılandırılan hata kodlarında kimlik bilgilerini otomatik devre dışı bırak', 'Otomatik devre dışı bırakma hata kodları', 'Başarısız istekleri alternatif kimlik bilgileriyle yeniden dene', 'En fazla yeniden deneme', 'Saniye cinsinden yeniden deneme aralığı',
        'Çalışma Zamanı Günlükleri', 'Sunucu tarafı ayrıntı düzeyini ve sınırlı dosya saklamayı yönetin.', 'Günlük düzeyi', 'MB cinsinden en büyük dosya boyutu', 'Saklanan yedek dosyalar', 'Etkin dosya yapılandırılan boyuta ulaştığında günlükler otomatik olarak döndürülür.',
        'Depolama ve Proxy', 'Kimlik bilgisi depolamasını ve dış ağ yönlendirmesini ayarlayın.', 'Kimlik bilgileri dizini', 'Giden proxy', 'Sunucu OAuth veya sağlayıcı API’lerine doğrudan erişemediğinde proxy kullanın.', 'Kimlik bilgileri dizinini değiştirmek uygulamanın yeniden başlatılmasını gerektirir.',
        'Yönlendirme Politikası', 'Sağlıklı kimlik bilgilerini otomatik dengeleyin veya geri dönüşü korurken bir sağlayıcıyı tercih edin.', 'Kimlik bilgisi seçimi', 'Dengeli', 'Sağlayıcı önceliği', 'Tercih edilen sağlayıcı', 'Otomatik', 'Saniye cinsinden çıkarım zaman aşımı', 'Tercih edilen sağlayıcı kullanılamıyorsa veya modelle uyumlu değilse yönlendirme başka bir sağlıklı sağlayıcı üzerinden devam eder.',
        'Code Assist Uyumluluğu', 'Eski istemci ve endpoint uyumluluğu için isteğe bağlı ayarlar.', 'Barındırma Keep-Alive', 'Boştaki hizmetleri askıya alan platformlar için isteğe bağlı düzenli istekler.', 'Keep-Alive URL’si', 'Geçerli URL’yi kullan', 'Saniye cinsinden Keep-Alive aralığı'
    ]
};

for (const [locale, values] of Object.entries(SETTINGS_PAGE_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(SETTINGS_PAGE_KEYS.map((key, index) => [key, values[index]])));
}

const PROVIDER_CATALOG_KEYS = [
    'providers.catalog', 'providers.catalog_description', 'providers.find', 'providers.search',
    'providers.account_provider', 'providers.api_key_provider', 'providers.model_server',
    'providers.antigravity_description', 'providers.ai_studio_description', 'providers.grok_description',
    'providers.spacexai_description', 'providers.codex_description', 'providers.openai_description',
    'providers.claude_code_description', 'providers.claude_platform_description',
    'providers.ollama_description', 'providers.no_matches'
];

const PROVIDER_CATALOG_VALUES = {
    en: ['Provider Catalog', 'Choose a connection type, then add credentials to the shared routing pool.', 'Find a provider', 'Search providers', 'Account Provider', 'API Key Provider', 'Model Server', 'Connect Google Antigravity accounts through OAuth or import existing credential archives.', 'Add Gemini API keys for native Google model access and automatic provider fallback.', 'Connect a Grok Build account through OAuth and route its available models through the shared pool.', 'Add SpaceXAI Console API keys for direct Grok Build model access and automatic provider fallback.', 'Authorize a ChatGPT account with the OpenAI device flow and route Codex models through the pool.', 'Validate OpenAI API keys, discover available models, and route requests through the shared pool.', 'Authorize an Anthropic account and route its available Claude models through the shared pool.', 'Add Anthropic API keys, discover available Claude models, and route requests through the pool.', 'Connect local, remote, or cloud Ollama endpoints and route every model they expose.', 'No providers match your search.'],
    'zh-CN': ['提供商目录', '选择连接方式，然后将凭据添加到共享路由池。', '查找提供商', '搜索提供商', '账户提供商', 'API 密钥提供商', '模型服务器', '通过 OAuth 连接 Google Antigravity 账户，或导入已有的凭据归档。', '添加 Gemini API 密钥，以原生访问 Google 模型并自动切换提供商。', '通过 OAuth 连接 Grok Build 账户，并通过共享池路由其可用模型。', '添加 SpaceXAI Console API 密钥，以直接访问 Grok Build 模型并自动切换提供商。', '通过 OpenAI 设备授权流程连接 ChatGPT 账户，并通过凭据池路由 Codex 模型。', '验证 OpenAI API 密钥、发现可用模型，并通过共享池路由请求。', '授权 Anthropic 账户，并通过共享池路由其可用的 Claude 模型。', '添加 Anthropic API 密钥、发现可用的 Claude 模型，并通过凭据池路由请求。', '连接本地、远程或云端 Ollama endpoint，并路由其公开的全部模型。', '没有与搜索条件匹配的提供商。'],
    'zh-TW': ['供應商目錄', '選擇連線方式，然後將憑證加入共用路由集區。', '尋找供應商', '搜尋供應商', '帳戶供應商', 'API 金鑰供應商', '模型伺服器', '透過 OAuth 連線 Google Antigravity 帳戶，或匯入現有的憑證封存檔。', '新增 Gemini API 金鑰，以原生存取 Google 模型並自動切換供應商。', '透過 OAuth 連線 Grok Build 帳戶，並從共用集區路由其可用模型。', '新增 SpaceXAI Console API 金鑰，以直接存取 Grok Build 模型並自動切換供應商。', '透過 OpenAI 裝置授權流程連線 ChatGPT 帳戶，並從憑證集區路由 Codex 模型。', '驗證 OpenAI API 金鑰、探索可用模型，並透過共用集區路由請求。', '授權 Anthropic 帳戶，並透過共用集區路由其可用的 Claude 模型。', '新增 Anthropic API 金鑰、探索可用的 Claude 模型，並透過集區路由請求。', '連線本機、遠端或雲端 Ollama endpoint，並路由其公開的所有模型。', '沒有符合搜尋條件的供應商。'],
    de: ['Provider-Katalog', 'Wählen Sie eine Verbindungsart und fügen Sie die Zugangsdaten dem gemeinsamen Routing-Pool hinzu.', 'Provider suchen', 'Provider durchsuchen', 'Konto-Provider', 'API-Schlüssel-Provider', 'Modellserver', 'Verbinden Sie Google-Antigravity-Konten per OAuth oder importieren Sie vorhandene Zugangsdatenarchive.', 'Fügen Sie Gemini-API-Schlüssel für nativen Zugriff auf Google-Modelle und automatisches Provider-Fallback hinzu.', 'Verbinden Sie ein Grok-Build-Konto per OAuth und routen Sie dessen verfügbare Modelle über den gemeinsamen Pool.', 'Fügen Sie SpaceXAI-Console-API-Schlüssel für direkten Zugriff auf Grok-Build-Modelle und automatisches Provider-Fallback hinzu.', 'Autorisieren Sie ein ChatGPT-Konto über den OpenAI-Gerätefluss und routen Sie Codex-Modelle über den Pool.', 'Prüfen Sie OpenAI-API-Schlüssel, ermitteln Sie verfügbare Modelle und routen Sie Anfragen über den gemeinsamen Pool.', 'Autorisieren Sie ein Anthropic-Konto und routen Sie dessen verfügbare Claude-Modelle über den gemeinsamen Pool.', 'Fügen Sie Anthropic-API-Schlüssel hinzu, ermitteln Sie verfügbare Claude-Modelle und routen Sie Anfragen über den Pool.', 'Verbinden Sie lokale, entfernte oder cloudbasierte Ollama-Endpunkte und routen Sie alle bereitgestellten Modelle.', 'Keine Provider entsprechen Ihrer Suche.'],
    es: ['Catálogo de proveedores', 'Elige un tipo de conexión y añade las credenciales al grupo de enrutamiento compartido.', 'Buscar un proveedor', 'Buscar proveedores', 'Proveedor de cuenta', 'Proveedor de clave API', 'Servidor de modelos', 'Conecta cuentas de Google Antigravity mediante OAuth o importa archivos de credenciales existentes.', 'Añade claves API de Gemini para acceder de forma nativa a los modelos de Google y disponer de respaldo automático entre proveedores.', 'Conecta una cuenta de Grok Build mediante OAuth y enruta sus modelos disponibles a través del grupo compartido.', 'Añade claves API de SpaceXAI Console para acceder directamente a modelos de Grok Build y disponer de respaldo automático.', 'Autoriza una cuenta de ChatGPT mediante el flujo de dispositivo de OpenAI y enruta modelos de Codex a través del grupo.', 'Valida claves API de OpenAI, detecta los modelos disponibles y enruta solicitudes mediante el grupo compartido.', 'Autoriza una cuenta de Anthropic y enruta sus modelos Claude disponibles mediante el grupo compartido.', 'Añade claves API de Anthropic, detecta modelos Claude disponibles y enruta solicitudes mediante el grupo.', 'Conecta endpoints de Ollama locales, remotos o en la nube y enruta todos los modelos que publiquen.', 'Ningún proveedor coincide con la búsqueda.'],
    fr: ['Catalogue des fournisseurs', 'Choisissez un mode de connexion, puis ajoutez les identifiants au pool de routage partagé.', 'Rechercher un fournisseur', 'Rechercher des fournisseurs', 'Fournisseur avec compte', 'Fournisseur avec clé API', 'Serveur de modèles', 'Connectez des comptes Google Antigravity par OAuth ou importez des archives d’identifiants existantes.', 'Ajoutez des clés API Gemini pour accéder directement aux modèles Google avec basculement automatique entre fournisseurs.', 'Connectez un compte Grok Build par OAuth et routez ses modèles disponibles via le pool partagé.', 'Ajoutez des clés API SpaceXAI Console pour accéder directement aux modèles Grok Build avec basculement automatique.', 'Autorisez un compte ChatGPT avec le flux d’appareil OpenAI et routez les modèles Codex via le pool.', 'Validez des clés API OpenAI, détectez les modèles disponibles et routez les requêtes via le pool partagé.', 'Autorisez un compte Anthropic et routez ses modèles Claude disponibles via le pool partagé.', 'Ajoutez des clés API Anthropic, détectez les modèles Claude disponibles et routez les requêtes via le pool.', 'Connectez des endpoints Ollama locaux, distants ou cloud et routez tous les modèles qu’ils exposent.', 'Aucun fournisseur ne correspond à votre recherche.'],
    id: ['Katalog Penyedia', 'Pilih jenis koneksi, lalu tambahkan kredensial ke pool perutean bersama.', 'Cari penyedia', 'Telusuri penyedia', 'Penyedia Akun', 'Penyedia Kunci API', 'Server Model', 'Hubungkan akun Google Antigravity melalui OAuth atau impor arsip kredensial yang sudah ada.', 'Tambahkan kunci API Gemini untuk akses langsung ke model Google dan failover penyedia otomatis.', 'Hubungkan akun Grok Build melalui OAuth dan rutekan model yang tersedia melalui pool bersama.', 'Tambahkan kunci API SpaceXAI Console untuk akses langsung ke model Grok Build dan failover penyedia otomatis.', 'Otorisasi akun ChatGPT melalui alur perangkat OpenAI dan rutekan model Codex melalui pool.', 'Validasi kunci API OpenAI, temukan model yang tersedia, lalu rutekan permintaan melalui pool bersama.', 'Otorisasi akun Anthropic dan rutekan model Claude yang tersedia melalui pool bersama.', 'Tambahkan kunci API Anthropic, temukan model Claude yang tersedia, lalu rutekan permintaan melalui pool.', 'Hubungkan endpoint Ollama lokal, jarak jauh, atau cloud dan rutekan semua model yang tersedia.', 'Tidak ada penyedia yang cocok dengan pencarian Anda.'],
    it: ['Catalogo provider', 'Scegli un tipo di connessione e aggiungi le credenziali al pool di routing condiviso.', 'Trova un provider', 'Cerca provider', 'Provider con account', 'Provider con chiave API', 'Server di modelli', 'Collega account Google Antigravity tramite OAuth o importa archivi di credenziali esistenti.', 'Aggiungi chiavi API Gemini per accedere direttamente ai modelli Google con fallback automatico tra provider.', 'Collega un account Grok Build tramite OAuth e instrada i modelli disponibili attraverso il pool condiviso.', 'Aggiungi chiavi API SpaceXAI Console per accedere direttamente ai modelli Grok Build con fallback automatico.', 'Autorizza un account ChatGPT con il flusso dispositivo OpenAI e instrada i modelli Codex attraverso il pool.', 'Convalida le chiavi API OpenAI, rileva i modelli disponibili e instrada le richieste tramite il pool condiviso.', 'Autorizza un account Anthropic e instrada i modelli Claude disponibili tramite il pool condiviso.', 'Aggiungi chiavi API Anthropic, rileva i modelli Claude disponibili e instrada le richieste tramite il pool.', 'Collega endpoint Ollama locali, remoti o cloud e instrada tutti i modelli esposti.', 'Nessun provider corrisponde alla ricerca.'],
    ja: ['プロバイダーカタログ', '接続方法を選び、認証情報を共有ルーティングプールに追加します。', 'プロバイダーを探す', 'プロバイダーを検索', 'アカウントプロバイダー', 'API キープロバイダー', 'モデルサーバー', 'OAuth で Google Antigravity アカウントを接続するか、既存の認証情報アーカイブをインポートします。', 'Gemini API キーを追加し、Google モデルへのネイティブアクセスとプロバイダーの自動フォールバックを利用します。', 'OAuth で Grok Build アカウントを接続し、利用可能なモデルを共有プール経由でルーティングします。', 'SpaceXAI Console API キーを追加し、Grok Build モデルへの直接アクセスと自動フォールバックを利用します。', 'OpenAI のデバイスフローで ChatGPT アカウントを認証し、Codex モデルをプール経由でルーティングします。', 'OpenAI API キーを検証して利用可能なモデルを検出し、共有プール経由でリクエストをルーティングします。', 'Anthropic アカウントを認証し、利用可能な Claude モデルを共有プール経由でルーティングします。', 'Anthropic API キーを追加して利用可能な Claude モデルを検出し、プール経由でリクエストをルーティングします。', 'ローカル、リモート、またはクラウドの Ollama endpoint に接続し、公開されているすべてのモデルをルーティングします。', '検索条件に一致するプロバイダーはありません。'],
    ko: ['공급자 카탈로그', '연결 방식을 선택한 뒤 자격 증명을 공유 라우팅 풀에 추가하세요.', '공급자 찾기', '공급자 검색', '계정 공급자', 'API 키 공급자', '모델 서버', 'OAuth로 Google Antigravity 계정을 연결하거나 기존 자격 증명 아카이브를 가져옵니다.', 'Gemini API 키를 추가해 Google 모델에 직접 액세스하고 공급자 자동 장애 조치를 사용합니다.', 'OAuth로 Grok Build 계정을 연결하고 사용可能な 모델을 공유 풀을 통해 라우팅합니다.', 'SpaceXAI Console API 키를 추가해 Grok Build 모델에 직접 액세스하고 자동 장애 조치를 사용합니다.', 'OpenAI 디바이스 흐름으로 ChatGPT 계정을 인증하고 Codex 모델을 풀을 통해 라우팅합니다.', 'OpenAI API 키를 검증하고 사용 가능한 모델을 검색한 뒤 공유 풀을 통해 요청을 라우팅합니다.', 'Anthropic 계정을 인증하고 사용可能な Claude 모델을 공유 풀을 통해 라우팅합니다.', 'Anthropic API 키를 추가하고 사용 가능한 Claude 모델을 검색한 뒤 풀을 통해 요청을 라우팅합니다.', '로컬, 원격 또는 클라우드 Ollama endpoint를 연결하고 제공되는 모든 모델을 라우팅합니다.', '검색 조건과 일치하는 공급자가 없습니다.'],
    pt: ['Catálogo de provedores', 'Escolha um tipo de conexão e adicione as credenciais ao pool de roteamento compartilhado.', 'Encontrar um provedor', 'Pesquisar provedores', 'Provedor por conta', 'Provedor por chave de API', 'Servidor de modelos', 'Conecte contas do Google Antigravity via OAuth ou importe arquivos de credenciais existentes.', 'Adicione chaves de API Gemini para acesso nativo aos modelos Google e fallback automático entre provedores.', 'Conecte uma conta do Grok Build via OAuth e roteie os modelos disponíveis pelo pool compartilhado.', 'Adicione chaves de API do SpaceXAI Console para acesso direto aos modelos Grok Build e fallback automático.', 'Autorize uma conta do ChatGPT pelo fluxo de dispositivo da OpenAI e roteie modelos Codex pelo pool.', 'Valide chaves de API da OpenAI, descubra os modelos disponíveis e roteie solicitações pelo pool compartilhado.', 'Autorize uma conta Anthropic e roteie os modelos Claude disponíveis pelo pool compartilhado.', 'Adicione chaves de API Anthropic, descubra modelos Claude disponíveis e roteie solicitações pelo pool.', 'Conecte endpoints Ollama locais, remotos ou na nuvem e roteie todos os modelos publicados.', 'Nenhum provedor corresponde à pesquisa.'],
    ru: ['Каталог провайдеров', 'Выберите способ подключения и добавьте учётные данные в общий пул маршрутизации.', 'Найти провайдера', 'Поиск провайдеров', 'Провайдер с учётной записью', 'Провайдер с ключом API', 'Сервер моделей', 'Подключите учётные записи Google Antigravity через OAuth или импортируйте существующие архивы учётных данных.', 'Добавьте ключи API Gemini для прямого доступа к моделям Google и автоматического переключения между провайдерами.', 'Подключите учётную запись Grok Build через OAuth и направляйте доступные модели через общий пул.', 'Добавьте ключи API SpaceXAI Console для прямого доступа к моделям Grok Build и автоматического переключения.', 'Авторизуйте учётную запись ChatGPT через поток устройства OpenAI и направляйте модели Codex через пул.', 'Проверьте ключи API OpenAI, обнаружьте доступные модели и направляйте запросы через общий пул.', 'Авторизуйте учётную запись Anthropic и направляйте доступные модели Claude через общий пул.', 'Добавьте ключи API Anthropic, обнаружьте доступные модели Claude и направляйте запросы через пул.', 'Подключите локальные, удалённые или облачные endpoint Ollama и направляйте все опубликованные ими модели.', 'Провайдеры по вашему запросу не найдены.'],
    th: ['แค็ตตาล็อกผู้ให้บริการ', 'เลือกวิธีเชื่อมต่อ แล้วเพิ่มข้อมูลรับรองลงในพูลการกำหนดเส้นทางร่วม', 'ค้นหาผู้ให้บริการ', 'ค้นหาผู้ให้บริการ', 'ผู้ให้บริการแบบบัญชี', 'ผู้ให้บริการแบบคีย์ API', 'เซิร์ฟเวอร์โมเดล', 'เชื่อมต่อบัญชี Google Antigravity ผ่าน OAuth หรือนำเข้าไฟล์ข้อมูลรับรองที่มีอยู่', 'เพิ่มคีย์ API ของ Gemini เพื่อเข้าถึงโมเดล Google โดยตรงและสลับผู้ให้บริการอัตโนมัติ', 'เชื่อมต่อบัญชี Grok Build ผ่าน OAuth และกำหนดเส้นทางโมเดลที่ใช้ได้ผ่านพูลร่วม', 'เพิ่มคีย์ API ของ SpaceXAI Console เพื่อเข้าถึงโมเดล Grok Build โดยตรงและสลับผู้ให้บริการอัตโนมัติ', 'อนุญาตบัญชี ChatGPT ผ่านขั้นตอนอุปกรณ์ của OpenAI และกำหนดเส้นทางโมเดล Codex ผ่านพูล', 'ตรวจสอบคีย์ API ของ OpenAI ค้นหาโมเดลที่ใช้ได้ และกำหนดเส้นทางคำขอผ่านพูลร่วม', 'อนุญาตบัญชี Anthropic และกำหนดเส้นทางโมเดล Claude ที่ใช้ได้ผ่านพูลร่วม', 'เพิ่มคีย์ API ของ Anthropic ค้นหาโมเดล Claude ที่ใช้ได้ และกำหนดเส้นทางคำขอผ่านพูล', 'เชื่อมต่อ endpoint Ollama ในเครื่อง ระยะไกล หรือบนคลาวด์ และกำหนดเส้นทางทุกโมเดลที่เปิดให้ใช้', 'ไม่พบผู้ให้บริการที่ตรงกับการค้นหา'],
    tr: ['Sağlayıcı Kataloğu', 'Bir bağlantı türü seçin ve kimlik bilgilerini paylaşılan yönlendirme havuzuna ekleyin.', 'Sağlayıcı bul', 'Sağlayıcılarda ara', 'Hesap Sağlayıcısı', 'API Anahtarı Sağlayıcısı', 'Model Sunucusu', 'Google Antigravity hesaplarını OAuth ile bağlayın veya mevcut kimlik bilgisi arşivlerini içe aktarın.', 'Google modellerine doğrudan erişmek ve otomatik sağlayıcı yedeklemesi kullanmak için Gemini API anahtarları ekleyin.', 'Bir Grok Build hesabını OAuth ile bağlayın ve kullanılabilir modellerini paylaşılan havuz üzerinden yönlendirin.', 'Grok Build modellerine doğrudan erişmek ve otomatik yedekleme kullanmak için SpaceXAI Console API anahtarları ekleyin.', 'OpenAI cihaz akışıyla bir ChatGPT hesabını yetkilendirin ve Codex modellerini havuz üzerinden yönlendirin.', 'OpenAI API anahtarlarını doğrulayın, kullanılabilir modelleri keşfedin ve istekleri paylaşılan havuz üzerinden yönlendirin.', 'Bir Anthropic hesabını yetkilendirin ve kullanılabilir Claude modellerini paylaşılan havuz üzerinden yönlendirin.', 'Anthropic API anahtarları ekleyin, kullanılabilir Claude modellerini keşfedin ve istekleri havuz üzerinden yönlendirin.', 'Yerel, uzak veya bulut Ollama endpointlerini bağlayın ve sundukları tüm modelleri yönlendirin.', 'Aramanızla eşleşen sağlayıcı bulunamadı.'],
    vi: ['Danh mục nhà cung cấp', 'Chọn phương thức kết nối, sau đó thêm thông tin xác thực vào kho định tuyến dùng chung.', 'Tìm nhà cung cấp', 'Tìm kiếm nhà cung cấp', 'Nhà cung cấp tài khoản', 'Nhà cung cấp khóa API', 'Máy chủ mô hình', 'Kết nối tài khoản Google Antigravity qua OAuth hoặc nhập kho lưu trữ thông tin xác thực hiện có.', 'Thêm khóa API Gemini để truy cập trực tiếp mô hình Google và tự động chuyển sang nhà cung cấp dự phòng.', 'Kết nối tài khoản Grok Build qua OAuth và định tuyến các mô hình khả dụng qua kho dùng chung.', 'Thêm khóa API SpaceXAI Console để truy cập trực tiếp mô hình Grok Build và tự động chuyển sang nhà cung cấp dự phòng.', 'Cấp quyền cho tài khoản ChatGPT bằng quy trình thiết bị của OpenAI và định tuyến mô hình Codex qua kho.', 'Xác thực khóa API OpenAI, khám phá các mô hình khả dụng và định tuyến yêu cầu qua kho dùng chung.', 'Cấp quyền cho tài khoản Anthropic và định tuyến các mô hình Claude khả dụng qua kho dùng chung.', 'Thêm khóa API Anthropic, khám phá các mô hình Claude khả dụng và định tuyến yêu cầu qua kho.', 'Kết nối endpoint Ollama cục bộ, từ xa hoặc trên đám mây và định tuyến mọi mô hình mà endpoint cung cấp.', 'Không có nhà cung cấp nào khớp với nội dung tìm kiếm.']
};

for (const [locale, values] of Object.entries(PROVIDER_CATALOG_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(PROVIDER_CATALOG_KEYS.map((key, index) => [key, values[index]])));
}

const CONSOLE_CHROME_KEYS = [
    'site_footer', 'open_navigation', 'primary_navigation', 'console', 'loading_version',
    'loading', 'loading_api_key', 'copy_api_key', 'show_api_key', 'regenerate_api_key',
    'copy_base_url', 'initialize', 'request', 'provider_activity', 'loading_request_breakdown',
    'credential', 'requests', 'success', 'tokens', 'loading_provider_models',
    'available_providers', 'loading_provider_credentials', 'loading_system_configuration', 'password_status',
    'debug', 'info', 'warning', 'error', 'critical',
    'models.priority_fallback', 'models.priority_fallback_description', 'models.fallback_order',
    'models.fallback_order_description', 'models.selection_description', 'models.unavailable_routes_description'
];

const CONSOLE_CHROME_VALUES = {
    en: ['Site footer', 'Open navigation', 'Primary navigation', 'Console', 'Loading version', 'Loading', 'Loading API key', 'Copy API key', 'Show API key', 'Regenerate API key', 'Copy base URL', 'Initialize', 'Request', 'Provider activity', 'Loading request breakdown', 'Credential', 'Requests', 'Success', 'Tokens', 'Loading provider models', 'Available providers', 'Loading provider credentials', 'Loading system configuration', 'Password status', 'Debug', 'Info', 'Warning', 'Error', 'Critical', 'Priority fallback', 'Credentials are balanced within each model before routing continues to the next model.', 'Fallback Order', 'Move models to define which one is attempted first.', 'Select models discovered from enabled provider credentials.', 'Unavailable credential-model routes appear here after an upstream 404 response. Other credentials, providers, and fallback models remain available.'],
    'zh-CN': ['网站页脚', '打开导航', '主导航', '控制台', '正在加载版本', '正在加载', '正在加载 API 密钥', '复制 API 密钥', '显示 API 密钥', '重新生成 API 密钥', '复制基础 URL', '初始化', '请求', '提供商活动', '正在加载请求明细', '凭据', '请求', '成功', '令牌', '正在加载提供商模型', '可用提供商', '正在加载提供商凭据', '正在加载系统配置', '密码状态', '调试', '信息', '警告', '错误', '严重', '按优先级回退', '系统会先在每个模型的凭据之间均衡分配，再继续尝试下一个模型。', '回退顺序', '移动模型以确定优先尝试顺序。', '选择从已启用提供商凭据中发现的模型。', '上游返回 404 后，不可用的凭据与模型组合会显示在此处；其他凭据、提供商和回退模型仍可继续使用。'],
    'zh-TW': ['網站頁尾', '開啟導覽', '主要導覽', '主控台', '正在載入版本', '正在載入', '正在載入 API 金鑰', '複製 API 金鑰', '顯示 API 金鑰', '重新產生 API 金鑰', '複製基礎 URL', '初始化', '請求', '供應商活動', '正在載入請求明細', '憑證', '請求', '成功', '權杖', '正在載入供應商模型', '可用的供應商', '正在載入供應商憑證', '正在載入系統設定', '密碼狀態', '偵錯', '資訊', '警告', '錯誤', '嚴重', '依優先順序容錯', '系統會先在每個模型的憑證之間平均分配，再繼續嘗試下一個模型。', '容錯順序', '移動模型以決定優先嘗試的順序。', '選取從已啟用供應商憑證中偵測到的模型。', '上游回傳 404 後，無法使用的憑證與模型組合會顯示於此；其他憑證、供應商與容錯模型仍可繼續使用。'],
    de: ['Seitenfuß', 'Navigation öffnen', 'Hauptnavigation', 'Konsole', 'Version wird geladen', 'Wird geladen', 'API-Schlüssel wird geladen', 'API-Schlüssel kopieren', 'API-Schlüssel anzeigen', 'API-Schlüssel neu erzeugen', 'Basis-URL kopieren', 'Initialisierung', 'Anfrage', 'Provider-Aktivität', 'Anfrageübersicht wird geladen', 'Zugang', 'Anfragen', 'Erfolg', 'Token', 'Provider-Modelle werden geladen', 'Verfügbare Provider', 'Provider-Zugänge werden geladen', 'Systemkonfiguration wird geladen', 'Passwortstatus', 'Debug', 'Info', 'Warnung', 'Fehler', 'Kritisch', 'Priorisiertes Fallback', 'Innerhalb jedes Modells werden die Zugänge ausgeglichen, bevor das nächste Modell versucht wird.', 'Fallback-Reihenfolge', 'Verschieben Sie Modelle, um die Reihenfolge der Versuche festzulegen.', 'Wählen Sie Modelle aus, die über aktivierte Provider-Zugänge gefunden wurden.', 'Nach einer 404-Antwort des Upstreams erscheinen hier nicht verfügbare Zugang-Modell-Routen. Andere Zugänge, Provider und Fallback-Modelle bleiben verfügbar.'],
    es: ['Pie del sitio', 'Abrir navegación', 'Navegación principal', 'Consola', 'Cargando versión', 'Cargando', 'Cargando clave API', 'Copiar clave API', 'Mostrar clave API', 'Regenerar clave API', 'Copiar URL base', 'Inicialización', 'Solicitud', 'Actividad de proveedores', 'Cargando desglose de solicitudes', 'Credencial', 'Solicitudes', 'Éxito', 'Tokens', 'Cargando modelos de proveedores', 'Proveedores disponibles', 'Cargando credenciales de proveedores', 'Cargando configuración del sistema', 'Estado de la contraseña', 'Depuración', 'Información', 'Advertencia', 'Error', 'Crítico', 'Respaldo por prioridad', 'Las credenciales se equilibran dentro de cada modelo antes de continuar con el siguiente.', 'Orden de respaldo', 'Mueve los modelos para definir cuál se intenta primero.', 'Selecciona modelos detectados en credenciales de proveedores habilitadas.', 'Las rutas de credencial y modelo no disponibles aparecen aquí tras una respuesta 404 del proveedor. Las demás credenciales, proveedores y modelos de respaldo siguen disponibles.'],
    fr: ['Pied de page', 'Ouvrir la navigation', 'Navigation principale', 'Console', 'Chargement de la version', 'Chargement', 'Chargement de la clé API', 'Copier la clé API', 'Afficher la clé API', 'Régénérer la clé API', 'Copier l’URL de base', 'Initialisation', 'Requête', 'Activité des fournisseurs', 'Chargement du détail des requêtes', 'Identifiant', 'Requêtes', 'Réussite', 'Tokens', 'Chargement des modèles fournisseurs', 'Fournisseurs disponibles', 'Chargement des identifiants fournisseurs', 'Chargement de la configuration système', 'État du mot de passe', 'Débogage', 'Informations', 'Avertissement', 'Erreur', 'Critique', 'Basculement prioritaire', 'Les identifiants sont équilibrés au sein de chaque modèle avant de passer au modèle suivant.', 'Ordre de basculement', 'Déplacez les modèles pour définir celui qui sera essayé en premier.', 'Sélectionnez les modèles détectés à partir des identifiants fournisseurs activés.', 'Les routes identifiant-modèle indisponibles apparaissent ici après une réponse 404 du fournisseur. Les autres identifiants, fournisseurs et modèles de secours restent disponibles.'],
    id: ['Footer situs', 'Buka navigasi', 'Navigasi utama', 'Konsol', 'Memuat versi', 'Memuat', 'Memuat kunci API', 'Salin kunci API', 'Tampilkan kunci API', 'Buat ulang kunci API', 'Salin URL dasar', 'Inisialisasi', 'Permintaan', 'Aktivitas penyedia', 'Memuat rincian permintaan', 'Kredensial', 'Permintaan', 'Berhasil', 'Token', 'Memuat model penyedia', 'Penyedia yang tersedia', 'Memuat kredensial penyedia', 'Memuat konfigurasi sistem', 'Status kata sandi', 'Debug', 'Info', 'Peringatan', 'Kesalahan', 'Kritis', 'Failover berdasarkan prioritas', 'Kredensial diseimbangkan dalam setiap model sebelum perutean berlanjut ke model berikutnya.', 'Urutan failover', 'Pindahkan model untuk menentukan model yang dicoba lebih dahulu.', 'Pilih model yang ditemukan dari kredensial penyedia aktif.', 'Rute kredensial-model yang tidak tersedia akan muncul di sini setelah respons 404 dari upstream. Kredensial, penyedia, dan model failover lainnya tetap tersedia.'],
    it: ['Piè di pagina', 'Apri navigazione', 'Navigazione principale', 'Console', 'Caricamento versione', 'Caricamento', 'Caricamento chiave API', 'Copia chiave API', 'Mostra chiave API', 'Rigenera chiave API', 'Copia URL di base', 'Inizializzazione', 'Richiesta', 'Attività dei provider', 'Caricamento dettaglio richieste', 'Credenziale', 'Richieste', 'Successo', 'Token', 'Caricamento modelli provider', 'Provider disponibili', 'Caricamento credenziali provider', 'Caricamento configurazione di sistema', 'Stato password', 'Debug', 'Informazioni', 'Avviso', 'Errore', 'Critico', 'Fallback prioritario', 'Le credenziali vengono bilanciate all’interno di ogni modello prima di passare al modello successivo.', 'Ordine di fallback', 'Sposta i modelli per definire quale tentare per primo.', 'Seleziona i modelli rilevati dalle credenziali provider abilitate.', 'Le route credenziale-modello non disponibili compaiono qui dopo una risposta 404 upstream. Le altre credenziali, i provider e i modelli di fallback restano disponibili.'],
    ja: ['サイトフッター', 'ナビゲーションを開く', 'メインナビゲーション', 'コンソール', 'バージョンを読み込み中', '読み込み中', 'API キーを読み込み中', 'API キーをコピー', 'API キーを表示', 'API キーを再生成', 'ベース URL をコピー', '初期化', 'リクエスト', 'プロバイダーの稼働状況', 'リクエスト明細を読み込み中', '認証情報', 'リクエスト', '成功', 'トークン', 'プロバイダーモデルを読み込み中', '利用可能なプロバイダー', 'プロバイダー認証情報を読み込み中', 'システム設定を読み込み中', 'パスワードの状態', 'デバッグ', '情報', '警告', 'エラー', '重大', '優先順位によるフォールバック', '各モデル内で認証情報を分散した後、次のモデルへルーティングします。', 'フォールバック順序', 'モデルを移動して、先に試す順序を指定します。', '有効なプロバイダー認証情報から検出されたモデルを選択します。', '上流から 404 が返された認証情報とモデルの組み合わせがここに表示されます。ほかの認証情報、プロバイダー、フォールバックモデルは引き続き利用できます。'],
    ko: ['사이트 바닥글', '탐색 열기', '기본 탐색', '콘솔', '버전 불러오는 중', '불러오는 중', 'API 키 불러오는 중', 'API 키 복사', 'API 키 표시', 'API 키 다시 생성', '기본 URL 복사', '초기화', '요청', '공급자 활동', '요청 내역 불러오는 중', '자격 증명', '요청', '성공', '토큰', '공급자 모델 불러오는 중', '사용 가능한 공급자', '공급자 자격 증명 불러오는 중', '시스템 설정 불러오는 중', '비밀번호 상태', '디버그', '정보', '경고', '오류', '심각', '우선순위 장애 조치', '각 모델 안에서 자격 증명을 균형 있게 사용한 뒤 다음 모델로 라우팅합니다.', '장애 조치 순서', '먼저 시도할 모델의 순서를 정하도록 모델을 이동하세요.', '활성화된 공급자 자격 증명에서 검색된 모델을 선택하세요.', '업스트림이 404를 반환한 자격 증명-모델 경로가 여기에 표시됩니다. 다른 자격 증명, 공급자, 장애 조치 모델은 계속 사용할 수 있습니다.'],
    pt: ['Rodapé do site', 'Abrir navegação', 'Navegação principal', 'Console', 'Carregando versão', 'Carregando', 'Carregando chave de API', 'Copiar chave de API', 'Mostrar chave de API', 'Gerar nova chave de API', 'Copiar URL base', 'Inicialização', 'Solicitação', 'Atividade dos provedores', 'Carregando detalhes das solicitações', 'Credencial', 'Solicitações', 'Sucesso', 'Tokens', 'Carregando modelos dos provedores', 'Provedores disponíveis', 'Carregando credenciais dos provedores', 'Carregando configuração do sistema', 'Status da senha', 'Depuração', 'Informações', 'Aviso', 'Erro', 'Crítico', 'Fallback por prioridade', 'As credenciais são balanceadas dentro de cada modelo antes de o roteamento continuar para o próximo.', 'Ordem de fallback', 'Mova os modelos para definir qual será tentado primeiro.', 'Selecione modelos descobertos nas credenciais de provedores habilitadas.', 'As rotas indisponíveis entre credencial e modelo aparecem aqui após uma resposta 404 do provedor. As demais credenciais, provedores e modelos de fallback continuam disponíveis.'],
    ru: ['Нижний колонтитул сайта', 'Открыть навигацию', 'Основная навигация', 'Консоль', 'Загрузка версии', 'Загрузка', 'Загрузка ключа API', 'Копировать ключ API', 'Показать ключ API', 'Создать новый ключ API', 'Копировать базовый URL', 'Инициализация', 'Запрос', 'Активность провайдеров', 'Загрузка статистики запросов', 'Учётные данные', 'Запросы', 'Успешно', 'Токены', 'Загрузка моделей провайдеров', 'Доступные провайдеры', 'Загрузка учётных данных провайдеров', 'Загрузка конфигурации системы', 'Состояние пароля', 'Отладка', 'Информация', 'Предупреждение', 'Ошибка', 'Критическая ошибка', 'Резервирование по приоритету', 'Сначала нагрузка распределяется между учётными данными каждой модели, затем маршрутизация переходит к следующей модели.', 'Порядок резервирования', 'Перемещайте модели, чтобы задать порядок их использования.', 'Выберите модели, обнаруженные через включённые учётные данные провайдеров.', 'Недоступные маршруты между учётными данными и моделями появляются здесь после ответа 404 от провайдера. Остальные учётные данные, провайдеры и резервные модели остаются доступными.'],
    th: ['ส่วนท้ายเว็บไซต์', 'เปิดเมนูนำทาง', 'เมนูนำทางหลัก', 'คอนโซล', 'กำลังโหลดเวอร์ชัน', 'กำลังโหลด', 'กำลังโหลดคีย์ API', 'คัดลอกคีย์ API', 'แสดงคีย์ API', 'สร้างคีย์ API ใหม่', 'คัดลอก URL หลัก', 'เริ่มต้นใช้งาน', 'คำขอ', 'กิจกรรมของผู้ให้บริการ', 'กำลังโหลดรายละเอียดคำขอ', 'ข้อมูลรับรอง', 'คำขอ', 'สำเร็จ', 'โทเค็น', 'กำลังโหลดโมเดลของผู้ให้บริการ', 'ผู้ให้บริการที่ใช้ได้', 'กำลังโหลดข้อมูลรับรองของผู้ให้บริการ', 'กำลังโหลดการตั้งค่าระบบ', 'สถานะรหัสผ่าน', 'ดีบัก', 'ข้อมูล', 'คำเตือน', 'ข้อผิดพลาด', 'ร้ายแรง', 'ใช้เส้นทางสำรองตามลำดับความสำคัญ', 'ระบบจะกระจายการใช้งานข้อมูลรับรองภายในแต่ละโมเดล ก่อนเปลี่ยนไปใช้โมเดลถัดไป', 'ลำดับเส้นทางสำรอง', 'ย้ายโมเดลเพื่อกำหนดลำดับที่จะลองใช้', 'เลือกโมเดลที่ค้นพบจากข้อมูลรับรองของผู้ให้บริการที่เปิดใช้งาน', 'เส้นทางข้อมูลรับรองกับโมเดลที่ใช้ไม่ได้จะแสดงที่นี่หลังได้รับสถานะ 404 จากต้นทาง ส่วนข้อมูลรับรอง ผู้ให้บริการ และโมเดลสำรองอื่นยังคงใช้งานได้'],
    tr: ['Site altbilgisi', 'Gezinmeyi aç', 'Ana gezinme', 'Konsol', 'Sürüm yükleniyor', 'Yükleniyor', 'API anahtarı yükleniyor', 'API anahtarını kopyala', 'API anahtarını göster', 'API anahtarını yeniden oluştur', 'Temel URL’yi kopyala', 'Başlatma', 'İstek', 'Sağlayıcı etkinliği', 'İstek dökümü yükleniyor', 'Kimlik bilgisi', 'İstekler', 'Başarı', 'Tokenlar', 'Sağlayıcı modelleri yükleniyor', 'Kullanılabilir sağlayıcılar', 'Sağlayıcı kimlik bilgileri yükleniyor', 'Sistem yapılandırması yükleniyor', 'Parola durumu', 'Hata ayıklama', 'Bilgi', 'Uyarı', 'Hata', 'Kritik', 'Öncelikli yedekleme', 'Yönlendirme sonraki modele geçmeden önce her model içindeki kimlik bilgileri dengelenir.', 'Yedekleme sırası', 'Önce denenecek modeli belirlemek için modelleri taşıyın.', 'Etkin sağlayıcı kimlik bilgilerinden keşfedilen modelleri seçin.', 'Üst hizmetten 404 yanıtı alan kimlik bilgisi-model yolları burada görünür. Diğer kimlik bilgileri, sağlayıcılar ve yedek modeller kullanılabilir kalır.'],
    vi: ['Chân trang', 'Mở thanh điều hướng', 'Thanh điều hướng chính', 'Bảng điều khiển', 'Đang tải phiên bản', 'Đang tải', 'Đang tải khóa API', 'Sao chép khóa API', 'Hiện khóa API', 'Tạo lại khóa API', 'Sao chép URL cơ sở', 'Khởi tạo', 'Yêu cầu', 'Hoạt động của nhà cung cấp', 'Đang tải chi tiết yêu cầu', 'Thông tin xác thực', 'Yêu cầu', 'Thành công', 'Token', 'Đang tải mô hình của nhà cung cấp', 'Nhà cung cấp khả dụng', 'Đang tải thông tin xác thực của nhà cung cấp', 'Đang tải cấu hình hệ thống', 'Trạng thái mật khẩu', 'Gỡ lỗi', 'Thông tin', 'Cảnh báo', 'Lỗi', 'Nghiêm trọng', 'Dự phòng theo thứ tự ưu tiên', 'Thông tin xác thực được cân bằng trong từng mô hình trước khi hệ thống chuyển sang mô hình tiếp theo.', 'Thứ tự dự phòng', 'Di chuyển mô hình để xác định mô hình được thử trước.', 'Chọn các mô hình được phát hiện từ thông tin xác thực đang bật của nhà cung cấp.', 'Các tuyến thông tin xác thực–mô hình không khả dụng sẽ xuất hiện tại đây sau phản hồi 404 từ thượng nguồn. Những thông tin xác thực, nhà cung cấp và mô hình dự phòng khác vẫn tiếp tục hoạt động.']
};

for (const [locale, values] of Object.entries(CONSOLE_CHROME_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(CONSOLE_CHROME_KEYS.map((key, index) => [key, values[index]])));
}

const RUNTIME_UI_KEYS = [
    'document_title', 'runtime.validating', 'runtime.validate_add', 'runtime.generating',
    'runtime.saving', 'runtime.connecting', 'runtime.checking', 'runtime.importing',
    'runtime.get_provider_auth', 'runtime.save_credential', 'runtime.authorization_unavailable',
    'runtime.code_unavailable', 'runtime.verification_unavailable', 'runtime.credential_added_title',
    'runtime.credential_updated_title', 'runtime.models_available', 'runtime.credential_saved',
    'runtime.credentials_imported', 'models.unavailable', 'models.ready', 'models.route_count',
    'models.no_unavailable_routes', 'models.occurrence_count', 'models.last_seen',
    'models.credential_name', 'remove', 'models.select_one', 'models.no_matches',
    'models.none_available', 'pagination.page_of', 'upload.more_results', 'import_zip'
];

const RUNTIME_UI_VALUES = {
    en: [
        'Omni Gateway Console', 'Validating...', 'Validate and add', 'Generating...', 'Saving...', 'Connecting...', 'Checking...', 'Importing...',
        'Get provider authentication link', 'Save credential', 'Authorization unavailable', 'Code unavailable', 'Verification page unavailable',
        'Credential added to pool', 'Credential updated', '{count} models available.', 'Credential saved for {account}.', '{count} credentials imported.',
        'Unavailable', 'Ready', '{count} routes', 'No unavailable model routes are recorded.', '{count} occurrences', 'Last seen {time}',
        'Credential {name}', 'Remove', 'Select at least one provider model to activate omway.', 'No models match your search.',
        'No models are available from enabled credentials.', 'Page {page} of {total}', '{count} additional results are not shown.', 'Import ZIP'
    ],
    'zh-CN': [
        'Omni Gateway 控制台', '正在验证...', '验证并添加', '正在生成...', '正在保存...', '正在连接...', '正在检查...', '正在导入...',
        '获取提供商授权链接', '保存凭据', '授权信息不可用', '授权码不可用', '验证页面不可用',
        '凭据已添加到凭据池', '凭据已更新', '可用模型：{count} 个。', '已保存 {account} 的凭据。', '已导入 {count} 份凭据。',
        '不可用', '可用', '路由：{count} 条', '尚未记录不可用的模型路由。', '发生次数：{count}', '最近出现于 {time}',
        '凭据 {name}', '移除', '请至少选择一个提供商模型以启用 omway。', '没有符合搜索条件的模型。',
        '已启用的凭据当前未提供任何模型。', '第 {page} 页，共 {total} 页', '另有 {count} 条结果未显示。', '导入 ZIP'
    ],
    'zh-TW': [
        'Omni Gateway 主控台', '正在驗證...', '驗證並新增', '正在產生...', '正在儲存...', '正在連線...', '正在檢查...', '正在匯入...',
        '取得供應商授權連結', '儲存憑證', '授權資訊無法使用', '授權碼無法使用', '驗證頁面無法使用',
        '憑證已新增至憑證集區', '憑證已更新', '可用模型：{count} 個。', '已儲存 {account} 的憑證。', '已匯入 {count} 份憑證。',
        '無法使用', '可用', '路由：{count} 條', '目前沒有無法使用的模型路由記錄。', '發生次數：{count}', '最近出現於 {time}',
        '憑證 {name}', '移除', '請至少選取一個供應商模型以啟用 omway。', '沒有符合搜尋條件的模型。',
        '已啟用的憑證目前未提供任何模型。', '第 {page} 頁，共 {total} 頁', '另有 {count} 筆結果未顯示。', '匯入 ZIP'
    ],
    de: [
        'Omni Gateway Konsole', 'Wird geprüft...', 'Prüfen und hinzufügen', 'Wird erstellt...', 'Wird gespeichert...', 'Verbindung wird hergestellt...', 'Wird geprüft...', 'Wird importiert...',
        'Provider-Autorisierungslink abrufen', 'Zugangsdaten speichern', 'Autorisierung nicht verfügbar', 'Code nicht verfügbar', 'Bestätigungsseite nicht verfügbar',
        'Zugangsdaten zum Pool hinzugefügt', 'Zugangsdaten aktualisiert', '{count} Modelle verfügbar.', 'Zugangsdaten für {account} gespeichert.', '{count} Zugangsdaten importiert.',
        'Nicht verfügbar', 'Bereit', '{count} Routen', 'Es sind keine nicht verfügbaren Modellrouten erfasst.', '{count} Vorkommnisse', 'Zuletzt gesehen: {time}',
        'Zugang {name}', 'Entfernen', 'Wählen Sie mindestens ein Provider-Modell aus, um omway zu aktivieren.', 'Keine Modelle entsprechen Ihrer Suche.',
        'Über aktivierte Zugänge sind keine Modelle verfügbar.', 'Seite {page} von {total}', '{count} weitere Ergebnisse werden nicht angezeigt.', 'ZIP importieren'
    ],
    es: [
        'Consola de Omni Gateway', 'Validando...', 'Validar y añadir', 'Generando...', 'Guardando...', 'Conectando...', 'Comprobando...', 'Importando...',
        'Obtener enlace de autorización del proveedor', 'Guardar credencial', 'Autorización no disponible', 'Código no disponible', 'Página de verificación no disponible',
        'Credencial añadida al grupo', 'Credencial actualizada', '{count} modelos disponibles.', 'Credencial guardada para {account}.', '{count} credenciales importadas.',
        'No disponible', 'Listo', '{count} rutas', 'No hay rutas de modelo no disponibles registradas.', '{count} incidencias', 'Última detección: {time}',
        'Credencial {name}', 'Quitar', 'Selecciona al menos un modelo de proveedor para activar omway.', 'Ningún modelo coincide con la búsqueda.',
        'Las credenciales habilitadas no ofrecen ningún modelo.', 'Página {page} de {total}', 'No se muestran {count} resultados adicionales.', 'Importar ZIP'
    ],
    fr: [
        'Console Omni Gateway', 'Validation en cours...', 'Valider et ajouter', 'Génération en cours...', 'Enregistrement...', 'Connexion...', 'Vérification...', 'Importation...',
        'Obtenir le lien d’autorisation du fournisseur', 'Enregistrer l’identifiant', 'Autorisation indisponible', 'Code indisponible', 'Page de vérification indisponible',
        'Identifiant ajouté au pool', 'Identifiant mis à jour', '{count} modèles disponibles.', 'Identifiant enregistré pour {account}.', '{count} identifiants importés.',
        'Indisponible', 'Prêt', '{count} routes', 'Aucune route de modèle indisponible n’est enregistrée.', '{count} occurrences', 'Dernière détection : {time}',
        'Identifiant {name}', 'Retirer', 'Sélectionnez au moins un modèle fournisseur pour activer omway.', 'Aucun modèle ne correspond à votre recherche.',
        'Aucun modèle n’est disponible via les identifiants activés.', 'Page {page} sur {total}', '{count} résultats supplémentaires ne sont pas affichés.', 'Importer un ZIP'
    ],
    id: [
        'Konsol Omni Gateway', 'Memvalidasi...', 'Validasi dan tambahkan', 'Membuat...', 'Menyimpan...', 'Menghubungkan...', 'Memeriksa...', 'Mengimpor...',
        'Dapatkan tautan otorisasi penyedia', 'Simpan kredensial', 'Otorisasi tidak tersedia', 'Kode tidak tersedia', 'Halaman verifikasi tidak tersedia',
        'Kredensial ditambahkan ke pool', 'Kredensial diperbarui', '{count} model tersedia.', 'Kredensial untuk {account} telah disimpan.', '{count} kredensial diimpor.',
        'Tidak tersedia', 'Siap', '{count} rute', 'Belum ada rute model yang tidak tersedia.', '{count} kejadian', 'Terakhir terlihat {time}',
        'Kredensial {name}', 'Hapus', 'Pilih setidaknya satu model penyedia untuk mengaktifkan omway.', 'Tidak ada model yang cocok dengan pencarian.',
        'Tidak ada model yang tersedia dari kredensial aktif.', 'Halaman {page} dari {total}', '{count} hasil tambahan tidak ditampilkan.', 'Impor ZIP'
    ],
    it: [
        'Console Omni Gateway', 'Convalida in corso...', 'Convalida e aggiungi', 'Generazione...', 'Salvataggio...', 'Connessione...', 'Verifica...', 'Importazione...',
        'Ottieni link di autorizzazione del provider', 'Salva credenziale', 'Autorizzazione non disponibile', 'Codice non disponibile', 'Pagina di verifica non disponibile',
        'Credenziale aggiunta al pool', 'Credenziale aggiornata', '{count} modelli disponibili.', 'Credenziale salvata per {account}.', '{count} credenziali importate.',
        'Non disponibile', 'Pronto', '{count} route', 'Non sono registrate route di modello non disponibili.', '{count} occorrenze', 'Ultimo rilevamento: {time}',
        'Credenziale {name}', 'Rimuovi', 'Seleziona almeno un modello provider per attivare omway.', 'Nessun modello corrisponde alla ricerca.',
        'Nessun modello è disponibile dalle credenziali abilitate.', 'Pagina {page} di {total}', '{count} risultati aggiuntivi non sono mostrati.', 'Importa ZIP'
    ],
    ja: [
        'Omni Gateway コンソール', '検証中...', '検証して追加', '生成中...', '保存中...', '接続中...', '確認中...', 'インポート中...',
        'プロバイダー認証リンクを取得', '認証情報を保存', '認証を利用できません', 'コードを利用できません', '確認ページを利用できません',
        '認証情報をプールに追加しました', '認証情報を更新しました', '利用可能なモデル：{count} 件。', '{account} の認証情報を保存しました。', '認証情報を {count} 件インポートしました。',
        '利用不可', '準備完了', 'ルート：{count} 件', '利用不可として記録されたモデルルートはありません。', '発生回数：{count}', '最終検出：{time}',
        '認証情報 {name}', '削除', 'omway を有効にするには、プロバイダーモデルを 1 つ以上選択してください。', '検索条件に一致するモデルはありません。',
        '有効な認証情報から利用できるモデルがありません。', '{page} / {total} ページ', 'ほか {count} 件の結果は表示されていません。', 'ZIP をインポート'
    ],
    ko: [
        'Omni Gateway 콘솔', '검증 중...', '검증 후 추가', '생성 중...', '저장 중...', '연결 중...', '확인 중...', '가져오는 중...',
        '공급자 인증 링크 받기', '자격 증명 저장', '인증을 사용할 수 없음', '코드를 사용할 수 없음', '확인 페이지를 사용할 수 없음',
        '자격 증명을 풀에 추가했습니다', '자격 증명을 업데이트했습니다', '사용 가능한 모델: {count}개.', '{account}의 자격 증명을 저장했습니다.', '자격 증명 {count}개를 가져왔습니다.',
        '사용할 수 없음', '준비됨', '경로 {count}개', '사용할 수 없는 모델 경로 기록이 없습니다.', '발생 {count}회', '마지막 감지: {time}',
        '자격 증명 {name}', '제거', 'omway를 활성화하려면 공급자 모델을 하나 이상 선택하세요.', '검색 조건과 일치하는 모델이 없습니다.',
        '활성화된 자격 증명에서 사용할 수 있는 모델이 없습니다.', '{total}페이지 중 {page}페이지', '추가 결과 {count}개는 표시되지 않습니다.', 'ZIP 가져오기'
    ],
    pt: [
        'Console do Omni Gateway', 'Validando...', 'Validar e adicionar', 'Gerando...', 'Salvando...', 'Conectando...', 'Verificando...', 'Importando...',
        'Obter link de autorização do provedor', 'Salvar credencial', 'Autorização indisponível', 'Código indisponível', 'Página de verificação indisponível',
        'Credencial adicionada ao pool', 'Credencial atualizada', '{count} modelos disponíveis.', 'Credencial de {account} salva.', '{count} credenciais importadas.',
        'Indisponível', 'Pronto', '{count} rotas', 'Nenhuma rota de modelo indisponível foi registrada.', '{count} ocorrências', 'Visto pela última vez em {time}',
        'Credencial {name}', 'Remover', 'Selecione pelo menos um modelo de provedor para ativar o omway.', 'Nenhum modelo corresponde à pesquisa.',
        'Nenhum modelo está disponível nas credenciais habilitadas.', 'Página {page} de {total}', '{count} resultados adicionais não são exibidos.', 'Importar ZIP'
    ],
    ru: [
        'Консоль Omni Gateway', 'Проверка...', 'Проверить и добавить', 'Создание...', 'Сохранение...', 'Подключение...', 'Проверка...', 'Импорт...',
        'Получить ссылку авторизации провайдера', 'Сохранить учётные данные', 'Авторизация недоступна', 'Код недоступен', 'Страница подтверждения недоступна',
        'Учётные данные добавлены в пул', 'Учётные данные обновлены', 'Доступно моделей: {count}.', 'Учётные данные для {account} сохранены.', 'Импортировано учётных данных: {count}.',
        'Недоступно', 'Готово', 'Маршрутов: {count}', 'Недоступные маршруты моделей не зарегистрированы.', 'Событий: {count}', 'Последнее событие: {time}',
        'Учётные данные {name}', 'Удалить', 'Выберите хотя бы одну модель провайдера, чтобы активировать omway.', 'Поиск не дал результатов.',
        'Во включённых учётных данных нет доступных моделей.', 'Страница {page} из {total}', 'Не показано дополнительных результатов: {count}.', 'Импортировать ZIP'
    ],
    th: [
        'คอนโซล Omni Gateway', 'กำลังตรวจสอบ...', 'ตรวจสอบและเพิ่ม', 'กำลังสร้าง...', 'กำลังบันทึก...', 'กำลังเชื่อมต่อ...', 'กำลังตรวจสอบ...', 'กำลังนำเข้า...',
        'รับลิงก์อนุญาตจากผู้ให้บริการ', 'บันทึกข้อมูลรับรอง', 'ไม่มีข้อมูลการอนุญาต', 'ไม่มีรหัส', 'ไม่มีหน้าตรวจสอบ',
        'เพิ่มข้อมูลรับรองลงในพูลแล้ว', 'อัปเดตข้อมูลรับรองแล้ว', 'มีโมเดลให้ใช้ {count} รายการ', 'บันทึกข้อมูลรับรองของ {account} แล้ว', 'นำเข้าข้อมูลรับรองแล้ว {count} รายการ',
        'ใช้ไม่ได้', 'พร้อมใช้งาน', 'เส้นทาง {count} รายการ', 'ยังไม่มีบันทึกเส้นทางโมเดลที่ใช้ไม่ได้', 'เกิดขึ้น {count} ครั้ง', 'พบล่าสุดเมื่อ {time}',
        'ข้อมูลรับรอง {name}', 'นำออก', 'เลือกโมเดลของผู้ให้บริการอย่างน้อยหนึ่งรายการเพื่อเปิดใช้ omway', 'ไม่พบโมเดลที่ตรงกับการค้นหา',
        'ไม่มีโมเดลจากข้อมูลรับรองที่เปิดใช้งาน', 'หน้า {page} จาก {total}', 'ไม่ได้แสดงผลลัพธ์เพิ่มเติม {count} รายการ', 'นำเข้า ZIP'
    ],
    tr: [
        'Omni Gateway Konsolu', 'Doğrulanıyor...', 'Doğrula ve ekle', 'Oluşturuluyor...', 'Kaydediliyor...', 'Bağlanıyor...', 'Kontrol ediliyor...', 'İçe aktarılıyor...',
        'Sağlayıcı yetkilendirme bağlantısını al', 'Kimlik bilgisini kaydet', 'Yetkilendirme kullanılamıyor', 'Kod kullanılamıyor', 'Doğrulama sayfası kullanılamıyor',
        'Kimlik bilgisi havuza eklendi', 'Kimlik bilgisi güncellendi', '{count} model kullanılabilir.', '{account} için kimlik bilgisi kaydedildi.', '{count} kimlik bilgisi içe aktarıldı.',
        'Kullanılamıyor', 'Hazır', '{count} rota', 'Kullanılamayan model rotası kaydedilmemiş.', '{count} kez oluştu', 'Son görülme: {time}',
        'Kimlik bilgisi {name}', 'Kaldır', 'omway modelini etkinleştirmek için en az bir sağlayıcı modeli seçin.', 'Aramanızla eşleşen model yok.',
        'Etkin kimlik bilgilerinden kullanılabilir model bulunamadı.', 'Sayfa {page}/{total}', '{count} ek sonuç gösterilmiyor.', 'ZIP içe aktar'
    ],
    vi: [
        'Bảng điều khiển Omni Gateway', 'Đang xác thực...', 'Xác thực và thêm', 'Đang tạo...', 'Đang lưu...', 'Đang kết nối...', 'Đang kiểm tra...', 'Đang nhập...',
        'Lấy liên kết cấp quyền của nhà cung cấp', 'Lưu thông tin xác thực', 'Không có thông tin cấp quyền', 'Không có mã cấp quyền', 'Không có trang xác minh',
        'Đã thêm thông tin xác thực vào kho', 'Đã cập nhật thông tin xác thực', 'Có {count} mô hình khả dụng.', 'Đã lưu thông tin xác thực cho {account}.', 'Đã nhập {count} thông tin xác thực.',
        'Không khả dụng', 'Sẵn sàng', '{count} tuyến', 'Chưa ghi nhận tuyến mô hình nào không khả dụng.', 'Xuất hiện {count} lần', 'Ghi nhận gần nhất lúc {time}',
        'Thông tin xác thực {name}', 'Gỡ bỏ', 'Chọn ít nhất một mô hình của nhà cung cấp để kích hoạt omway.', 'Không có mô hình nào khớp với nội dung tìm kiếm.',
        'Không có mô hình nào từ các thông tin xác thực đang bật.', 'Trang {page}/{total}', 'Không hiển thị thêm {count} kết quả.', 'Nhập ZIP'
    ]
};

for (const [locale, values] of Object.entries(RUNTIME_UI_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(RUNTIME_UI_KEYS.map((key, index) => [key, values[index]])));
}

const PROVIDER_ACTION_KEYS = [
    'provider.settings_load_failed', 'provider.settings_saved', 'provider.settings_save_failed',
    'provider.settings_reset', 'provider.settings_reset_failed', 'provider.api_key_required',
    'provider.api_key_add_failed', 'provider.auth_ready', 'provider.auth_start_failed',
    'provider.auth_code_required', 'provider.auth_session_required', 'provider.credential_save_failed',
    'provider.endpoint_required', 'provider.connection_add_failed', 'provider.authorization_pending',
    'provider.device_code_ready'
];

const PROVIDER_ACTION_VALUES = {
    en: ['Could not load {provider} settings: {error}', '{provider} settings saved.', 'Could not save {provider} settings: {error}', '{provider} settings restored to defaults.', 'Could not restore {provider} settings: {error}', 'Enter a {provider} API key.', 'Could not add the {provider} API key: {error}', '{provider} authorization is ready. Complete sign-in to continue.', 'Could not start {provider} authorization: {error}', 'Enter the authorization code provided by {provider}.', 'Generate a new {provider} authorization request before saving the credential.', 'Could not save the {provider} credential: {error}', 'Enter a {provider} endpoint.', 'Could not add the {provider} connection: {error}', '{provider} authorization is still pending.', '{provider} device code generated.'],
    'zh-CN': ['无法加载 {provider} 设置：{error}', '{provider} 设置已保存。', '无法保存 {provider} 设置：{error}', '{provider} 设置已恢复默认值。', '无法恢复 {provider} 设置：{error}', '请输入 {provider} API 密钥。', '无法添加 {provider} API 密钥：{error}', '{provider} 授权已就绪，请完成登录以继续。', '无法启动 {provider} 授权：{error}', '请输入 {provider} 提供的授权码。', '保存凭据前，请先重新发起 {provider} 授权。', '无法保存 {provider} 凭据：{error}', '请输入 {provider} endpoint。', '无法添加 {provider} 连接：{error}', '{provider} 授权仍在等待完成。', '已生成 {provider} 设备代码。'],
    'zh-TW': ['無法載入 {provider} 設定：{error}', '{provider} 設定已儲存。', '無法儲存 {provider} 設定：{error}', '{provider} 設定已恢復預設值。', '無法恢復 {provider} 設定：{error}', '請輸入 {provider} API 金鑰。', '無法新增 {provider} API 金鑰：{error}', '{provider} 授權已就緒，請完成登入以繼續。', '無法開始 {provider} 授權：{error}', '請輸入 {provider} 提供的授權碼。', '儲存憑證前，請先重新發起 {provider} 授權。', '無法儲存 {provider} 憑證：{error}', '請輸入 {provider} endpoint。', '無法新增 {provider} 連線：{error}', '{provider} 授權仍在等待完成。', '已產生 {provider} 裝置代碼。'],
    de: ['Die {provider}-Einstellungen konnten nicht geladen werden: {error}', '{provider}-Einstellungen gespeichert.', 'Die {provider}-Einstellungen konnten nicht gespeichert werden: {error}', '{provider}-Einstellungen auf Standardwerte zurückgesetzt.', 'Die {provider}-Einstellungen konnten nicht zurückgesetzt werden: {error}', 'Geben Sie einen API-Schlüssel für {provider} ein.', 'Der API-Schlüssel für {provider} konnte nicht hinzugefügt werden: {error}', 'Die {provider}-Autorisierung ist bereit. Schließen Sie die Anmeldung ab.', 'Die {provider}-Autorisierung konnte nicht gestartet werden: {error}', 'Geben Sie den von {provider} bereitgestellten Autorisierungscode ein.', 'Starten Sie vor dem Speichern einen neuen {provider}-Autorisierungsvorgang.', 'Die {provider}-Zugangsdaten konnten nicht gespeichert werden: {error}', 'Geben Sie einen {provider}-Endpoint ein.', 'Die {provider}-Verbindung konnte nicht hinzugefügt werden: {error}', 'Die {provider}-Autorisierung ist noch nicht abgeschlossen.', '{provider}-Gerätecode erstellt.'],
    es: ['No se pudo cargar la configuración de {provider}: {error}', 'Configuración de {provider} guardada.', 'No se pudo guardar la configuración de {provider}: {error}', 'Se restauró la configuración predeterminada de {provider}.', 'No se pudo restaurar la configuración de {provider}: {error}', 'Introduce una clave API de {provider}.', 'No se pudo añadir la clave API de {provider}: {error}', 'La autorización de {provider} está lista. Completa el inicio de sesión para continuar.', 'No se pudo iniciar la autorización de {provider}: {error}', 'Introduce el código de autorización proporcionado por {provider}.', 'Genera una nueva autorización de {provider} antes de guardar la credencial.', 'No se pudo guardar la credencial de {provider}: {error}', 'Introduce un endpoint de {provider}.', 'No se pudo añadir la conexión de {provider}: {error}', 'La autorización de {provider} sigue pendiente.', 'Código de dispositivo de {provider} generado.'],
    fr: ['Impossible de charger les paramètres {provider} : {error}', 'Paramètres {provider} enregistrés.', 'Impossible d’enregistrer les paramètres {provider} : {error}', 'Paramètres {provider} rétablis par défaut.', 'Impossible de rétablir les paramètres {provider} : {error}', 'Saisissez une clé API {provider}.', 'Impossible d’ajouter la clé API {provider} : {error}', 'L’autorisation {provider} est prête. Terminez la connexion pour continuer.', 'Impossible de démarrer l’autorisation {provider} : {error}', 'Saisissez le code d’autorisation fourni par {provider}.', 'Générez une nouvelle autorisation {provider} avant d’enregistrer l’identifiant.', 'Impossible d’enregistrer l’identifiant {provider} : {error}', 'Saisissez un endpoint {provider}.', 'Impossible d’ajouter la connexion {provider} : {error}', 'L’autorisation {provider} est toujours en attente.', 'Code d’appareil {provider} généré.'],
    id: ['Tidak dapat memuat pengaturan {provider}: {error}', 'Pengaturan {provider} disimpan.', 'Tidak dapat menyimpan pengaturan {provider}: {error}', 'Pengaturan {provider} dikembalikan ke nilai bawaan.', 'Tidak dapat memulihkan pengaturan {provider}: {error}', 'Masukkan kunci API {provider}.', 'Tidak dapat menambahkan kunci API {provider}: {error}', 'Otorisasi {provider} siap. Selesaikan proses masuk untuk melanjutkan.', 'Tidak dapat memulai otorisasi {provider}: {error}', 'Masukkan kode otorisasi dari {provider}.', 'Buat permintaan otorisasi {provider} baru sebelum menyimpan kredensial.', 'Tidak dapat menyimpan kredensial {provider}: {error}', 'Masukkan endpoint {provider}.', 'Tidak dapat menambahkan koneksi {provider}: {error}', 'Otorisasi {provider} masih tertunda.', 'Kode perangkat {provider} dibuat.'],
    it: ['Impossibile caricare le impostazioni di {provider}: {error}', 'Impostazioni di {provider} salvate.', 'Impossibile salvare le impostazioni di {provider}: {error}', 'Impostazioni predefinite di {provider} ripristinate.', 'Impossibile ripristinare le impostazioni di {provider}: {error}', 'Inserisci una chiave API di {provider}.', 'Impossibile aggiungere la chiave API di {provider}: {error}', 'L’autorizzazione di {provider} è pronta. Completa l’accesso per continuare.', 'Impossibile avviare l’autorizzazione di {provider}: {error}', 'Inserisci il codice di autorizzazione fornito da {provider}.', 'Genera una nuova autorizzazione di {provider} prima di salvare la credenziale.', 'Impossibile salvare la credenziale di {provider}: {error}', 'Inserisci un endpoint di {provider}.', 'Impossibile aggiungere la connessione di {provider}: {error}', 'L’autorizzazione di {provider} è ancora in sospeso.', 'Codice dispositivo di {provider} generato.'],
    ja: ['{provider} の設定を読み込めませんでした：{error}', '{provider} の設定を保存しました。', '{provider} の設定を保存できませんでした：{error}', '{provider} の設定を初期値に戻しました。', '{provider} の設定を初期値に戻せませんでした：{error}', '{provider} の API キーを入力してください。', '{provider} の API キーを追加できませんでした：{error}', '{provider} の認証準備ができました。ログインを完了してください。', '{provider} の認証を開始できませんでした：{error}', '{provider} が表示した認証コードを入力してください。', '認証情報を保存する前に、{provider} の認証を新しく開始してください。', '{provider} の認証情報を保存できませんでした：{error}', '{provider} の endpoint を入力してください。', '{provider} の接続を追加できませんでした：{error}', '{provider} の認証はまだ完了していません。', '{provider} のデバイスコードを生成しました。'],
    ko: ['{provider} 설정을 불러오지 못했습니다: {error}', '{provider} 설정을 저장했습니다.', '{provider} 설정을 저장하지 못했습니다: {error}', '{provider} 설정을 기본값으로 복원했습니다.', '{provider} 설정을 복원하지 못했습니다: {error}', '{provider} API 키를 입력하세요.', '{provider} API 키를 추가하지 못했습니다: {error}', '{provider} 인증 준비가 완료되었습니다. 로그인을 마쳐 주세요.', '{provider} 인증을 시작하지 못했습니다: {error}', '{provider}에서 제공한 인증 코드를 입력하세요.', '자격 증명을 저장하기 전에 {provider} 인증을 새로 시작하세요.', '{provider} 자격 증명을 저장하지 못했습니다: {error}', '{provider} endpoint를 입력하세요.', '{provider} 연결을 추가하지 못했습니다: {error}', '{provider} 인증이 아직 대기 중입니다.', '{provider} 기기 코드를 생성했습니다.'],
    pt: ['Não foi possível carregar as configurações de {provider}: {error}', 'Configurações de {provider} salvas.', 'Não foi possível salvar as configurações de {provider}: {error}', 'Configurações padrão de {provider} restauradas.', 'Não foi possível restaurar as configurações de {provider}: {error}', 'Informe uma chave de API de {provider}.', 'Não foi possível adicionar a chave de API de {provider}: {error}', 'A autorização de {provider} está pronta. Conclua o login para continuar.', 'Não foi possível iniciar a autorização de {provider}: {error}', 'Informe o código de autorização fornecido por {provider}.', 'Gere uma nova autorização de {provider} antes de salvar a credencial.', 'Não foi possível salvar a credencial de {provider}: {error}', 'Informe um endpoint de {provider}.', 'Não foi possível adicionar a conexão de {provider}: {error}', 'A autorização de {provider} ainda está pendente.', 'Código de dispositivo de {provider} gerado.'],
    ru: ['Не удалось загрузить настройки {provider}: {error}', 'Настройки {provider} сохранены.', 'Не удалось сохранить настройки {provider}: {error}', 'Настройки {provider} восстановлены по умолчанию.', 'Не удалось восстановить настройки {provider}: {error}', 'Введите API-ключ {provider}.', 'Не удалось добавить API-ключ {provider}: {error}', 'Авторизация {provider} готова. Завершите вход, чтобы продолжить.', 'Не удалось начать авторизацию {provider}: {error}', 'Введите код авторизации, предоставленный {provider}.', 'Перед сохранением учётных данных запустите новую авторизацию {provider}.', 'Не удалось сохранить учётные данные {provider}: {error}', 'Введите endpoint {provider}.', 'Не удалось добавить подключение {provider}: {error}', 'Авторизация {provider} ещё не завершена.', 'Код устройства {provider} создан.'],
    th: ['ไม่สามารถโหลดการตั้งค่า {provider}: {error}', 'บันทึกการตั้งค่า {provider} แล้ว', 'ไม่สามารถบันทึกการตั้งค่า {provider}: {error}', 'คืนค่าการตั้งค่าเริ่มต้นของ {provider} แล้ว', 'ไม่สามารถคืนค่าการตั้งค่า {provider}: {error}', 'โปรดป้อนคีย์ API ของ {provider}', 'ไม่สามารถเพิ่มคีย์ API ของ {provider}: {error}', 'การอนุญาต {provider} พร้อมแล้ว โปรดเข้าสู่ระบบให้เสร็จเพื่อดำเนินการต่อ', 'ไม่สามารถเริ่มการอนุญาต {provider}: {error}', 'โปรดป้อนรหัสอนุญาตที่ {provider} แสดง', 'โปรดเริ่มการอนุญาต {provider} ใหม่ก่อนบันทึกข้อมูลรับรอง', 'ไม่สามารถบันทึกข้อมูลรับรอง {provider}: {error}', 'โปรดป้อน endpoint ของ {provider}', 'ไม่สามารถเพิ่มการเชื่อมต่อ {provider}: {error}', 'การอนุญาต {provider} ยังรอดำเนินการอยู่', 'สร้างรหัสอุปกรณ์ {provider} แล้ว'],
    tr: ['{provider} ayarları yüklenemedi: {error}', '{provider} ayarları kaydedildi.', '{provider} ayarları kaydedilemedi: {error}', '{provider} ayarları varsayılanlara döndürüldü.', '{provider} ayarları geri yüklenemedi: {error}', 'Bir {provider} API anahtarı girin.', '{provider} API anahtarı eklenemedi: {error}', '{provider} yetkilendirmesi hazır. Devam etmek için oturum açmayı tamamlayın.', '{provider} yetkilendirmesi başlatılamadı: {error}', '{provider} tarafından verilen yetkilendirme kodunu girin.', 'Kimlik bilgisini kaydetmeden önce yeni bir {provider} yetkilendirme isteği oluşturun.', '{provider} kimlik bilgisi kaydedilemedi: {error}', 'Bir {provider} endpoint’i girin.', '{provider} bağlantısı eklenemedi: {error}', '{provider} yetkilendirmesi hâlâ bekliyor.', '{provider} cihaz kodu oluşturuldu.'],
    vi: ['Không thể tải cài đặt {provider}: {error}', 'Đã lưu cài đặt {provider}.', 'Không thể lưu cài đặt {provider}: {error}', 'Đã khôi phục cài đặt mặc định của {provider}.', 'Không thể khôi phục cài đặt {provider}: {error}', 'Nhập khóa API của {provider}.', 'Không thể thêm khóa API của {provider}: {error}', 'Đã sẵn sàng cấp quyền cho {provider}. Hãy hoàn tất đăng nhập để tiếp tục.', 'Không thể bắt đầu cấp quyền cho {provider}: {error}', 'Nhập mã cấp quyền do {provider} cung cấp.', 'Hãy tạo yêu cầu cấp quyền {provider} mới trước khi lưu thông tin xác thực.', 'Không thể lưu thông tin xác thực {provider}: {error}', 'Nhập endpoint của {provider}.', 'Không thể thêm kết nối {provider}: {error}', 'Quy trình cấp quyền {provider} vẫn đang chờ hoàn tất.', 'Đã tạo mã thiết bị {provider}.']
};

for (const [locale, values] of Object.entries(PROVIDER_ACTION_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(PROVIDER_ACTION_KEYS.map((key, index) => [key, values[index]])));
}

const PROVIDER_DIALOG_KEYS = [
    'runtime.get_authorization_code', 'runtime.check_authorization',
    'provider.reset_confirm', 'provider.reset_title'
];

const PROVIDER_DIALOG_VALUES = {
    en: ['Get authorization code', 'Check authorization', 'Restore the built-in {provider} settings? Environment-managed values will be preserved.', 'Reset {provider} Settings'],
    'zh-CN': ['获取授权码', '检查授权状态', '恢复 {provider} 的内置设置？由运行环境管理的值将保留。', '重置 {provider} 设置'],
    'zh-TW': ['取得授權碼', '檢查授權狀態', '恢復 {provider} 的內建設定？由執行環境管理的值將保留。', '重設 {provider} 設定'],
    de: ['Autorisierungscode abrufen', 'Autorisierung prüfen', 'Integrierte {provider}-Einstellungen wiederherstellen? Von der Laufzeitumgebung verwaltete Werte bleiben erhalten.', '{provider}-Einstellungen zurücksetzen'],
    es: ['Obtener código de autorización', 'Comprobar autorización', '¿Restaurar la configuración integrada de {provider}? Se conservarán los valores administrados por el entorno de ejecución.', 'Restablecer configuración de {provider}'],
    fr: ['Obtenir le code d’autorisation', 'Vérifier l’autorisation', 'Rétablir les paramètres intégrés de {provider} ? Les valeurs gérées par l’environnement d’exécution seront conservées.', 'Réinitialiser les paramètres {provider}'],
    id: ['Dapatkan kode otorisasi', 'Periksa otorisasi', 'Pulihkan pengaturan bawaan {provider}? Nilai yang dikelola lingkungan runtime akan dipertahankan.', 'Reset Pengaturan {provider}'],
    it: ['Ottieni il codice di autorizzazione', 'Verifica autorizzazione', 'Ripristinare le impostazioni integrate di {provider}? I valori gestiti dall’ambiente di esecuzione saranno conservati.', 'Ripristina impostazioni di {provider}'],
    ja: ['認証コードを取得', '認証状態を確認', '{provider} の組み込み設定を復元しますか？実行環境が管理する値は保持されます。', '{provider} の設定をリセット'],
    ko: ['인증 코드 받기', '인증 확인', '{provider} 기본 설정을 복원할까요? 실행 환경에서 관리하는 값은 유지됩니다.', '{provider} 설정 재설정'],
    pt: ['Obter código de autorização', 'Verificar autorização', 'Restaurar as configurações integradas de {provider}? Os valores gerenciados pelo ambiente de execução serão preservados.', 'Redefinir configurações de {provider}'],
    ru: ['Получить код авторизации', 'Проверить авторизацию', 'Восстановить встроенные настройки {provider}? Значения, управляемые средой выполнения, будут сохранены.', 'Сбросить настройки {provider}'],
    th: ['รับรหัสอนุญาต', 'ตรวจสอบการอนุญาต', 'คืนค่าการตั้งค่าเริ่มต้นของ {provider} หรือไม่ ค่าที่จัดการโดยสภาพแวดล้อมรันไทม์จะยังคงอยู่', 'รีเซ็ตการตั้งค่า {provider}'],
    tr: ['Yetkilendirme kodunu al', 'Yetkilendirmeyi kontrol et', 'Yerleşik {provider} ayarları geri yüklensin mi? Çalışma ortamının yönettiği değerler korunur.', '{provider} Ayarlarını Sıfırla'],
    vi: ['Lấy mã cấp quyền', 'Kiểm tra cấp quyền', 'Khôi phục cài đặt tích hợp sẵn của {provider}? Các giá trị do môi trường chạy quản lý sẽ được giữ nguyên.', 'Đặt lại cài đặt {provider}']
};

for (const [locale, values] of Object.entries(PROVIDER_DIALOG_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(PROVIDER_DIALOG_KEYS.map((key, index) => [key, values[index]])));
}

const OPERATION_COPY_KEYS = [
    'runtime.loading_models', 'models.restore_credential_route', 'models.restore_provider_route',
    'models.route_restored', 'models.route_restore_failed', 'models.clear_confirm',
    'models.clear_title', 'models.blacklist_cleared', 'models.blacklist_clear_failed',
    'models.catalog_refreshed', 'models.catalog_load_failed', 'models.virtual_updated',
    'models.virtual_save_failed', 'models.move_up', 'models.move_down', 'models.remove_selected',
    'credentials.verified', 'credentials.test_failed', 'settings.managed_environment',
    'settings.not_configured', 'settings.current_password_required', 'settings.new_password_required',
    'settings.password_confirmation_mismatch', 'settings.password_update_failed',
    'settings.restart_to_apply', 'settings.reset_confirm', 'settings.reset_failed',
    'import.pool_select_zip', 'import.pool_too_large', 'import.pool_inspecting',
    'import.pool_complete', 'import.pool_failed', 'provider.import_complete',
    'provider.import_failed', 'api_key.regenerate_failed', 'quota.reset_unavailable',
    'quota.resets_at', 'quota.next_reset', 'quota.reset_at'
];

const OPERATION_COPY_VALUES = {
    en: [
        'Loading available models...', 'Restore this credential-model route', 'Restore this provider-model route',
        'Model route restored.', 'Could not restore the model route: {error}', 'Restore every model route excluded after an upstream 404 response?',
        'Clear Unavailable Routes', 'Unavailable model routes cleared.', 'Could not clear unavailable model routes: {error}',
        'Provider model catalog refreshed.', 'Could not load the provider model catalog: {error}', 'Virtual model updated.',
        'Could not save omway: {error}', 'Move model up', 'Move model down', 'Remove model',
        'Credential verified.', 'Model test failed: {error}', 'Managed by environment',
        'Not configured', 'Enter the current console password.', 'Enter a new console password.',
        'The console password confirmation does not match.', 'Could not update the console password: {error}',
        'Configuration saved. Restart the application to apply listener or storage changes.', 'Reset system configuration to defaults? Access passwords and the generated API key will be preserved.', 'Could not reset system configuration: {error}',
        'Select a ZIP archive exported from the credential pool.', 'The pool archive exceeds the 10 MB import limit.', 'Inspecting the pool archive and validating provider credentials...',
        'Pool archive imported.', 'Could not import the pool archive: {error}', '{provider} import completed.',
        '{provider} import failed: {error}', 'Could not regenerate the API key.', 'Reset time unavailable',
        'Resets {time}', 'Next reset', 'Reset {time}'
    ],
    'zh-CN': [
        '正在加载可用模型...', '恢复此凭据与模型的路由', '恢复此提供商与模型的路由', '模型路由已恢复。', '无法恢复模型路由：{error}', '恢复因上游返回 404 而被排除的所有模型路由？', '清除不可用路由', '已清除不可用的模型路由。', '无法清除不可用的模型路由：{error}', '提供商模型目录已刷新。', '无法加载提供商模型目录：{error}', '虚拟模型已更新。', '无法保存 omway：{error}', '上移模型', '下移模型', '移除模型', '凭据验证通过。', '模型测试失败：{error}', '由运行环境管理', '尚未配置', '请输入当前控制台密码。', '请输入新的控制台密码。', '控制台密码确认不一致。', '无法更新控制台密码：{error}', '配置已保存。请重启应用以应用监听器或存储更改。', '将系统配置恢复为默认值？访问密码和已生成的 API 密钥将被保留。', '无法重置系统配置：{error}', '请选择从凭据池导出的 ZIP 归档。', '凭据池归档超过 10 MB 导入限制。', '正在检查凭据池归档并验证提供商凭据...', '凭据池归档已导入。', '无法导入凭据池归档：{error}', '{provider} 导入完成。', '{provider} 导入失败：{error}', '无法重新生成 API 密钥。', '无法确定重置时间', '重置时间：{time}', '下次重置', '重置时间：{time}'
    ],
    'zh-TW': [
        '正在載入可用模型...', '恢復此憑證與模型的路由', '恢復此供應商與模型的路由', '模型路由已恢復。', '無法恢復模型路由：{error}', '恢復因上游傳回 404 而被排除的所有模型路由？', '清除無法使用的路由', '已清除無法使用的模型路由。', '無法清除無法使用的模型路由：{error}', '供應商模型目錄已重新整理。', '無法載入供應商模型目錄：{error}', '虛擬模型已更新。', '無法儲存 omway：{error}', '上移模型', '下移模型', '移除模型', '憑證驗證成功。', '模型測試失敗：{error}', '由執行環境管理', '尚未設定', '請輸入目前的主控台密碼。', '請輸入新的主控台密碼。', '主控台密碼確認不相符。', '無法更新主控台密碼：{error}', '設定已儲存。請重新啟動應用程式以套用監聽器或儲存空間變更。', '將系統設定恢復為預設值？存取密碼與已產生的 API 金鑰將會保留。', '無法重設系統設定：{error}', '請選取從憑證集區匯出的 ZIP 封存檔。', '憑證集區封存檔超過 10 MB 匯入限制。', '正在檢查憑證集區封存檔並驗證供應商憑證...', '憑證集區封存檔已匯入。', '無法匯入憑證集區封存檔：{error}', '{provider} 匯入完成。', '{provider} 匯入失敗：{error}', '無法重新產生 API 金鑰。', '無法取得重設時間', '重設時間：{time}', '下次重設', '重設時間：{time}'
    ],
    de: [
        'Verfügbare Modelle werden geladen...', 'Diese Zugang-Modell-Route wiederherstellen', 'Diese Provider-Modell-Route wiederherstellen', 'Modellroute wiederhergestellt.', 'Die Modellroute konnte nicht wiederhergestellt werden: {error}', 'Alle nach einer 404-Antwort des Upstreams ausgeschlossenen Modellrouten wiederherstellen?', 'Nicht verfügbare Routen löschen', 'Nicht verfügbare Modellrouten wurden gelöscht.', 'Nicht verfügbare Modellrouten konnten nicht gelöscht werden: {error}', 'Provider-Modellkatalog aktualisiert.', 'Der Provider-Modellkatalog konnte nicht geladen werden: {error}', 'Virtuelles Modell aktualisiert.', 'omway konnte nicht gespeichert werden: {error}', 'Modell nach oben verschieben', 'Modell nach unten verschieben', 'Modell entfernen', 'Zugangsdaten geprüft.', 'Modelltest fehlgeschlagen: {error}', 'Von der Umgebung verwaltet', 'Nicht konfiguriert', 'Geben Sie das aktuelle Konsolenpasswort ein.', 'Geben Sie ein neues Konsolenpasswort ein.', 'Die Bestätigung des Konsolenpassworts stimmt nicht überein.', 'Das Konsolenpasswort konnte nicht aktualisiert werden: {error}', 'Konfiguration gespeichert. Starten Sie die Anwendung neu, um Listener- oder Speicheränderungen anzuwenden.', 'Systemkonfiguration zurücksetzen? Zugangspasswörter und der generierte API-Schlüssel bleiben erhalten.', 'Die Systemkonfiguration konnte nicht zurückgesetzt werden: {error}', 'Wählen Sie ein aus dem Zugangspool exportiertes ZIP-Archiv.', 'Das Pool-Archiv überschreitet das Importlimit von 10 MB.', 'Pool-Archiv wird geprüft und Provider-Zugangsdaten werden validiert...', 'Pool-Archiv importiert.', 'Das Pool-Archiv konnte nicht importiert werden: {error}', '{provider}-Import abgeschlossen.', '{provider}-Import fehlgeschlagen: {error}', 'Der API-Schlüssel konnte nicht neu erstellt werden.', 'Rücksetzzeit nicht verfügbar', 'Zurücksetzung {time}', 'Nächste Zurücksetzung', 'Zurücksetzung {time}'
    ],
    es: [
        'Cargando modelos disponibles...', 'Restaurar esta ruta de credencial y modelo', 'Restaurar esta ruta de proveedor y modelo', 'Ruta de modelo restaurada.', 'No se pudo restaurar la ruta del modelo: {error}', '¿Restaurar todas las rutas de modelo excluidas tras una respuesta 404 del proveedor?', 'Limpiar rutas no disponibles', 'Se limpiaron las rutas de modelo no disponibles.', 'No se pudieron limpiar las rutas no disponibles: {error}', 'Catálogo de modelos de proveedores actualizado.', 'No se pudo cargar el catálogo de modelos de proveedores: {error}', 'Modelo virtual actualizado.', 'No se pudo guardar omway: {error}', 'Subir modelo', 'Bajar modelo', 'Quitar modelo', 'Credencial verificada.', 'La prueba del modelo falló: {error}', 'Administrado por el entorno', 'Sin configurar', 'Introduce la contraseña actual de la consola.', 'Introduce una nueva contraseña para la consola.', 'La confirmación de la contraseña no coincide.', 'No se pudo actualizar la contraseña de la consola: {error}', 'Configuración guardada. Reinicia la aplicación para aplicar los cambios del puerto de escucha o del almacenamiento.', '¿Restablecer la configuración del sistema? Se conservarán las contraseñas de acceso y la clave API generada.', 'No se pudo restablecer la configuración del sistema: {error}', 'Selecciona un archivo ZIP exportado desde el pool de credenciales.', 'El archivo del pool supera el límite de importación de 10 MB.', 'Inspeccionando el archivo del pool y validando las credenciales de los proveedores...', 'Archivo del pool importado.', 'No se pudo importar el archivo del pool: {error}', 'Importación de {provider} completada.', 'La importación de {provider} falló: {error}', 'No se pudo regenerar la clave API.', 'Hora de restablecimiento no disponible', 'Se restablece {time}', 'Próximo restablecimiento', 'Restablecimiento {time}'
    ],
    fr: [
        'Chargement des modèles disponibles...', 'Rétablir cette route identifiant-modèle', 'Rétablir cette route fournisseur-modèle', 'Route de modèle rétablie.', 'Impossible de rétablir la route du modèle : {error}', 'Rétablir toutes les routes de modèles exclues après une réponse 404 du fournisseur ?', 'Effacer les routes indisponibles', 'Les routes de modèles indisponibles ont été effacées.', 'Impossible d’effacer les routes indisponibles : {error}', 'Catalogue des modèles fournisseurs actualisé.', 'Impossible de charger le catalogue des modèles fournisseurs : {error}', 'Modèle virtuel mis à jour.', 'Impossible d’enregistrer omway : {error}', 'Monter le modèle', 'Descendre le modèle', 'Retirer le modèle', 'Identifiant vérifié.', 'Échec du test du modèle : {error}', 'Géré par l’environnement', 'Non configuré', 'Saisissez le mot de passe actuel de la console.', 'Saisissez un nouveau mot de passe pour la console.', 'La confirmation du mot de passe ne correspond pas.', 'Impossible de mettre à jour le mot de passe de la console : {error}', 'Configuration enregistrée. Redémarrez l’application pour appliquer les changements d’écoute ou de stockage.', 'Rétablir la configuration système par défaut ? Les mots de passe d’accès et la clé API générée seront conservés.', 'Impossible de réinitialiser la configuration système : {error}', 'Sélectionnez une archive ZIP exportée depuis le pool d’identifiants.', 'L’archive du pool dépasse la limite d’importation de 10 Mo.', 'Analyse de l’archive du pool et validation des identifiants fournisseurs...', 'Archive du pool importée.', 'Impossible d’importer l’archive du pool : {error}', 'Importation {provider} terminée.', 'Échec de l’importation {provider} : {error}', 'Impossible de régénérer la clé API.', 'Heure de réinitialisation indisponible', 'Réinitialisation {time}', 'Prochaine réinitialisation', 'Réinitialisation {time}'
    ],
    id: [
        'Memuat model yang tersedia...', 'Pulihkan rute kredensial-model ini', 'Pulihkan rute penyedia-model ini', 'Rute model dipulihkan.', 'Rute model tidak dapat dipulihkan: {error}', 'Pulihkan semua rute model yang dikecualikan setelah respons 404 dari penyedia?', 'Hapus Rute yang Tidak Tersedia', 'Rute model yang tidak tersedia telah dihapus.', 'Rute yang tidak tersedia tidak dapat dihapus: {error}', 'Katalog model penyedia diperbarui.', 'Katalog model penyedia tidak dapat dimuat: {error}', 'Model virtual diperbarui.', 'omway tidak dapat disimpan: {error}', 'Naikkan model', 'Turunkan model', 'Hapus model', 'Kredensial berhasil diverifikasi.', 'Pengujian model gagal: {error}', 'Dikelola oleh lingkungan', 'Belum dikonfigurasi', 'Masukkan kata sandi konsol saat ini.', 'Masukkan kata sandi konsol yang baru.', 'Konfirmasi kata sandi konsol tidak cocok.', 'Kata sandi konsol tidak dapat diperbarui: {error}', 'Konfigurasi disimpan. Mulai ulang aplikasi untuk menerapkan perubahan listener atau penyimpanan.', 'Reset konfigurasi sistem ke nilai bawaan? Kata sandi akses dan kunci API yang dibuat akan dipertahankan.', 'Konfigurasi sistem tidak dapat direset: {error}', 'Pilih arsip ZIP yang diekspor dari kumpulan kredensial.', 'Arsip kumpulan melebihi batas impor 10 MB.', 'Memeriksa arsip kumpulan dan memvalidasi kredensial penyedia...', 'Arsip kumpulan diimpor.', 'Arsip kumpulan tidak dapat diimpor: {error}', 'Impor {provider} selesai.', 'Impor {provider} gagal: {error}', 'Kunci API tidak dapat dibuat ulang.', 'Waktu reset tidak tersedia', 'Direset {time}', 'Reset berikutnya', 'Reset {time}'
    ],
    it: [
        'Caricamento dei modelli disponibili...', 'Ripristina questa route credenziale-modello', 'Ripristina questa route provider-modello', 'Route del modello ripristinata.', 'Impossibile ripristinare la route del modello: {error}', 'Ripristinare tutte le route dei modelli escluse dopo una risposta 404 del provider?', 'Cancella route non disponibili', 'Route dei modelli non disponibili cancellate.', 'Impossibile cancellare le route non disponibili: {error}', 'Catalogo dei modelli dei provider aggiornato.', 'Impossibile caricare il catalogo dei modelli dei provider: {error}', 'Modello virtuale aggiornato.', 'Impossibile salvare omway: {error}', 'Sposta il modello in alto', 'Sposta il modello in basso', 'Rimuovi modello', 'Credenziale verificata.', 'Test del modello non riuscito: {error}', 'Gestito dall’ambiente', 'Non configurato', 'Inserisci la password corrente della console.', 'Inserisci una nuova password per la console.', 'La conferma della password non corrisponde.', 'Impossibile aggiornare la password della console: {error}', 'Configurazione salvata. Riavvia l’applicazione per applicare le modifiche al listener o all’archiviazione.', 'Ripristinare la configurazione di sistema? Le password di accesso e la chiave API generata saranno conservate.', 'Impossibile ripristinare la configurazione di sistema: {error}', 'Seleziona un archivio ZIP esportato dal pool di credenziali.', 'L’archivio del pool supera il limite di importazione di 10 MB.', 'Analisi dell’archivio del pool e convalida delle credenziali dei provider...', 'Archivio del pool importato.', 'Impossibile importare l’archivio del pool: {error}', 'Importazione {provider} completata.', 'Importazione {provider} non riuscita: {error}', 'Impossibile rigenerare la chiave API.', 'Ora di ripristino non disponibile', 'Ripristino {time}', 'Prossimo ripristino', 'Ripristino {time}'
    ],
    ja: [
        '利用可能なモデルを読み込んでいます...', 'この認証情報とモデルのルートを復元', 'このプロバイダーとモデルのルートを復元', 'モデルルートを復元しました。', 'モデルルートを復元できませんでした：{error}', 'アップストリームの 404 応答後に除外されたすべてのモデルルートを復元しますか？', '利用不可ルートを消去', '利用不可のモデルルートを消去しました。', '利用不可のモデルルートを消去できませんでした：{error}', 'プロバイダーのモデルカタログを更新しました。', 'プロバイダーのモデルカタログを読み込めませんでした：{error}', '仮想モデルを更新しました。', 'omway を保存できませんでした：{error}', 'モデルを上へ移動', 'モデルを下へ移動', 'モデルを削除', '認証情報を確認しました。', 'モデルテストに失敗しました：{error}', '実行環境で管理', '未設定', '現在のコンソールパスワードを入力してください。', '新しいコンソールパスワードを入力してください。', 'コンソールパスワードの確認が一致しません。', 'コンソールパスワードを更新できませんでした：{error}', '設定を保存しました。リスナーまたは保存先の変更を反映するにはアプリケーションを再起動してください。', 'システム設定を初期値に戻しますか？アクセス用パスワードと生成済み API キーは保持されます。', 'システム設定をリセットできませんでした：{error}', '認証情報プールから書き出した ZIP アーカイブを選択してください。', 'プールのアーカイブが 10 MB のインポート上限を超えています。', 'プールのアーカイブを確認し、プロバイダーの認証情報を検証しています...', 'プールのアーカイブをインポートしました。', 'プールのアーカイブをインポートできませんでした：{error}', '{provider} のインポートが完了しました。', '{provider} のインポートに失敗しました：{error}', 'API キーを再生成できませんでした。', 'リセット時刻を取得できません', '{time} にリセット', '次回のリセット', '{time} にリセット'
    ],
    ko: [
        '사용 가능한 모델을 불러오는 중...', '이 자격 증명-모델 경로 복원', '이 공급자-모델 경로 복원', '모델 경로를 복원했습니다.', '모델 경로를 복원하지 못했습니다: {error}', '업스트림의 404 응답 후 제외된 모든 모델 경로를 복원할까요?', '사용 불가 경로 지우기', '사용 불가 모델 경로를 지웠습니다.', '사용 불가 모델 경로를 지우지 못했습니다: {error}', '공급자 모델 카탈로그를 새로 고쳤습니다.', '공급자 모델 카탈로그를 불러오지 못했습니다: {error}', '가상 모델을 업데이트했습니다.', 'omway를 저장하지 못했습니다: {error}', '모델 위로 이동', '모델 아래로 이동', '모델 제거', '자격 증명을 확인했습니다.', '모델 테스트 실패: {error}', '환경에서 관리됨', '설정되지 않음', '현재 콘솔 비밀번호를 입력하세요.', '새 콘솔 비밀번호를 입력하세요.', '콘솔 비밀번호 확인이 일치하지 않습니다.', '콘솔 비밀번호를 업데이트하지 못했습니다: {error}', '설정을 저장했습니다. 리스너 또는 저장소 변경 사항을 적용하려면 애플리케이션을 다시 시작하세요.', '시스템 설정을 기본값으로 되돌릴까요? 접근 비밀번호와 생성된 API 키는 유지됩니다.', '시스템 설정을 재설정하지 못했습니다: {error}', '자격 증명 풀에서 내보낸 ZIP 압축 파일을 선택하세요.', '풀 압축 파일이 10 MB 가져오기 제한을 초과했습니다.', '풀 압축 파일을 검사하고 공급자 자격 증명을 확인하는 중...', '풀 압축 파일을 가져왔습니다.', '풀 압축 파일을 가져오지 못했습니다: {error}', '{provider} 가져오기를 완료했습니다.', '{provider} 가져오기 실패: {error}', 'API 키를 재생성하지 못했습니다.', '재설정 시간을 알 수 없음', '{time}에 재설정', '다음 재설정', '{time}에 재설정'
    ],
    pt: [
        'Carregando modelos disponíveis...', 'Restaurar esta rota de credencial e modelo', 'Restaurar esta rota de provedor e modelo', 'Rota do modelo restaurada.', 'Não foi possível restaurar a rota do modelo: {error}', 'Restaurar todas as rotas de modelo excluídas após uma resposta 404 do provedor?', 'Limpar Rotas Indisponíveis', 'Rotas de modelo indisponíveis removidas.', 'Não foi possível limpar as rotas indisponíveis: {error}', 'Catálogo de modelos dos provedores atualizado.', 'Não foi possível carregar o catálogo de modelos dos provedores: {error}', 'Modelo virtual atualizado.', 'Não foi possível salvar omway: {error}', 'Mover modelo para cima', 'Mover modelo para baixo', 'Remover modelo', 'Credencial verificada.', 'Falha no teste do modelo: {error}', 'Gerenciado pelo ambiente', 'Não configurado', 'Digite a senha atual do console.', 'Digite uma nova senha para o console.', 'A confirmação da senha do console não corresponde.', 'Não foi possível atualizar a senha do console: {error}', 'Configuração salva. Reinicie o aplicativo para aplicar alterações do listener ou armazenamento.', 'Redefinir a configuração do sistema? As senhas de acesso e a chave API gerada serão preservadas.', 'Não foi possível redefinir a configuração do sistema: {error}', 'Selecione um arquivo ZIP exportado do pool de credenciais.', 'O arquivo do pool excede o limite de importação de 10 MB.', 'Inspecionando o arquivo do pool e validando credenciais dos provedores...', 'Arquivo do pool importado.', 'Não foi possível importar o arquivo do pool: {error}', 'Importação de {provider} concluída.', 'Falha na importação de {provider}: {error}', 'Não foi possível regenerar a chave API.', 'Horário de redefinição indisponível', 'Redefine {time}', 'Próxima redefinição', 'Redefinição {time}'
    ],
    ru: [
        'Загрузка доступных моделей...', 'Восстановить маршрут учётных данных и модели', 'Восстановить маршрут провайдера и модели', 'Маршрут модели восстановлен.', 'Не удалось восстановить маршрут модели: {error}', 'Восстановить все маршруты моделей, исключённые после ответа 404 от провайдера?', 'Очистить недоступные маршруты', 'Недоступные маршруты моделей очищены.', 'Не удалось очистить недоступные маршруты: {error}', 'Каталог моделей провайдеров обновлён.', 'Не удалось загрузить каталог моделей провайдеров: {error}', 'Виртуальная модель обновлена.', 'Не удалось сохранить omway: {error}', 'Переместить модель вверх', 'Переместить модель вниз', 'Удалить модель', 'Учётные данные проверены.', 'Проверка модели завершилась ошибкой: {error}', 'Управляется окружением', 'Не настроено', 'Введите текущий пароль консоли.', 'Введите новый пароль консоли.', 'Подтверждение пароля консоли не совпадает.', 'Не удалось обновить пароль консоли: {error}', 'Конфигурация сохранена. Перезапустите приложение, чтобы применить изменения прослушивателя или хранилища.', 'Сбросить системную конфигурацию? Пароли доступа и сгенерированный ключ API будут сохранены.', 'Не удалось сбросить системную конфигурацию: {error}', 'Выберите ZIP-архив, экспортированный из пула учётных данных.', 'Архив пула превышает ограничение импорта 10 МБ.', 'Проверка архива пула и учётных данных провайдеров...', 'Архив пула импортирован.', 'Не удалось импортировать архив пула: {error}', 'Импорт {provider} завершён.', 'Не удалось импортировать {provider}: {error}', 'Не удалось создать новый API-ключ.', 'Время сброса недоступно', 'Сброс {time}', 'Следующий сброс', 'Сброс {time}'
    ],
    th: [
        'กำลังโหลดโมเดลที่ใช้ได้...', 'คืนค่าเส้นทางข้อมูลรับรองกับโมเดลนี้', 'คืนค่าเส้นทางผู้ให้บริการกับโมเดลนี้', 'คืนค่าเส้นทางโมเดลแล้ว', 'ไม่สามารถคืนค่าเส้นทางโมเดล: {error}', 'คืนค่าเส้นทางโมเดลทั้งหมดที่ถูกตัดออกหลังผู้ให้บริการตอบกลับ 404 หรือไม่', 'ล้างเส้นทางที่ใช้ไม่ได้', 'ล้างเส้นทางโมเดลที่ใช้ไม่ได้แล้ว', 'ไม่สามารถล้างเส้นทางที่ใช้ไม่ได้: {error}', 'รีเฟรชรายการโมเดลของผู้ให้บริการแล้ว', 'ไม่สามารถโหลดรายการโมเดลของผู้ให้บริการ: {error}', 'อัปเดตโมเดลเสมือนแล้ว', 'ไม่สามารถบันทึก omway: {error}', 'เลื่อนโมเดลขึ้น', 'เลื่อนโมเดลลง', 'นำโมเดลออก', 'ตรวจสอบข้อมูลรับรองแล้ว', 'ทดสอบโมเดลไม่สำเร็จ: {error}', 'จัดการโดยสภาพแวดล้อม', 'ยังไม่ได้กำหนดค่า', 'โปรดป้อนรหัสผ่านคอนโซลปัจจุบัน', 'โปรดป้อนรหัสผ่านคอนโซลใหม่', 'การยืนยันรหัสผ่านคอนโซลไม่ตรงกัน', 'ไม่สามารถอัปเดตรหัสผ่านคอนโซล: {error}', 'บันทึกการกำหนดค่าแล้ว โปรดรีสตาร์ตแอปเพื่อใช้การเปลี่ยนแปลง listener หรือพื้นที่จัดเก็บ', 'รีเซ็ตการกำหนดค่าระบบหรือไม่ รหัสผ่านการเข้าถึงและคีย์ API ที่สร้างไว้จะยังคงอยู่', 'ไม่สามารถรีเซ็ตการกำหนดค่าระบบ: {error}', 'เลือกไฟล์ ZIP ที่ส่งออกจากพูลข้อมูลรับรอง', 'ไฟล์พูลมีขนาดเกินขีดจำกัดการนำเข้า 10 MB', 'กำลังตรวจสอบไฟล์พูลและยืนยันข้อมูลรับรองของผู้ให้บริการ...', 'นำเข้าไฟล์พูลแล้ว', 'ไม่สามารถนำเข้าไฟล์พูล: {error}', 'นำเข้า {provider} เสร็จแล้ว', 'นำเข้า {provider} ไม่สำเร็จ: {error}', 'ไม่สามารถสร้างคีย์ API ใหม่ได้', 'ไม่มีข้อมูลเวลารีเซ็ต', 'รีเซ็ต {time}', 'รีเซ็ตครั้งถัดไป', 'รีเซ็ต {time}'
    ],
    tr: [
        'Kullanılabilir modeller yükleniyor...', 'Bu kimlik bilgisi-model rotasını geri yükle', 'Bu sağlayıcı-model rotasını geri yükle', 'Model rotası geri yüklendi.', 'Model rotası geri yüklenemedi: {error}', 'Üst sağlayıcının 404 yanıtından sonra dışlanan tüm model rotaları geri yüklensin mi?', 'Kullanılamayan Rotaları Temizle', 'Kullanılamayan model rotaları temizlendi.', 'Kullanılamayan rotalar temizlenemedi: {error}', 'Sağlayıcı model kataloğu yenilendi.', 'Sağlayıcı model kataloğu yüklenemedi: {error}', 'Sanal model güncellendi.', 'omway kaydedilemedi: {error}', 'Modeli yukarı taşı', 'Modeli aşağı taşı', 'Modeli kaldır', 'Kimlik bilgisi doğrulandı.', 'Model testi başarısız: {error}', 'Ortam tarafından yönetiliyor', 'Yapılandırılmadı', 'Geçerli konsol parolasını girin.', 'Yeni bir konsol parolası girin.', 'Konsol parolası doğrulaması eşleşmiyor.', 'Konsol parolası güncellenemedi: {error}', 'Yapılandırma kaydedildi. Dinleyici veya depolama değişikliklerini uygulamak için uygulamayı yeniden başlatın.', 'Sistem yapılandırması varsayılanlara sıfırlansın mı? Erişim parolaları ve oluşturulan API anahtarı korunur.', 'Sistem yapılandırması sıfırlanamadı: {error}', 'Kimlik bilgisi havuzundan dışa aktarılan bir ZIP arşivi seçin.', 'Havuz arşivi 10 MB içe aktarma sınırını aşıyor.', 'Havuz arşivi inceleniyor ve sağlayıcı kimlik bilgileri doğrulanıyor...', 'Havuz arşivi içe aktarıldı.', 'Havuz arşivi içe aktarılamadı: {error}', '{provider} içe aktarması tamamlandı.', '{provider} içe aktarması başarısız: {error}', 'API anahtarı yeniden oluşturulamadı.', 'Sıfırlama zamanı kullanılamıyor', '{time} tarihinde sıfırlanır', 'Sonraki sıfırlama', '{time} tarihinde sıfırlanır'
    ],
    vi: [
        'Đang tải các mô hình khả dụng...', 'Khôi phục tuyến thông tin xác thực-mô hình này', 'Khôi phục tuyến nhà cung cấp-mô hình này', 'Đã khôi phục tuyến mô hình.', 'Không thể khôi phục tuyến mô hình: {error}', 'Khôi phục tất cả tuyến mô hình đã bị loại sau khi upstream trả về mã 404?', 'Xóa các tuyến không khả dụng', 'Đã xóa các tuyến mô hình không khả dụng.', 'Không thể xóa các tuyến không khả dụng: {error}', 'Đã làm mới danh mục mô hình của nhà cung cấp.', 'Không thể tải danh mục mô hình của nhà cung cấp: {error}', 'Đã cập nhật mô hình ảo.', 'Không thể lưu omway: {error}', 'Di chuyển mô hình lên', 'Di chuyển mô hình xuống', 'Xóa mô hình', 'Đã xác minh thông tin xác thực.', 'Kiểm tra mô hình không thành công: {error}', 'Do môi trường quản lý', 'Chưa cấu hình', 'Nhập mật khẩu bảng điều khiển hiện tại.', 'Nhập mật khẩu bảng điều khiển mới.', 'Mật khẩu xác nhận không khớp.', 'Không thể cập nhật mật khẩu bảng điều khiển: {error}', 'Đã lưu cấu hình. Hãy khởi động lại ứng dụng để áp dụng thay đổi về listener hoặc nơi lưu trữ.', 'Khôi phục cấu hình hệ thống về mặc định? Mật khẩu truy cập và khóa API đã tạo sẽ được giữ nguyên.', 'Không thể khôi phục cấu hình hệ thống: {error}', 'Chọn tệp ZIP được xuất từ pool thông tin xác thực.', 'Tệp lưu trữ của pool vượt quá giới hạn nhập 10 MB.', 'Đang kiểm tra tệp lưu trữ của pool và xác thực thông tin của nhà cung cấp...', 'Đã nhập tệp lưu trữ của pool.', 'Không thể nhập tệp lưu trữ của pool: {error}', 'Đã hoàn tất nhập {provider}.', 'Không thể nhập {provider}: {error}', 'Không thể tạo lại khóa API.', 'Không có thời gian đặt lại', 'Đặt lại lúc {time}', 'Lần đặt lại tiếp theo', 'Đặt lại lúc {time}'
    ]
};

for (const [locale, values] of Object.entries(OPERATION_COPY_VALUES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(OPERATION_COPY_KEYS.map((key, index) => [key, values[index]])));
}

const CREDENTIAL_CARD_KEYS = [
    'provider_antigravity', 'provider_google_ai_studio', 'provider_grok', 'provider_xai_console',
    'provider_codex', 'provider_openai_platform', 'provider_claude_code', 'provider_claude_platform',
    'provider_ollama',
    'btn_view_content', 'btn_view_content_title', 'btn_download', 'btn_view_models', 'btn_view_models_title',
    'btn_view_quota', 'btn_view_quota_title', 'btn_enable_credit', 'btn_enable_credit_title',
    'btn_disable_credit', 'btn_disable_credit_title', 'btn_setup_preview', 'btn_setup_preview_title',
    'btn_verify_id', 'btn_verify_id_title', 'btn_test_model', 'btn_test_model_title',
    'btn_view_errors', 'btn_view_errors_title', 'credential_count', 'credential_badge_auto_disabled',
    'credential_badge_preview', 'credential_badge_tier', 'credential_badge_plan', 'credential_badge_credits',
    'credential_state_on', 'credential_state_off', 'credential_badge_cooldown'
];

const CREDENTIAL_CARD_VALUES = {
    en: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Details', 'View the stored details and payload for this credential.', 'Download', 'Models', 'View models available through this credential.',
        'Quota', 'View quota usage information for this credential.', 'Enable credit', 'Allow this credential to use available Google One AI credits.',
        'Disable credit', 'Prevent this credential from using available Google One AI credits.', 'Configure', 'Configure the Preview channel and enable experimental features.',
        'Verify', 'Verify this credential and refresh its provider metadata.', 'Test', 'Select a model and test it with this credential.',
        'Errors', 'View detailed error messages for this credential.', '{count} credentials', 'Auto-disabled',
        'Preview: {state}', 'Tier: {tier}', 'Plan: {plan}', 'Credits: {state}', 'On', 'Off', 'Cooldown {model}: {time}'
    ],
    'zh-CN': [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        '详情', '查看此凭据保存的详情和内容。', '下载', '模型', '查看此凭据可用的模型。',
        '配额', '查看此凭据的配额使用情况。', '启用积分', '允许此凭据使用可用的 Google One AI 积分。',
        '停用积分', '阻止此凭据使用可用的 Google One AI 积分。', '配置', '配置 Preview 通道并启用实验性功能。',
        '验证', '验证此凭据并刷新其提供商元数据。', '测试', '选择一个模型并使用此凭据进行测试。',
        '错误', '查看此凭据的详细错误信息。', '{count} 个凭据', '已自动停用',
        'Preview：{state}', '层级：{tier}', '套餐：{plan}', '积分：{state}', '开启', '关闭', '冷却 {model}：{time}'
    ],
    'zh-TW': [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        '詳細資料', '檢視此憑證儲存的詳細資料和內容。', '下載', '模型', '檢視此憑證可用的模型。',
        '配額', '檢視此憑證的配額使用情況。', '啟用點數', '允許此憑證使用可用的 Google One AI 點數。',
        '停用點數', '禁止此憑證使用可用的 Google One AI 點數。', '設定', '設定 Preview 頻道並啟用實驗性功能。',
        '驗證', '驗證此憑證並重新整理其供應商中繼資料。', '測試', '選擇模型並使用此憑證進行測試。',
        '錯誤', '檢視此憑證的詳細錯誤訊息。', '{count} 個憑證', '已自動停用',
        'Preview：{state}', '層級：{tier}', '方案：{plan}', '點數：{state}', '開啟', '關閉', '冷卻 {model}：{time}'
    ],
    de: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Details', 'Gespeicherte Details und Daten dieser Zugangsdaten anzeigen.', 'Herunterladen', 'Modelle', 'Mit diesen Zugangsdaten verfügbare Modelle anzeigen.',
        'Kontingent', 'Kontingentnutzung dieser Zugangsdaten anzeigen.', 'Guthaben aktivieren', 'Diesen Zugangsdaten die Nutzung verfügbarer Google One AI-Guthaben erlauben.',
        'Guthaben deaktivieren', 'Diesen Zugangsdaten die Nutzung verfügbarer Google One AI-Guthaben untersagen.', 'Konfigurieren', 'Den Preview-Kanal konfigurieren und experimentelle Funktionen aktivieren.',
        'Prüfen', 'Diese Zugangsdaten prüfen und die Anbieter-Metadaten aktualisieren.', 'Testen', 'Ein Modell auswählen und mit diesen Zugangsdaten testen.',
        'Fehler', 'Detaillierte Fehlermeldungen für diese Zugangsdaten anzeigen.', '{count} Zugangsdaten', 'Automatisch deaktiviert',
        'Vorschau: {state}', 'Stufe: {tier}', 'Tarif: {plan}', 'Guthaben: {state}', 'Ein', 'Aus', 'Wartezeit {model}: {time}'
    ],
    es: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Detalles', 'Ver los detalles y datos guardados de esta credencial.', 'Descargar', 'Modelos', 'Ver los modelos disponibles mediante esta credencial.',
        'Cuota', 'Ver el uso de cuota de esta credencial.', 'Activar créditos', 'Permitir que esta credencial use créditos disponibles de Google One AI.',
        'Desactivar créditos', 'Impedir que esta credencial use créditos disponibles de Google One AI.', 'Configurar', 'Configurar el canal Preview y activar funciones experimentales.',
        'Verificar', 'Verificar esta credencial y actualizar sus metadatos del proveedor.', 'Probar', 'Seleccionar un modelo y probarlo con esta credencial.',
        'Errores', 'Ver mensajes de error detallados de esta credencial.', '{count} credenciales', 'Desactivada automáticamente',
        'Vista previa: {state}', 'Nivel: {tier}', 'Plan: {plan}', 'Créditos: {state}', 'Activado', 'Desactivado', 'En espera {model}: {time}'
    ],
    fr: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Détails', 'Afficher les détails et les données enregistrées pour cet identifiant.', 'Télécharger', 'Modèles', 'Afficher les modèles disponibles avec cet identifiant.',
        'Quota', 'Afficher l’utilisation du quota de cet identifiant.', 'Activer les crédits', 'Autoriser cet identifiant à utiliser les crédits Google One AI disponibles.',
        'Désactiver les crédits', 'Empêcher cet identifiant d’utiliser les crédits Google One AI disponibles.', 'Configurer', 'Configurer le canal Preview et activer les fonctionnalités expérimentales.',
        'Vérifier', 'Vérifier cet identifiant et actualiser les métadonnées du fournisseur.', 'Tester', 'Sélectionner un modèle et le tester avec cet identifiant.',
        'Erreurs', 'Afficher les messages d’erreur détaillés pour cet identifiant.', '{count} identifiants', 'Désactivé automatiquement',
        'Aperçu : {state}', 'Niveau : {tier}', 'Forfait : {plan}', 'Crédits : {state}', 'Activé', 'Désactivé', 'Délai {model} : {time}'
    ],
    id: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Detail', 'Lihat detail dan data yang tersimpan untuk kredensial ini.', 'Unduh', 'Model', 'Lihat model yang tersedia melalui kredensial ini.',
        'Kuota', 'Lihat penggunaan kuota untuk kredensial ini.', 'Aktifkan kredit', 'Izinkan kredensial ini menggunakan kredit Google One AI yang tersedia.',
        'Nonaktifkan kredit', 'Cegah kredensial ini menggunakan kredit Google One AI yang tersedia.', 'Konfigurasi', 'Konfigurasikan kanal Preview dan aktifkan fitur eksperimental.',
        'Verifikasi', 'Verifikasi kredensial ini dan perbarui metadata penyedianya.', 'Uji', 'Pilih model dan uji dengan kredensial ini.',
        'Error', 'Lihat pesan error terperinci untuk kredensial ini.', '{count} kredensial', 'Dinonaktifkan otomatis',
        'Pratinjau: {state}', 'Tingkat: {tier}', 'Paket: {plan}', 'Kredit: {state}', 'Aktif', 'Nonaktif', 'Jeda {model}: {time}'
    ],
    it: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Dettagli', 'Visualizza i dettagli e i dati salvati per questa credenziale.', 'Scarica', 'Modelli', 'Visualizza i modelli disponibili tramite questa credenziale.',
        'Quota', 'Visualizza l’utilizzo della quota per questa credenziale.', 'Abilita crediti', 'Consenti a questa credenziale di usare i crediti Google One AI disponibili.',
        'Disabilita crediti', 'Impedisci a questa credenziale di usare i crediti Google One AI disponibili.', 'Configura', 'Configura il canale Preview e abilita le funzionalità sperimentali.',
        'Verifica', 'Verifica questa credenziale e aggiorna i relativi metadati del provider.', 'Testa', 'Seleziona un modello e testalo con questa credenziale.',
        'Errori', 'Visualizza messaggi di errore dettagliati per questa credenziale.', '{count} credenziali', 'Disabilitata automaticamente',
        'Anteprima: {state}', 'Livello: {tier}', 'Piano: {plan}', 'Crediti: {state}', 'Attivo', 'Disattivo', 'Attesa {model}: {time}'
    ],
    ja: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        '詳細', 'この認証情報に保存されている詳細とデータを表示します。', 'ダウンロード', 'モデル', 'この認証情報で利用できるモデルを表示します。',
        'クォータ', 'この認証情報のクォータ使用状況を表示します。', 'クレジットを有効化', 'この認証情報で利用可能な Google One AI クレジットの使用を許可します。',
        'クレジットを無効化', 'この認証情報で利用可能な Google One AI クレジットの使用を停止します。', '設定', 'Preview チャネルを設定し、実験的な機能を有効にします。',
        '検証', 'この認証情報を検証し、プロバイダーのメタデータを更新します。', 'テスト', 'モデルを選択し、この認証情報でテストします。',
        'エラー', 'この認証情報の詳細なエラーメッセージを表示します。', '{count} 件の認証情報', '自動的に無効化',
        'プレビュー: {state}', '階層: {tier}', 'プラン: {plan}', 'クレジット: {state}', 'オン', 'オフ', 'クールダウン {model}: {time}'
    ],
    ko: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        '세부 정보', '이 자격 증명에 저장된 세부 정보와 데이터를 봅니다.', '다운로드', '모델', '이 자격 증명으로 사용할 수 있는 모델을 봅니다.',
        '할당량', '이 자격 증명의 할당량 사용량을 봅니다.', '크레딧 사용', '이 자격 증명이 사용 가능한 Google One AI 크레딧을 사용하도록 허용합니다.',
        '크레딧 해제', '이 자격 증명이 사용 가능한 Google One AI 크레딧을 사용하지 못하도록 합니다.', '구성', 'Preview 채널을 구성하고 실험적 기능을 활성화합니다.',
        '검증', '이 자격 증명을 검증하고 제공업체 메타데이터를 새로 고칩니다.', '테스트', '모델을 선택하고 이 자격 증명으로 테스트합니다.',
        '오류', '이 자격 증명의 자세한 오류 메시지를 봅니다.', '자격 증명 {count}개', '자동 비활성화됨',
        '미리 보기: {state}', '등급: {tier}', '요금제: {plan}', '크레딧: {state}', '사용', '사용 안 함', '대기 {model}: {time}'
    ],
    pt: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Detalhes', 'Veja os detalhes e os dados salvos desta credencial.', 'Baixar', 'Modelos', 'Veja os modelos disponíveis com esta credencial.',
        'Cota', 'Veja o uso de cota desta credencial.', 'Ativar créditos', 'Permita que esta credencial use os créditos disponíveis do Google One AI.',
        'Desactivar créditos', 'Impeça que esta credencial use os créditos disponíveis do Google One AI.', 'Configurar', 'Configure o canal Preview e ative recursos experimentais.',
        'Verificar', 'Verifique esta credencial e atualize os metadados do provedor.', 'Testar', 'Selecione um modelo e teste-o com esta credencial.',
        'Erros', 'Veja mensagens de erro detalhadas desta credencial.', '{count} credenciais', 'Desativada automaticamente',
        'Visualização: {state}', 'Nível: {tier}', 'Plano: {plan}', 'Créditos: {state}', 'Ativado', 'Desativado', 'Espera {model}: {time}'
    ],
    ru: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Сведения', 'Показать сохранённые сведения и данные этих учётных данных.', 'Скачать', 'Модели', 'Показать модели, доступные через эти учётные данные.',
        'Квота', 'Показать использование квоты для этих учётных данных.', 'Включить кредиты', 'Разрешить этим учётным данным использовать доступные кредиты Google One AI.',
        'Отключить кредиты', 'Запретить этим учётным данным использовать доступные кредиты Google One AI.', 'Настроить', 'Настроить канал Preview и включить экспериментальные функции.',
        'Проверить', 'Проверить эти учётные данные и обновить метаданные провайдера.', 'Тестировать', 'Выбрать модель и проверить её с этими учётными данными.',
        'Ошибки', 'Показать подробные сообщения об ошибках для этих учётных данных.', '{count} учётных данных', 'Автоматически отключено',
        'Предпросмотр: {state}', 'Уровень: {tier}', 'Тариф: {plan}', 'Кредиты: {state}', 'Вкл.', 'Выкл.', 'Ожидание {model}: {time}'
    ],
    th: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'รายละเอียด', 'ดูรายละเอียดและข้อมูลที่บันทึกไว้สำหรับข้อมูลรับรองนี้', 'ดาวน์โหลด', 'โมเดล', 'ดูโมเดลที่ใช้ได้ผ่านข้อมูลรับรองนี้',
        'โควตา', 'ดูการใช้โควตาของข้อมูลรับรองนี้', 'เปิดใช้เครดิต', 'อนุญาตให้ข้อมูลรับรองนี้ใช้เครดิต Google One AI ที่มีอยู่',
        'ปิดใช้เครดิต', 'ป้องกันไม่ให้ข้อมูลรับรองนี้ใช้เครดิต Google One AI ที่มีอยู่', 'ตั้งค่า', 'ตั้งค่าช่องทาง Preview และเปิดใช้ฟีเจอร์ทดลอง',
        'ตรวจสอบ', 'ตรวจสอบข้อมูลรับรองนี้และรีเฟรชข้อมูลเมตาของผู้ให้บริการ', 'ทดสอบ', 'เลือกโมเดลและทดสอบด้วยข้อมูลรับรองนี้',
        'ข้อผิดพลาด', 'ดูข้อความข้อผิดพลาดโดยละเอียดสำหรับข้อมูลรับรองนี้', '{count} ข้อมูลรับรอง', 'ปิดใช้งานอัตโนมัติ',
        'ตัวอย่าง: {state}', 'ระดับ: {tier}', 'แพ็กเกจ: {plan}', 'เครดิต: {state}', 'เปิด', 'ปิด', 'พัก {model}: {time}'
    ],
    tr: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Ayrıntılar', 'Bu kimlik bilgisinin kaydedilmiş ayrıntılarını ve verilerini görüntüle.', 'İndir', 'Modeller', 'Bu kimlik bilgisiyle kullanılabilen modelleri görüntüle.',
        'Kota', 'Bu kimlik bilgisinin kota kullanımını görüntüle.', 'Kredileri etkinleştir', 'Bu kimlik bilgisinin kullanılabilir Google One AI kredilerini kullanmasına izin ver.',
        'Kredileri devre dışı bırak', 'Bu kimlik bilgisinin kullanılabilir Google One AI kredilerini kullanmasını engelle.', 'Yapılandır', 'Preview kanalını yapılandır ve deneysel özellikleri etkinleştir.',
        'Doğrula', 'Bu kimlik bilgisini doğrula ve sağlayıcı meta verilerini yenile.', 'Test et', 'Bir model seç ve bu kimlik bilgisiyle test et.',
        'Hatalar', 'Bu kimlik bilgisi için ayrıntılı hata iletilerini görüntüle.', '{count} kimlik bilgisi', 'Otomatik devre dışı bırakıldı',
        'Ön izleme: {state}', 'Kademe: {tier}', 'Plan: {plan}', 'Krediler: {state}', 'Açık', 'Kapalı', 'Bekleme {model}: {time}'
    ],
    vi: [
        'Google Antigravity', 'Google AI Studio', 'Grok Build', 'SpaceXAI Console', 'Codex', 'OpenAI Platform', 'Claude Code', 'Claude Platform', 'Ollama',
        'Chi tiết', 'Xem chi tiết và dữ liệu đã lưu của thông tin xác thực này.', 'Tải xuống', 'Mô hình', 'Xem các mô hình có thể dùng với thông tin xác thực này.',
        'Hạn mức', 'Xem mức sử dụng hạn mức của thông tin xác thực này.', 'Bật credit', 'Cho phép thông tin xác thực này sử dụng credit Google One AI hiện có.',
        'Tắt credit', 'Ngăn thông tin xác thực này sử dụng credit Google One AI hiện có.', 'Cấu hình', 'Cấu hình kênh Preview và bật các tính năng thử nghiệm.',
        'Xác minh', 'Xác minh thông tin xác thực này và làm mới siêu dữ liệu của nhà cung cấp.', 'Thử model', 'Chọn một model và thử bằng thông tin xác thực này.',
        'Lỗi', 'Xem thông báo lỗi chi tiết của thông tin xác thực này.', '{count} thông tin xác thực', 'Tự động tắt',
        'Preview: {state}', 'Cấp: {tier}', 'Gói: {plan}', 'Credit: {state}', 'Bật', 'Tắt', 'Chờ {model}: {time}'
    ]
};

for (const [locale, values] of Object.entries(CREDENTIAL_CARD_VALUES)) {
    if (values.length !== CREDENTIAL_CARD_KEYS.length) {
        throw new Error(`Invalid credential card catalog for ${locale}.`);
    }
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(CREDENTIAL_CARD_KEYS.map((key, index) => [key, values[index]])));
}

const CREDENTIAL_MODAL_KEYS = [
    'modal.email', 'modal.project_id', 'modal.expiry', 'modal.credential_payload_intro',
    'modal.credential_summary', 'modal.credential_payload', 'modal.provider', 'modal.available_models',
    'modal.copy_model_id', 'modal.models_intro', 'modal.model_ids', 'modal.filter_models',
    'modal.filter_available_models', 'modal.no_models_match', 'modal.models_load_failed',
    'modal.credential_unavailable', 'modal.model_test_title', 'modal.no_models_available',
    'modal.model_test_intro', 'modal.model', 'modal.select_model', 'modal.test', 'modal.unavailable',
    'modal.monthly_credits', 'modal.weekly_usage', 'modal.account', 'modal.credential',
    'modal.quota_source', 'modal.grok_billing', 'modal.billing_periods', 'modal.lowest_remaining',
    'modal.credits_used', 'modal.percent_used', 'modal.percent_left', 'modal.grok_quota_intro',
    'modal.quota_summary', 'modal.plan', 'modal.usage_windows', 'modal.unknown', 'modal.reset_credits',
    'modal.standard_limit', 'modal.code_review_limit', 'modal.reached', 'modal.available',
    'modal.usage_limit', 'modal.codex_quota_intro', 'modal.tracked_models', 'modal.average_remaining',
    'modal.no_quota_intro', 'modal.model_quota_intro', 'modal.model_quota', 'modal.no_quota',
    'modal.average_quota_preview', 'modal.lowest_billing_preview', 'modal.billing_preview',
    'modal.lowest_window_preview', 'modal.window_preview', 'modal.status', 'modal.type', 'modal.reason',
    'modal.stored_errors', 'modal.no_errors_intro', 'modal.error_summary', 'modal.errors_intro'
];

const CREDENTIAL_MODAL_VALUES = {
    en: [
        'Email', 'Project ID', 'Expiry', 'This is the stored payload for the selected credential.',
        'Credential Summary', 'Credential Payload', 'Provider', 'Available models', 'Copy model ID',
        'These models are currently reported as available for this credential.', 'Model IDs', 'Filter models',
        'Filter available models', 'No models match this filter.', 'Unable to load available models.',
        'Credential information is unavailable.', 'Model Test', 'No models are currently available for this credential.',
        'Select a model to test with the {provider} credential{account}. The test sends a minimal generation request to the provider.',
        'Model', 'Select a model', 'Test', 'Unavailable', 'Monthly Credits', 'Weekly Usage', 'Account',
        'Credential', 'Quota source', 'Grok Build account billing', 'Billing periods', 'Lowest remaining quota',
        '{used} / {limit} credits used', '{value}% used', '{value}% left',
        'Account quota reported by Grok Build for the selected OAuth credential.', 'Quota Summary', 'Plan',
        'Usage windows', 'Unknown', 'Rate-limit reset credits', 'Standard limit', 'Code review limit',
        'Reached', 'Available', 'Usage Limit',
        'Account rate limits reported by Codex for the selected OAuth credential.', 'Tracked models',
        'Average remaining quota', 'No quota information is available for this credential yet.',
        'Quota usage is grouped by model for the selected credential.', 'Model Quota', 'No quota',
        'Average quota: {quota} across {count} models.', 'Lowest account quota: {quota} across {count} active billing periods.',
        'Account quota: {quota} for the active billing period.', 'Lowest account quota: {quota} across {count} usage windows.',
        'Account quota: {quota} for the active usage window.', 'Status', 'Type', 'Reason', 'Stored errors',
        'This credential has no stored provider errors.', 'Error Summary',
        'These are the latest provider errors recorded for this credential.'
    ],
    'zh-CN': [
        '电子邮箱', '项目 ID', '到期时间', '以下是所选凭据当前保存的完整内容。', '凭据摘要', '凭据内容', '提供商',
        '可用模型', '复制模型 ID', '以下模型是该凭据目前可用的模型。', '模型 ID', '筛选模型', '筛选可用模型',
        '没有符合筛选条件的模型。', '无法加载可用模型。', '无法获取凭据信息。', '模型测试', '该凭据目前没有可用模型。',
        '选择一个模型，使用 {provider} 凭据{account}进行测试。系统只会向提供商发送一条最小生成请求。', '模型', '选择模型',
        '测试', '不可用', '月度额度', '每周用量', '账户', '凭据', '额度来源', 'Grok Build 账户账单', '计费周期',
        '最低剩余额度', '已使用 {used} / {limit} 点额度', '已使用 {value}%', '剩余 {value}%',
        '以下是 Grok Build 为所选 OAuth 凭据报告的账户额度。', '额度摘要', '套餐', '用量周期', '未知',
        '速率限制重置点数', '标准限制', '代码审查限制', '已达到', '可用', '用量限制',
        '以下是 Codex 为所选 OAuth 凭据报告的账户速率限制。', '已跟踪模型', '平均剩余额度',
        '该凭据暂时没有可用的额度信息。', '所选凭据的额度按模型分组显示。', '模型额度', '无额度信息',
        '平均额度：{quota}，共 {count} 个模型。', '账户最低额度：{quota}，共 {count} 个有效计费周期。',
        '当前计费周期的账户额度：{quota}。', '账户最低额度：{quota}，共 {count} 个用量周期。',
        '当前用量周期的账户额度：{quota}。', '状态', '类型', '原因', '已记录错误', '该凭据没有已记录的提供商错误。',
        '错误摘要', '以下是该凭据最近记录的提供商错误。'
    ],
    'zh-TW': [
        '電子郵件', '專案 ID', '到期時間', '以下是所選憑證目前儲存的完整內容。', '憑證摘要', '憑證內容', '供應商',
        '可用模型', '複製模型 ID', '以下模型是此憑證目前可用的模型。', '模型 ID', '篩選模型', '篩選可用模型',
        '沒有符合篩選條件的模型。', '無法載入可用模型。', '無法取得憑證資訊。', '模型測試', '此憑證目前沒有可用模型。',
        '選擇一個模型，使用 {provider} 憑證{account}進行測試。系統只會向供應商傳送最小的生成請求。', '模型', '選擇模型',
        '測試', '無法使用', '每月額度', '每週用量', '帳戶', '憑證', '額度來源', 'Grok Build 帳戶帳單', '計費週期',
        '最低剩餘額度', '已使用 {used} / {limit} 點額度', '已使用 {value}%', '剩餘 {value}%',
        '以下是 Grok Build 為所選 OAuth 憑證回報的帳戶額度。', '額度摘要', '方案', '用量週期', '未知',
        '速率限制重設點數', '標準限制', '程式碼審查限制', '已達上限', '可用', '用量限制',
        '以下是 Codex 為所選 OAuth 憑證回報的帳戶速率限制。', '追蹤中的模型', '平均剩餘額度',
        '此憑證目前沒有可用的額度資訊。', '所選憑證的額度依模型分組顯示。', '模型額度', '無額度資訊',
        '平均額度：{quota}，共 {count} 個模型。', '帳戶最低額度：{quota}，共 {count} 個有效計費週期。',
        '目前計費週期的帳戶額度：{quota}。', '帳戶最低額度：{quota}，共 {count} 個用量週期。',
        '目前用量週期的帳戶額度：{quota}。', '狀態', '類型', '原因', '已記錄錯誤', '此憑證沒有已記錄的供應商錯誤。',
        '錯誤摘要', '以下是此憑證最近記錄的供應商錯誤。'
    ],
    de: [
        'E-Mail', 'Projekt-ID', 'Ablaufdatum', 'Dies ist der gespeicherte Inhalt des ausgewählten Zugangs.',
        'Zugangsdatenübersicht', 'Gespeicherter Inhalt', 'Anbieter', 'Verfügbare Modelle', 'Modell-ID kopieren',
        'Diese Modelle sind derzeit mit diesem Zugang verfügbar.', 'Modell-IDs', 'Modelle filtern', 'Verfügbare Modelle filtern',
        'Keine Modelle entsprechen diesem Filter.', 'Die verfügbaren Modelle konnten nicht geladen werden.',
        'Die Zugangsdaten sind nicht verfügbar.', 'Modelltest', 'Für diesen Zugang sind derzeit keine Modelle verfügbar.',
        'Wählen Sie ein Modell aus, um den {provider}-Zugang{account} zu testen. Dabei wird eine minimale Generierungsanfrage an den Anbieter gesendet.',
        'Modell', 'Modell auswählen', 'Testen', 'Nicht verfügbar', 'Monatliches Guthaben', 'Wöchentliche Nutzung',
        'Konto', 'Zugang', 'Kontingentquelle', 'Grok Build-Kontoabrechnung', 'Abrechnungszeiträume',
        'Niedrigstes Restkontingent', '{used} von {limit} Guthaben verbraucht', '{value}% verbraucht', '{value}% verfügbar',
        'Von Grok Build gemeldetes Kontingent für den ausgewählten OAuth-Zugang.', 'Kontingentübersicht', 'Tarif',
        'Nutzungszeiträume', 'Unbekannt', 'Guthaben zum Zurücksetzen des Ratenlimits', 'Standardlimit',
        'Limit für Code-Reviews', 'Erreicht', 'Verfügbar', 'Nutzungslimit',
        'Von Codex gemeldete Kontolimits für den ausgewählten OAuth-Zugang.', 'Erfasste Modelle',
        'Durchschnittliches Restkontingent', 'Für diesen Zugang liegen noch keine Kontingentdaten vor.',
        'Die Kontingentnutzung des ausgewählten Zugangs ist nach Modell gruppiert.', 'Modellkontingent', 'Kein Kontingent',
        'Durchschnittliches Kontingent: {quota} über {count} Modelle.', 'Niedrigstes Kontokontingent: {quota} über {count} aktive Abrechnungszeiträume.',
        'Kontokontingent im aktiven Abrechnungszeitraum: {quota}.', 'Niedrigstes Kontokontingent: {quota} über {count} Nutzungszeiträume.',
        'Kontokontingent im aktiven Nutzungszeitraum: {quota}.', 'Status', 'Typ', 'Grund', 'Gespeicherte Fehler',
        'Für diesen Zugang sind keine Anbieterfehler gespeichert.', 'Fehlerübersicht',
        'Dies sind die zuletzt für diesen Zugang gespeicherten Anbieterfehler.'
    ],
    es: [
        'Correo electrónico', 'ID del proyecto', 'Caducidad', 'Este es el contenido guardado de la credencial seleccionada.',
        'Resumen de la credencial', 'Contenido de la credencial', 'Proveedor', 'Modelos disponibles', 'Copiar ID del modelo',
        'Estos son los modelos que la credencial tiene disponibles actualmente.', 'ID de modelos', 'Filtrar modelos',
        'Filtrar modelos disponibles', 'Ningún modelo coincide con el filtro.', 'No se pudieron cargar los modelos disponibles.',
        'La información de la credencial no está disponible.', 'Prueba de modelo', 'Esta credencial no tiene modelos disponibles actualmente.',
        'Selecciona un modelo para probar la credencial de {provider}{account}. La prueba envía una solicitud mínima de generación al proveedor.',
        'Modelo', 'Selecciona un modelo', 'Probar', 'No disponible', 'Créditos mensuales', 'Uso semanal', 'Cuenta',
        'Credencial', 'Origen de la cuota', 'Facturación de la cuenta de Grok Build', 'Periodos de facturación',
        'Cuota mínima restante', '{used} de {limit} créditos utilizados', '{value}% utilizado', '{value}% disponible',
        'Cuota de cuenta comunicada por Grok Build para la credencial OAuth seleccionada.', 'Resumen de cuota', 'Plan',
        'Periodos de uso', 'Desconocido', 'Créditos para restablecer el límite', 'Límite estándar',
        'Límite de revisión de código', 'Alcanzado', 'Disponible', 'Límite de uso',
        'Límites de cuenta comunicados por Codex para la credencial OAuth seleccionada.', 'Modelos supervisados',
        'Cuota media restante', 'Todavía no hay información de cuota para esta credencial.',
        'El uso de cuota de la credencial seleccionada se agrupa por modelo.', 'Cuota por modelo', 'Sin cuota',
        'Cuota media: {quota} en {count} modelos.', 'Cuota mínima de la cuenta: {quota} en {count} periodos de facturación activos.',
        'Cuota de la cuenta en el periodo de facturación activo: {quota}.', 'Cuota mínima de la cuenta: {quota} en {count} periodos de uso.',
        'Cuota de la cuenta en el periodo de uso activo: {quota}.', 'Estado', 'Tipo', 'Motivo', 'Errores guardados',
        'Esta credencial no tiene errores de proveedor guardados.', 'Resumen de errores',
        'Estos son los últimos errores del proveedor registrados para esta credencial.'
    ],
    fr: [
        'Adresse e-mail', 'ID du projet', 'Expiration', 'Voici le contenu enregistré pour l’identifiant sélectionné.',
        'Résumé de l’identifiant', 'Contenu de l’identifiant', 'Fournisseur', 'Modèles disponibles', 'Copier l’ID du modèle',
        'Ces modèles sont actuellement disponibles avec cet identifiant.', 'ID des modèles', 'Filtrer les modèles',
        'Filtrer les modèles disponibles', 'Aucun modèle ne correspond à ce filtre.', 'Impossible de charger les modèles disponibles.',
        'Les informations de l’identifiant ne sont pas disponibles.', 'Test du modèle', 'Aucun modèle n’est actuellement disponible avec cet identifiant.',
        'Sélectionnez un modèle pour tester l’identifiant {provider}{account}. Le test envoie une requête de génération minimale au fournisseur.',
        'Modèle', 'Sélectionner un modèle', 'Tester', 'Indisponible', 'Crédits mensuels', 'Utilisation hebdomadaire',
        'Compte', 'Identifiant', 'Source du quota', 'Facturation du compte Grok Build', 'Périodes de facturation',
        'Quota restant le plus faible', '{used} crédits utilisés sur {limit}', '{value} % utilisés', '{value} % restants',
        'Quota de compte communiqué par Grok Build pour l’identifiant OAuth sélectionné.', 'Résumé du quota', 'Forfait',
        'Périodes d’utilisation', 'Inconnu', 'Crédits de réinitialisation de limite', 'Limite standard',
        'Limite de revue de code', 'Atteinte', 'Disponible', 'Limite d’utilisation',
        'Limites de compte communiquées par Codex pour l’identifiant OAuth sélectionné.', 'Modèles suivis',
        'Quota restant moyen', 'Aucune information de quota n’est encore disponible pour cet identifiant.',
        'L’utilisation du quota de l’identifiant sélectionné est regroupée par modèle.', 'Quota par modèle', 'Aucun quota',
        'Quota moyen : {quota} sur {count} modèles.', 'Quota de compte le plus faible : {quota} sur {count} périodes de facturation actives.',
        'Quota du compte pour la période de facturation active : {quota}.', 'Quota de compte le plus faible : {quota} sur {count} périodes d’utilisation.',
        'Quota du compte pour la période d’utilisation active : {quota}.', 'État', 'Type', 'Motif', 'Erreurs enregistrées',
        'Aucune erreur de fournisseur n’est enregistrée pour cet identifiant.', 'Résumé des erreurs',
        'Voici les dernières erreurs de fournisseur enregistrées pour cet identifiant.'
    ],
    id: [
        'Email', 'ID proyek', 'Kedaluwarsa', 'Berikut isi tersimpan untuk kredensial yang dipilih.', 'Ringkasan Kredensial',
        'Isi Kredensial', 'Penyedia', 'Model tersedia', 'Salin ID model', 'Model berikut saat ini tersedia untuk kredensial ini.',
        'ID Model', 'Filter model', 'Filter model yang tersedia', 'Tidak ada model yang sesuai dengan filter.',
        'Model yang tersedia tidak dapat dimuat.', 'Informasi kredensial tidak tersedia.', 'Pengujian Model',
        'Saat ini tidak ada model yang tersedia untuk kredensial ini.',
        'Pilih model untuk menguji kredensial {provider}{account}. Pengujian mengirim permintaan pembuatan minimal ke penyedia.',
        'Model', 'Pilih model', 'Uji', 'Tidak tersedia', 'Kredit Bulanan', 'Penggunaan Mingguan', 'Akun', 'Kredensial',
        'Sumber kuota', 'Tagihan akun Grok Build', 'Periode tagihan', 'Sisa kuota terendah',
        '{used} dari {limit} kredit digunakan', '{value}% digunakan', '{value}% tersisa',
        'Kuota akun yang dilaporkan Grok Build untuk kredensial OAuth yang dipilih.', 'Ringkasan Kuota', 'Paket',
        'Jendela penggunaan', 'Tidak diketahui', 'Kredit reset batas laju', 'Batas standar', 'Batas tinjauan kode',
        'Tercapai', 'Tersedia', 'Batas Penggunaan',
        'Batas akun yang dilaporkan Codex untuk kredensial OAuth yang dipilih.', 'Model yang dipantau', 'Rata-rata sisa kuota',
        'Informasi kuota untuk kredensial ini belum tersedia.', 'Penggunaan kuota kredensial yang dipilih dikelompokkan berdasarkan model.',
        'Kuota Model', 'Tidak ada kuota', 'Kuota rata-rata: {quota} pada {count} model.',
        'Kuota akun terendah: {quota} pada {count} periode tagihan aktif.', 'Kuota akun pada periode tagihan aktif: {quota}.',
        'Kuota akun terendah: {quota} pada {count} jendela penggunaan.', 'Kuota akun pada jendela penggunaan aktif: {quota}.',
        'Status', 'Jenis', 'Alasan', 'Kesalahan tersimpan', 'Kredensial ini tidak memiliki kesalahan penyedia yang tersimpan.',
        'Ringkasan Kesalahan', 'Berikut kesalahan penyedia terbaru yang tercatat untuk kredensial ini.'
    ],
    it: [
        'Email', 'ID progetto', 'Scadenza', 'Questo è il contenuto salvato della credenziale selezionata.',
        'Riepilogo credenziale', 'Contenuto credenziale', 'Provider', 'Modelli disponibili', 'Copia ID modello',
        'Questi modelli risultano attualmente disponibili per la credenziale.', 'ID modelli', 'Filtra modelli',
        'Filtra i modelli disponibili', 'Nessun modello corrisponde al filtro.', 'Impossibile caricare i modelli disponibili.',
        'Le informazioni della credenziale non sono disponibili.', 'Test del modello', 'Nessun modello è attualmente disponibile per questa credenziale.',
        'Seleziona un modello per testare la credenziale {provider}{account}. Il test invia una richiesta minima di generazione al provider.',
        'Modello', 'Seleziona un modello', 'Testa', 'Non disponibile', 'Crediti mensili', 'Utilizzo settimanale',
        'Account', 'Credenziale', 'Origine quota', 'Fatturazione account Grok Build', 'Periodi di fatturazione',
        'Quota residua minima', '{used} crediti utilizzati su {limit}', '{value}% utilizzato', '{value}% residuo',
        'Quota account comunicata da Grok Build per la credenziale OAuth selezionata.', 'Riepilogo quota', 'Piano',
        'Finestre di utilizzo', 'Sconosciuto', 'Crediti di ripristino del limite', 'Limite standard',
        'Limite revisione codice', 'Raggiunto', 'Disponibile', 'Limite di utilizzo',
        'Limiti account comunicati da Codex per la credenziale OAuth selezionata.', 'Modelli monitorati',
        'Quota residua media', 'Non sono ancora disponibili informazioni sulla quota per questa credenziale.',
        'L’utilizzo della quota della credenziale selezionata è raggruppato per modello.', 'Quota per modello', 'Nessuna quota',
        'Quota media: {quota} su {count} modelli.', 'Quota account minima: {quota} su {count} periodi di fatturazione attivi.',
        'Quota account nel periodo di fatturazione attivo: {quota}.', 'Quota account minima: {quota} su {count} finestre di utilizzo.',
        'Quota account nella finestra di utilizzo attiva: {quota}.', 'Stato', 'Tipo', 'Motivo', 'Errori salvati',
        'Questa credenziale non contiene errori del provider registrati.', 'Riepilogo errori',
        'Questi sono gli ultimi errori del provider registrati per la credenziale.'
    ],
    ja: [
        'メールアドレス', 'プロジェクト ID', '有効期限', '選択した認証情報に保存されている内容です。', '認証情報の概要',
        '認証情報の内容', 'プロバイダー', '利用可能なモデル', 'モデル ID をコピー', 'この認証情報で現在利用可能と報告されているモデルです。',
        'モデル ID', 'モデルを絞り込む', '利用可能なモデルを絞り込む', '条件に一致するモデルはありません。',
        '利用可能なモデルを読み込めませんでした。', '認証情報を取得できません。', 'モデルテスト',
        'この認証情報で現在利用できるモデルはありません。',
        '{provider} の認証情報{account}でテストするモデルを選択してください。プロバイダーには最小限の生成リクエストだけが送信されます。',
        'モデル', 'モデルを選択', 'テスト', '利用不可', '月間クレジット', '週間使用量', 'アカウント', '認証情報',
        '割り当ての取得元', 'Grok Build アカウント請求', '請求期間', '最小残量', '{limit} クレジット中 {used} を使用',
        '{value}% 使用', '残り {value}%', '選択した OAuth 認証情報について Grok Build が報告したアカウント割り当てです。',
        '割り当ての概要', 'プラン', '使用期間', '不明', 'レート制限リセット用クレジット', '標準上限',
        'コードレビュー上限', '上限到達', '利用可能', '使用上限',
        '選択した OAuth 認証情報について Codex が報告したアカウント制限です。', '追跡中のモデル', '平均残量',
        'この認証情報の割り当て情報はまだありません。', '選択した認証情報の使用量をモデル別に表示しています。',
        'モデル別割り当て', '割り当てなし', '平均割り当て：{count} モデルで {quota}。',
        'アカウントの最小割り当て：有効な {count} 請求期間で {quota}。', '現在の請求期間のアカウント割り当て：{quota}。',
        'アカウントの最小割り当て：{count} 使用期間で {quota}。', '現在の使用期間のアカウント割り当て：{quota}。',
        'ステータス', '種類', '理由', '記録済みエラー', 'この認証情報にはプロバイダーエラーが記録されていません。',
        'エラー概要', 'この認証情報に記録された最新のプロバイダーエラーです。'
    ],
    ko: [
        '이메일', '프로젝트 ID', '만료 시각', '선택한 자격 증명에 저장된 내용입니다.', '자격 증명 요약', '자격 증명 내용',
        '공급자', '사용 가능한 모델', '모델 ID 복사', '현재 이 자격 증명으로 사용할 수 있다고 보고된 모델입니다.',
        '모델 ID', '모델 필터', '사용 가능한 모델 필터', '필터와 일치하는 모델이 없습니다.', '사용 가능한 모델을 불러오지 못했습니다.',
        '자격 증명 정보를 확인할 수 없습니다.', '모델 테스트', '현재 이 자격 증명으로 사용할 수 있는 모델이 없습니다.',
        '{provider} 자격 증명{account}으로 테스트할 모델을 선택하세요. 공급자에는 최소 생성 요청만 전송됩니다.',
        '모델', '모델 선택', '테스트', '사용 불가', '월간 크레딧', '주간 사용량', '계정', '자격 증명',
        '할당량 출처', 'Grok Build 계정 청구', '청구 기간', '가장 낮은 잔여 할당량', '{limit} 크레딧 중 {used} 사용',
        '{value}% 사용', '{value}% 남음', '선택한 OAuth 자격 증명에 대해 Grok Build가 보고한 계정 할당량입니다.',
        '할당량 요약', '플랜', '사용 기간', '알 수 없음', '속도 제한 재설정 크레딧', '표준 제한',
        '코드 리뷰 제한', '한도 도달', '사용 가능', '사용 제한',
        '선택한 OAuth 자격 증명에 대해 Codex가 보고한 계정 제한입니다.', '추적 중인 모델', '평균 잔여 할당량',
        '이 자격 증명의 할당량 정보가 아직 없습니다.', '선택한 자격 증명의 할당량 사용량을 모델별로 표시합니다.',
        '모델 할당량', '할당량 없음', '평균 할당량: {count}개 모델에서 {quota}.',
        '최저 계정 할당량: 활성 청구 기간 {count}개에서 {quota}.', '현재 청구 기간의 계정 할당량: {quota}.',
        '최저 계정 할당량: 사용 기간 {count}개에서 {quota}.', '현재 사용 기간의 계정 할당량: {quota}.',
        '상태', '유형', '사유', '저장된 오류', '이 자격 증명에는 저장된 공급자 오류가 없습니다.',
        '오류 요약', '이 자격 증명에 최근 기록된 공급자 오류입니다.'
    ],
    pt: [
        'E-mail', 'ID do projeto', 'Expiração', 'Este é o conteúdo armazenado da credencial selecionada.',
        'Resumo da credencial', 'Conteúdo da credencial', 'Provedor', 'Modelos disponíveis', 'Copiar ID do modelo',
        'Estes modelos estão disponíveis no momento para esta credencial.', 'IDs dos modelos', 'Filtrar modelos',
        'Filtrar modelos disponíveis', 'Nenhum modelo corresponde ao filtro.', 'Não foi possível carregar os modelos disponíveis.',
        'As informações da credencial não estão disponíveis.', 'Teste do modelo', 'Nenhum modelo está disponível no momento para esta credencial.',
        'Selecione um modelo para testar a credencial de {provider}{account}. O teste envia uma solicitação mínima de geração ao provedor.',
        'Modelo', 'Selecione um modelo', 'Testar', 'Indisponível', 'Créditos mensais', 'Uso semanal', 'Conta',
        'Credencial', 'Fonte da cota', 'Faturamento da conta Grok Build', 'Períodos de faturamento',
        'Menor cota restante', '{used} de {limit} créditos utilizados', '{value}% utilizado', '{value}% restante',
        'Cota da conta informada pelo Grok Build para a credencial OAuth selecionada.', 'Resumo da cota', 'Plano',
        'Janelas de uso', 'Desconhecido', 'Créditos para redefinir o limite', 'Limite padrão',
        'Limite de revisão de código', 'Atingido', 'Disponível', 'Limite de uso',
        'Limites da conta informados pelo Codex para a credencial OAuth selecionada.', 'Modelos monitorados',
        'Cota média restante', 'Ainda não há informações de cota para esta credencial.',
        'O uso da cota da credencial selecionada está agrupado por modelo.', 'Cota por modelo', 'Sem cota',
        'Cota média: {quota} em {count} modelos.', 'Menor cota da conta: {quota} em {count} períodos de faturamento ativos.',
        'Cota da conta no período de faturamento ativo: {quota}.', 'Menor cota da conta: {quota} em {count} janelas de uso.',
        'Cota da conta na janela de uso ativa: {quota}.', 'Status', 'Tipo', 'Motivo', 'Erros armazenados',
        'Esta credencial não tem erros de provedor armazenados.', 'Resumo dos erros',
        'Estes são os erros de provedor mais recentes registrados para esta credencial.'
    ],
    ru: [
        'Электронная почта', 'ID проекта', 'Срок действия', 'Это сохранённое содержимое выбранных учётных данных.',
        'Сводка по учётным данным', 'Содержимое учётных данных', 'Провайдер', 'Доступные модели', 'Копировать ID модели',
        'Эти модели сейчас доступны с выбранными учётными данными.', 'ID моделей', 'Фильтр моделей',
        'Фильтр доступных моделей', 'Нет моделей, соответствующих фильтру.', 'Не удалось загрузить доступные модели.',
        'Информация об учётных данных недоступна.', 'Проверка модели', 'Для этих учётных данных сейчас нет доступных моделей.',
        'Выберите модель для проверки учётных данных {provider}{account}. Провайдеру будет отправлен минимальный запрос на генерацию.',
        'Модель', 'Выберите модель', 'Проверить', 'Недоступно', 'Месячные кредиты', 'Недельное использование',
        'Учётная запись', 'Учётные данные', 'Источник квоты', 'Биллинг учётной записи Grok Build', 'Расчётные периоды',
        'Минимальный остаток квоты', 'Использовано {used} из {limit} кредитов', 'Использовано {value}%', 'Осталось {value}%',
        'Квота учётной записи от Grok Build для выбранных учётных данных OAuth.', 'Сводка по квоте', 'Тариф',
        'Периоды использования', 'Неизвестно', 'Кредиты сброса ограничения', 'Стандартное ограничение',
        'Ограничение на проверку кода', 'Достигнуто', 'Доступно', 'Ограничение использования',
        'Ограничения учётной записи от Codex для выбранных учётных данных OAuth.', 'Отслеживаемые модели',
        'Средний остаток квоты', 'Для этих учётных данных пока нет информации о квоте.',
        'Использование квоты выбранных учётных данных сгруппировано по моделям.', 'Квота моделей', 'Нет квоты',
        'Средняя квота: {quota} для {count} моделей.', 'Минимальная квота учётной записи: {quota} за {count} активных расчётных периодов.',
        'Квота учётной записи за активный расчётный период: {quota}.', 'Минимальная квота учётной записи: {quota} за {count} периодов использования.',
        'Квота учётной записи за активный период использования: {quota}.', 'Статус', 'Тип', 'Причина', 'Сохранённые ошибки',
        'Для этих учётных данных нет сохранённых ошибок провайдера.', 'Сводка ошибок',
        'Последние ошибки провайдера, зарегистрированные для этих учётных данных.'
    ],
    th: [
        'อีเมล', 'รหัสโปรเจกต์', 'วันหมดอายุ', 'นี่คือข้อมูลที่บันทึกไว้ของข้อมูลรับรองที่เลือก', 'สรุปข้อมูลรับรอง',
        'ข้อมูลที่บันทึกไว้', 'ผู้ให้บริการ', 'โมเดลที่ใช้ได้', 'คัดลอกรหัสโมเดล', 'โมเดลเหล่านี้พร้อมใช้งานกับข้อมูลรับรองนี้ในขณะนี้',
        'รหัสโมเดล', 'กรองโมเดล', 'กรองโมเดลที่ใช้ได้', 'ไม่มีโมเดลที่ตรงกับตัวกรอง', 'ไม่สามารถโหลดโมเดลที่ใช้ได้',
        'ไม่มีข้อมูลของข้อมูลรับรอง', 'ทดสอบโมเดล', 'ขณะนี้ไม่มีโมเดลที่ใช้ได้กับข้อมูลรับรองนี้',
        'เลือกโมเดลเพื่อทดสอบข้อมูลรับรอง {provider}{account} ระบบจะส่งคำขอสร้างเนื้อหาขนาดเล็กที่สุดไปยังผู้ให้บริการ',
        'โมเดล', 'เลือกโมเดล', 'ทดสอบ', 'ใช้ไม่ได้', 'เครดิตรายเดือน', 'การใช้งานรายสัปดาห์', 'บัญชี',
        'ข้อมูลรับรอง', 'แหล่งข้อมูลโควตา', 'การเรียกเก็บเงินบัญชี Grok Build', 'รอบเรียกเก็บเงิน',
        'โควตาคงเหลือต่ำสุด', 'ใช้เครดิต {used} จาก {limit}', 'ใช้แล้ว {value}%', 'เหลือ {value}%',
        'โควตาบัญชีที่ Grok Build รายงานสำหรับข้อมูลรับรอง OAuth ที่เลือก', 'สรุปโควตา', 'แพ็กเกจ',
        'ช่วงการใช้งาน', 'ไม่ทราบ', 'เครดิตรีเซ็ตขีดจำกัดอัตรา', 'ขีดจำกัดมาตรฐาน', 'ขีดจำกัดการตรวจโค้ด',
        'ถึงขีดจำกัดแล้ว', 'ใช้ได้', 'ขีดจำกัดการใช้งาน', 'ขีดจำกัดบัญชีที่ Codex รายงานสำหรับข้อมูลรับรอง OAuth ที่เลือก',
        'โมเดลที่ติดตาม', 'โควตาคงเหลือเฉลี่ย', 'ยังไม่มีข้อมูลโควตาสำหรับข้อมูลรับรองนี้',
        'การใช้โควตาของข้อมูลรับรองที่เลือกจะแสดงแยกตามโมเดล', 'โควตาโมเดล', 'ไม่มีข้อมูลโควตา',
        'โควตาเฉลี่ย: {quota} จาก {count} โมเดล', 'โควตาบัญชีต่ำสุด: {quota} จากรอบเรียกเก็บเงินที่ใช้งานอยู่ {count} รอบ',
        'โควตาบัญชีในรอบเรียกเก็บเงินปัจจุบัน: {quota}', 'โควตาบัญชีต่ำสุด: {quota} จากช่วงการใช้งาน {count} ช่วง',
        'โควตาบัญชีในช่วงการใช้งานปัจจุบัน: {quota}', 'สถานะ', 'ประเภท', 'สาเหตุ', 'ข้อผิดพลาดที่บันทึกไว้',
        'ข้อมูลรับรองนี้ไม่มีข้อผิดพลาดจากผู้ให้บริการที่บันทึกไว้', 'สรุปข้อผิดพลาด',
        'ข้อผิดพลาดล่าสุดจากผู้ให้บริการที่บันทึกไว้สำหรับข้อมูลรับรองนี้'
    ],
    tr: [
        'E-posta', 'Proje kimliği', 'Bitiş zamanı', 'Seçilen kimlik bilgisinin saklanan içeriği.', 'Kimlik Bilgisi Özeti',
        'Kimlik Bilgisi İçeriği', 'Sağlayıcı', 'Kullanılabilir modeller', 'Model kimliğini kopyala',
        'Bu modeller şu anda bu kimlik bilgisiyle kullanılabilir olarak bildiriliyor.', 'Model Kimlikleri', 'Modelleri filtrele',
        'Kullanılabilir modelleri filtrele', 'Filtreyle eşleşen model yok.', 'Kullanılabilir modeller yüklenemedi.',
        'Kimlik bilgisi ayrıntıları kullanılamıyor.', 'Model Testi', 'Bu kimlik bilgisi için şu anda kullanılabilir model yok.',
        '{provider} kimlik bilgisini{account} test etmek için bir model seçin. Sağlayıcıya yalnızca en küçük üretim isteği gönderilir.',
        'Model', 'Model seçin', 'Test et', 'Kullanılamıyor', 'Aylık Krediler', 'Haftalık Kullanım', 'Hesap',
        'Kimlik bilgisi', 'Kota kaynağı', 'Grok Build hesap faturalandırması', 'Faturalandırma dönemleri',
        'En düşük kalan kota', '{limit} kredinin {used} kadarı kullanıldı', '%{value} kullanıldı', '%{value} kaldı',
        'Seçilen OAuth kimlik bilgisi için Grok Build tarafından bildirilen hesap kotası.', 'Kota Özeti', 'Plan',
        'Kullanım dönemleri', 'Bilinmiyor', 'Hız sınırı sıfırlama kredileri', 'Standart sınır',
        'Kod inceleme sınırı', 'Sınıra ulaşıldı', 'Kullanılabilir', 'Kullanım Sınırı',
        'Seçilen OAuth kimlik bilgisi için Codex tarafından bildirilen hesap sınırları.', 'İzlenen modeller',
        'Ortalama kalan kota', 'Bu kimlik bilgisi için henüz kota bilgisi yok.',
        'Seçilen kimlik bilgisinin kota kullanımı modele göre gruplandırılır.', 'Model Kotası', 'Kota yok',
        'Ortalama kota: {count} modelde {quota}.', 'En düşük hesap kotası: {count} etkin faturalandırma döneminde {quota}.',
        'Etkin faturalandırma dönemindeki hesap kotası: {quota}.', 'En düşük hesap kotası: {count} kullanım döneminde {quota}.',
        'Etkin kullanım dönemindeki hesap kotası: {quota}.', 'Durum', 'Tür', 'Neden', 'Saklanan hatalar',
        'Bu kimlik bilgisi için saklanan sağlayıcı hatası yok.', 'Hata Özeti',
        'Bu kimlik bilgisi için kaydedilen en son sağlayıcı hataları.'
    ],
    vi: [
        'Email', 'Mã dự án', 'Thời hạn', 'Đây là nội dung đang được lưu của thông tin xác thực đã chọn.',
        'Tóm tắt thông tin xác thực', 'Nội dung thông tin xác thực', 'Nhà cung cấp', 'Mô hình khả dụng',
        'Sao chép mã mô hình', 'Đây là các mô hình hiện được ghi nhận là khả dụng với thông tin xác thực này.',
        'Mã mô hình', 'Lọc mô hình', 'Lọc các mô hình khả dụng', 'Không có mô hình nào khớp với bộ lọc.',
        'Không thể tải các mô hình khả dụng.', 'Không có thông tin của thông tin xác thực.', 'Kiểm tra mô hình',
        'Thông tin xác thực này hiện không có mô hình khả dụng.',
        'Chọn một mô hình để kiểm tra thông tin xác thực {provider}{account}. Hệ thống chỉ gửi một yêu cầu tạo nội dung tối thiểu đến nhà cung cấp.',
        'Mô hình', 'Chọn mô hình', 'Kiểm tra', 'Không khả dụng', 'Tín dụng theo tháng', 'Mức dùng theo tuần',
        'Tài khoản', 'Thông tin xác thực', 'Nguồn hạn mức', 'Thanh toán tài khoản Grok Build', 'Chu kỳ thanh toán',
        'Hạn mức còn lại thấp nhất', 'Đã dùng {used} / {limit} tín dụng', 'Đã dùng {value}%', 'Còn {value}%',
        'Hạn mức tài khoản do Grok Build báo cáo cho thông tin xác thực OAuth đã chọn.', 'Tóm tắt hạn mức', 'Gói',
        'Chu kỳ sử dụng', 'Không xác định', 'Tín dụng đặt lại giới hạn tốc độ', 'Giới hạn tiêu chuẩn',
        'Giới hạn đánh giá mã', 'Đã đạt giới hạn', 'Khả dụng', 'Giới hạn sử dụng',
        'Giới hạn tài khoản do Codex báo cáo cho thông tin xác thực OAuth đã chọn.', 'Mô hình được theo dõi',
        'Hạn mức trung bình còn lại', 'Chưa có thông tin hạn mức cho thông tin xác thực này.',
        'Mức sử dụng hạn mức của thông tin xác thực đã chọn được nhóm theo mô hình.', 'Hạn mức theo mô hình', 'Không có hạn mức',
        'Hạn mức trung bình: {quota} trên {count} mô hình.', 'Hạn mức tài khoản thấp nhất: {quota} trên {count} chu kỳ thanh toán đang hoạt động.',
        'Hạn mức tài khoản trong chu kỳ thanh toán hiện tại: {quota}.', 'Hạn mức tài khoản thấp nhất: {quota} trên {count} chu kỳ sử dụng.',
        'Hạn mức tài khoản trong chu kỳ sử dụng hiện tại: {quota}.', 'Trạng thái', 'Loại', 'Lý do',
        'Lỗi đã ghi nhận', 'Thông tin xác thực này không có lỗi nhà cung cấp nào được ghi nhận.', 'Tóm tắt lỗi',
        'Đây là các lỗi nhà cung cấp gần nhất được ghi nhận cho thông tin xác thực này.'
    ]
};

for (const [locale, values] of Object.entries(CREDENTIAL_MODAL_VALUES)) {
    if (values.length !== CREDENTIAL_MODAL_KEYS.length) {
        throw new Error(`Invalid credential modal catalog for ${locale}.`);
    }
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], Object.fromEntries(CREDENTIAL_MODAL_KEYS.map((key, index) => [key, values[index]])));
}

const PROVIDER_AUTHORIZATION_KEYS = [
    'provider.authorization_code',
    'provider.authorization_code_placeholder',
];

const PROVIDER_AUTHORIZATION_COPY = {
    en: ['Authorization code', 'Paste the Grok Build authorization code'],
    'zh-CN': ['授权码', '粘贴 Grok Build 提供的授权码'],
    'zh-TW': ['授權碼', '貼上 Grok Build 提供的授權碼'],
    de: ['Autorisierungscode', 'Fügen Sie den Autorisierungscode von Grok Build ein'],
    es: ['Código de autorización', 'Pega el código de autorización de Grok Build'],
    fr: ['Code d’autorisation', 'Collez le code d’autorisation fourni par Grok Build'],
    id: ['Kode otorisasi', 'Tempel kode otorisasi dari Grok Build'],
    it: ['Codice di autorizzazione', 'Incolla il codice di autorizzazione fornito da Grok Build'],
    ja: ['認証コード', 'Grok Build に表示された認証コードを貼り付けてください'],
    ko: ['인증 코드', 'Grok Build에서 제공한 인증 코드를 붙여 넣으세요'],
    pt: ['Código de autorização', 'Cole o código de autorização fornecido pelo Grok Build'],
    ru: ['Код авторизации', 'Вставьте код авторизации, предоставленный Grok Build'],
    th: ['รหัสอนุญาต', 'วางรหัสอนุญาตที่ Grok Build แสดง'],
    tr: ['Yetkilendirme kodu', 'Grok Build tarafından verilen yetkilendirme kodunu yapıştırın'],
    vi: ['Mã cấp quyền', 'Dán mã cấp quyền do Grok Build cung cấp'],
};

for (const [locale, values] of Object.entries(PROVIDER_AUTHORIZATION_COPY)) {
    Object.assign(
        PAGE_LOCALE_TRANSLATIONS[locale],
        Object.fromEntries(PROVIDER_AUTHORIZATION_KEYS.map((key, index) => [key, values[index]])),
    );
}

const DASHBOARD_METRICS_ENHANCEMENT_KEYS = [
    'dashboard.health_matrix_title', 'dashboard.health_matrix_description',
    'dashboard.status_healthy', 'dashboard.status_idle', 'dashboard.status_issues',
    'dashboard.status_cooldown', 'dashboard.status_degraded',
    'dashboard.token_distribution_title', 'dashboard.token_distribution_description',
    'dashboard.input_tokens', 'dashboard.output_tokens', 'dashboard.cached_tokens', 'dashboard.reasoning_tokens',
    'dashboard.timeline_traffic', 'dashboard.peak', 'now'
];

const DASHBOARD_METRICS_ENHANCEMENT_COPY = {
    en: [
        'Provider Health & Status Matrix', 'Real-time status, active credentials, and traffic health across all supported AI providers.',
        'Operational', 'Idle / Ready', 'Issues / Cooldown',
        'In Cooldown', 'Degraded (<60%)',
        'Token Consumption & Traffic Distribution', 'Visual breakdown of input, output, cached, and reasoning tokens with estimated cost savings.',
        'Input', 'Output', 'Cached', 'Reasoning',
        'Hourly Traffic Volume', 'Peak', 'Now'
    ],
    'zh-CN': [
        '提供商健康状态矩阵', '各 AI 提供商的实时状态、有效凭据与流量健康度。',
        '正常运行', '就绪 / 空闲', '异常 / 冷却中',
        '冷却中', '性能下降 (<60%)',
        '令牌消耗与流量分布', '直观展示输入、输出、缓存及推理令牌以及预估成本节约。',
        '输入', '输出', '缓存', '推理',
        '每小时流量分布', '峰值', '现在'
    ],
    'zh-TW': [
        '供應商健康狀態矩陣', '各 AI 供應商的即時狀態、有效憑證與流量健康度。',
        '正常運作', '就緒 / 閒置', '異常 / 冷卻中',
        '冷卻中', '效能下降 (<60%)',
        '權杖消耗與流量分佈', '直觀展示輸入、輸出、快取及推理權杖與預估成本節省。',
        '輸入', '輸出', '快取', '推理',
        '每小時流量分佈', '峰值', '現在'
    ],
    de: [
        'Provider-Zustandsmatrix', 'Echtzeit-Status, aktive Zugangsdaten und Datenverkehrszustand aller KI-Provider.',
        'Betriebsbereit', 'Bereit / Leerlauf', 'Probleme / Wartezeit',
        'In Wartezeit', 'Beeinträchtigt (<60%)',
        'Token-Verbrauch & Verkehrsverteilung', 'Visuelle Aufschlüsselung von Eingabe-, Ausgabe-, Cache- und Reasoning-Token mit geschätzten Einsparungen.',
        'Eingabe', 'Ausgabe', 'Zwischengespeichert', 'Reasoning',
        'Stündliches Verkehrsaufkommen', 'Spitze', 'Jetzt'
    ],
    es: [
        'Matriz de estado de proveedores', 'Estado en tiempo real, credenciales activas y salud del tráfico en todos los proveedores de IA.',
        'Operativo', 'Inactivo / Listo', 'Problemas / Enfriamiento',
        'En enfriamiento', 'Degradado (<60%)',
        'Consumo de tokens y distribución de tráfico', 'Desglose visual de tokens de entrada, salida, caché y razonamiento con ahorro estimado.',
        'Entrada', 'Salida', 'En caché', 'Razonamiento',
        'Volumen de tráfico por hora', 'Pico', 'Ahora'
    ],
    fr: [
        'Matrice d’état des fournisseurs', 'État en temps réel, identifiants actifs et flux de trafic sur tous les fournisseurs d’IA.',
        'Opérationnel', 'Prêt / Inactif', 'Problèmes / Refroidissement',
        'En refroidissement', 'Dégradé (<60%)',
        'Consommation de tokens et distribution du trafic', 'Répartition visuelle des tokens d’entrée, de sortie, de cache et de raisonnement avec économies estimées.',
        'Entrée', 'Sortie', 'En cache', 'Raisonnement',
        'Volume de trafic horaire', 'Pic', 'Maintenant'
    ],
    id: [
        'Matriks Kesehatan Penyedia', 'Status waktu nyata, kredensial aktif, dan kesehatan lalu lintas di semua penyedia AI.',
        'Operasional', 'Siap / Menganggur', 'Masalah / Cooldown',
        'Dalam Cooldown', 'Menurun (<60%)',
        'Konsumsi Token & Distribusi Trafik', 'Rincian visual token input, output, cache, dan penalaran dengan estimasi penghematan biaya.',
        'Input', 'Output', 'Cache', 'Penalaran',
        'Volume Lalu Lintas Per Jam', 'Puncak', 'Sekarang'
    ],
    it: [
        'Matrice di salute dei provider', 'Stato in tempo reale, credenziali attive e salute del traffico su tutti i provider IA.',
        'Operativo', 'Pronto / Inattivo', 'Problemi / Cooldown',
        'In cooldown', 'Degradato (<60%)',
        'Consumo di token e distribuzione del traffico', 'Ripartizione visiva dei token di input, output, cache e ragionamento con risparmi stimati.',
        'Input', 'Output', 'In cache', 'Ragionamento',
        'Volume di traffico orario', 'Picco', 'Ora'
    ],
    ja: [
        'プロバイダー状態マトリックス', '全 AI プロバイダーのリアルタイム状態、有効な認証情報、トラフィック健全性。',
        '稼働中', '待機中 / 準備完了', '問題 / クールダウン',
        'クールダウン中', '低下中 (<60%)',
        'トークン消費とトラフィック分布', '入力、出力、キャッシュ、推論トークンの視覚的内訳と推定コスト削減額。',
        '入力', '出力', 'キャッシュ', '推論',
        '1時間あたりのトラフィック量', 'ピーク', '現在'
    ],
    ko: [
        '공급자 상태 매트릭스', '모든 지원 AI 공급자의 실시간 상태, 활성 자격 증명 및 트래픽 상태.',
        '정상 작동', '대기 중 / 준비됨', '문제 / 쿨다운',
        '쿨다운 중', '저하됨 (<60%)',
        '토큰 소비 및 트래픽 분포', '입력, 출력, 캐시 및 추론 토큰의 시각적 분석과 예상 비용 절감.',
        '입력', '출력', '캐시됨', '추론',
        '시간별 트래픽 볼륨', '최고치', '지금'
    ],
    pt: [
        'Matriz de saúde dos provedores', 'Status em tempo real, credenciais ativas e integridade do tráfego em todos os provedores de IA.',
        'Operacional', 'Pronto / Ocioso', 'Problemas / Cooldown',
        'Em cooldown', 'Degradado (<60%)',
        'Consumo de tokens e distribuição de tráfego', 'Detalhamento visual de tokens de entrada, saída, cache e raciocínio com economia estimada.',
        'Entrada', 'Saída', 'Em cache', 'Raciocínio',
        'Volume de tráfego por hora', 'Pico', 'Agora'
    ],
    ru: [
        'Матрица состояния провайдеров', 'Статус в реальном времени, активные учётные данные и состояние трафика по всем провайдерам ИИ.',
        'Работает', 'Готов / Ожидание', 'Проблемы / Охлаждение',
        'Охлаждение', 'Деградация (<60%)',
        'Потребление токенов и распределение трафика', 'Наглядная разбивка входных, выходных, кэшированных токенов и токенов рассуждений с оценкой экономии.',
        'Вход', 'Выход', 'Кэш', 'Рассуждения',
        'Почасовой объём трафика', 'Пик', 'Сейчас'
    ],
    th: [
        'เมทริกซ์สถานะของผู้ให้บริการ', 'สถานะแบบเรียลไทม์ ข้อมูลรับรองที่ใช้งานอยู่ และความสมบูรณ์ของการรับส่งข้อมูลของผู้ให้บริการ AI ทั้งหมด',
        'ทำงานปกติ', 'พร้อมใช้งาน / ว่าง', 'มีปัญหา / คูลดาวน์',
        'กำลังคูลดาวน์', 'ประสิทธิภาพลดลง (<60%)',
        'การใช้โทเค็นและการกระจายข้อมูล', 'การแจกแจงแบบเห็นภาพของโทเค็นอินพุต เอาต์พุต แคช และการใช้เหตุผล พร้อมการประหยัดต้นทุนโดยประมาณ',
        'อินพุต', 'เอาต์พุต', 'แคชแล้ว', 'การใช้เหตุผล',
        'ปริมาณทราฟฟิกรายชั่วโมง', 'สูงสุด', 'ตอนนี้'
    ],
    tr: [
        'Sağlayıcı Sağlık ve Durum Matrisi', 'Tüm yapay zekâ sağlayıcılarında gerçek zamanlı durum, etkin kimlik bilgileri ve trafik sağlığı.',
        'Çalışıyor', 'Hazır / Boşta', 'Sorunlar / Bekleme',
        'Beklemede', 'Düşük (<%60)',
        'Belirteç Tüketimi ve Trafik Dağılımı', 'Tahmini maliyet tasarrufu ile giriş, çıkış, önbellek ve akıl yürütme belirteçlerinin görsel dökümü.',
        'Giriş', 'Çıkış', 'Önbelleğe Alınan', 'Akıl Yürütme',
        'Saatlik Trafik Hacmi', 'Zirve', 'Şimdi'
    ],
    vi: [
        'Ma trận trạng thái & sức khỏe nhà cung cấp', 'Trạng thái thời gian thực, thông tin xác thực hoạt động và sức khỏe lưu lượng của tất cả nhà cung cấp AI.',
        'Hoạt động tốt', 'Sẵn sàng / Chờ', 'Gặp sự cố / Hồi nhiệt',
        'Đang hồi nhiệt', 'Suy giảm (<60%)',
        'Phân bổ lưu lượng & tiêu thụ Token', 'Trực quan hóa chi tiết token đầu vào, đầu ra, bộ nhớ đệm và suy luận (reasoning) cùng lượng tiết kiệm ước tính.',
        'Đầu vào', 'Đầu ra', 'Bộ nhớ đệm', 'Suy luận',
        'Lưu lượng yêu cầu theo giờ', 'Đỉnh điểm', 'Hiện tại'
    ]
};

for (const [locale, values] of Object.entries(DASHBOARD_METRICS_ENHANCEMENT_COPY)) {
    Object.assign(
        PAGE_LOCALE_TRANSLATIONS[locale],
        Object.fromEntries(DASHBOARD_METRICS_ENHANCEMENT_KEYS.map((key, index) => [key, values[index]])),
    );
}

const ROUTING_STRATEGY_KEYS = [
    'settings.weighted', 'settings.least_latency', 'settings.lowest_cost'
];

const ROUTING_STRATEGY_COPY = {
    en: ['Weighted random', 'Least latency', 'Lowest cost'],
    'zh-CN': ['加权随机', '最低延迟', '最低成本'],
    'zh-TW': ['加權隨機', '最低延遲', '最低成本'],
    de: ['Gewichteter Zufall', 'Geringste Latenz', 'Niedrigste Kosten'],
    es: ['Aleatorio ponderado', 'Menor latencia', 'Menor costo'],
    fr: ['Aléatoire pondéré', 'Latence minimale', 'Coût minimal'],
    id: ['Acak berbobot', 'Latensi terendah', 'Biaya terendah'],
    it: ['Casuale ponderato', 'Latenza minima', 'Costo minimo'],
    ja: ['重み付きランダム', '最小レイテンシ', '最低コスト'],
    ko: ['가중치 무작위', '최소 지연 시간', '최저 비용'],
    pt: ['Aleatório ponderado', 'Menor latência', 'Menor custo'],
    ru: ['Взвешенный случайный', 'Минимальная задержка', 'Минимальная стоимость'],
    th: ['สุ่มตามน้ำหนัก', 'ค่าหน่วงต่ำสุด', 'ต้นทุนต่ำสุด'],
    tr: ['Ağırlıklı rastgele', 'En düşük gecikme', 'En düşük maliyet'],
    vi: ['Ngẫu nhiên theo trọng số', 'Độ trễ thấp nhất', 'Chi phí thấp nhất']
};

for (const [locale, values] of Object.entries(ROUTING_STRATEGY_COPY)) {
    Object.assign(
        PAGE_LOCALE_TRANSLATIONS[locale],
        Object.fromEntries(ROUTING_STRATEGY_KEYS.map((key, index) => [key, values[index]])),
    );
}

const THEME_MESSAGES = {
    en: { 'theme.label': 'Theme', 'theme.system': 'System', 'theme.light': 'Light', 'theme.dark': 'Dark', 'theme.hint': 'Controls the console color scheme on this device.' },
    'zh-CN': { 'theme.label': '主题', 'theme.system': '跟随系统', 'theme.light': '浅色', 'theme.dark': '深色', 'theme.hint': '控制此设备上的控制台配色。' },
    'zh-TW': { 'theme.label': '主題', 'theme.system': '跟隨系統', 'theme.light': '淺色', 'theme.dark': '深色', 'theme.hint': '控制此裝置上的主控台配色。' },
    de: { 'theme.label': 'Design', 'theme.system': 'System', 'theme.light': 'Hell', 'theme.dark': 'Dunkel', 'theme.hint': 'Steuert das Farbschema der Konsole auf diesem Gerät.' },
    es: { 'theme.label': 'Tema', 'theme.system': 'Sistema', 'theme.light': 'Claro', 'theme.dark': 'Oscuro', 'theme.hint': 'Controla el esquema de color de la consola en este dispositivo.' },
    fr: { 'theme.label': 'Thème', 'theme.system': 'Système', 'theme.light': 'Clair', 'theme.dark': 'Sombre', 'theme.hint': 'Contrôle le jeu de couleurs de la console sur cet appareil.' },
    id: { 'theme.label': 'Tema', 'theme.system': 'Sistem', 'theme.light': 'Terang', 'theme.dark': 'Gelap', 'theme.hint': 'Mengatur skema warna konsol di perangkat ini.' },
    it: { 'theme.label': 'Tema', 'theme.system': 'Sistema', 'theme.light': 'Chiaro', 'theme.dark': 'Scuro', 'theme.hint': 'Controlla lo schema colori della console su questo dispositivo.' },
    ja: { 'theme.label': 'テーマ', 'theme.system': 'システム', 'theme.light': 'ライト', 'theme.dark': 'ダーク', 'theme.hint': 'このデバイスでのコンソールの配色を設定します。' },
    ko: { 'theme.label': '테마', 'theme.system': '시스템', 'theme.light': '라이트', 'theme.dark': '다크', 'theme.hint': '이 기기에서 콘솔 색상 구성을 설정합니다.' },
    pt: { 'theme.label': 'Tema', 'theme.system': 'Sistema', 'theme.light': 'Claro', 'theme.dark': 'Escuro', 'theme.hint': 'Controla o esquema de cores do console neste dispositivo.' },
    ru: { 'theme.label': 'Тема', 'theme.system': 'Системная', 'theme.light': 'Светлая', 'theme.dark': 'Тёмная', 'theme.hint': 'Управляет цветовой схемой консоли на этом устройстве.' },
    th: { 'theme.label': 'ธีม', 'theme.system': 'ตามระบบ', 'theme.light': 'สว่าง', 'theme.dark': 'มืด', 'theme.hint': 'ควบคุมชุดสีของคอนโซลบนอุปกรณ์นี้' },
    tr: { 'theme.label': 'Tema', 'theme.system': 'Sistem', 'theme.light': 'Açık', 'theme.dark': 'Koyu', 'theme.hint': 'Bu cihazdaki konsol renk düzenini kontrol eder.' },
    vi: { 'theme.label': 'Giao diện', 'theme.system': 'Theo hệ thống', 'theme.light': 'Sáng', 'theme.dark': 'Tối', 'theme.hint': 'Điều khiển bảng màu của bảng điều khiển trên thiết bị này.' }
};

for (const [locale, messages] of Object.entries(THEME_MESSAGES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], messages);
}

const ACCESS_MESSAGES = {
    en: { 'access.label': 'Access', 'access.title': 'API Access', 'access.description': 'Connect SDK clients with the root integration key and protocol-specific base URLs.', 'access.root_key': 'Root integration key', 'access.root_key_description': 'This deployment-wide key has unrestricted inference access. Rotate it deliberately and update every connected client.' },
    'zh-CN': { 'access.label': '访问控制', 'access.title': 'API 访问', 'access.description': '使用根集成密钥和各协议的基础 URL 连接 SDK 客户端。', 'access.root_key': '根集成密钥', 'access.root_key_description': '此部署级密钥拥有不受限的推理访问权限。轮换前请做好计划，并更新所有已连接客户端。' },
    'zh-TW': { 'access.label': '存取控制', 'access.title': 'API 存取', 'access.description': '使用根整合金鑰和各通訊協定的基礎 URL 連接 SDK 用戶端。', 'access.root_key': '根整合金鑰', 'access.root_key_description': '此部署層級金鑰具有不受限制的推論存取權。輪替前請先規劃，並更新所有已連接的用戶端。' },
    de: { 'access.label': 'Zugriff', 'access.title': 'API-Zugriff', 'access.description': 'Verbinden Sie SDK-Clients mit dem Root-Integrationsschlüssel und protokollspezifischen Basis-URLs.', 'access.root_key': 'Root-Integrationsschlüssel', 'access.root_key_description': 'Dieser installationsweite Schlüssel erlaubt uneingeschränkte Inferenzzugriffe. Rotieren Sie ihn geplant und aktualisieren Sie alle verbundenen Clients.' },
    es: { 'access.label': 'Acceso', 'access.title': 'Acceso a la API', 'access.description': 'Conecta clientes SDK con la clave raíz de integración y las URL base de cada protocolo.', 'access.root_key': 'Clave raíz de integración', 'access.root_key_description': 'Esta clave para toda la implementación permite inferencia sin restricciones. Rótala de forma planificada y actualiza todos los clientes conectados.' },
    fr: { 'access.label': 'Accès', 'access.title': 'Accès API', 'access.description': 'Connectez les clients SDK avec la clé d’intégration racine et les URL de base propres à chaque protocole.', 'access.root_key': 'Clé d’intégration racine', 'access.root_key_description': 'Cette clé valable pour tout le déploiement donne un accès sans restriction à l’inférence. Planifiez sa rotation et mettez à jour chaque client connecté.' },
    id: { 'access.label': 'Akses', 'access.title': 'Akses API', 'access.description': 'Hubungkan klien SDK dengan kunci integrasi root dan URL dasar khusus protokol.', 'access.root_key': 'Kunci integrasi root', 'access.root_key_description': 'Kunci tingkat deployment ini memiliki akses inferensi tanpa batas. Rotasikan secara terencana dan perbarui setiap klien yang terhubung.' },
    it: { 'access.label': 'Accesso', 'access.title': 'Accesso API', 'access.description': 'Collega i client SDK con la chiave di integrazione root e gli URL di base specifici del protocollo.', 'access.root_key': 'Chiave di integrazione root', 'access.root_key_description': 'Questa chiave valida per l’intero deployment consente inferenza senza restrizioni. Pianificane la rotazione e aggiorna tutti i client connessi.' },
    ja: { 'access.label': 'アクセス', 'access.title': 'API アクセス', 'access.description': 'ルート統合キーとプロトコル別のベース URL を使って SDK クライアントを接続します。', 'access.root_key': 'ルート統合キー', 'access.root_key_description': 'このデプロイ全体のキーには制限のない推論アクセス権があります。計画的にローテーションし、接続済みの全クライアントを更新してください。' },
    ko: { 'access.label': '접근 관리', 'access.title': 'API 접근', 'access.description': '루트 통합 키와 프로토콜별 기본 URL로 SDK 클라이언트를 연결합니다.', 'access.root_key': '루트 통합 키', 'access.root_key_description': '이 배포 전체 키에는 제한 없는 추론 접근 권한이 있습니다. 계획적으로 교체하고 연결된 모든 클라이언트를 업데이트하세요.' },
    pt: { 'access.label': 'Acesso', 'access.title': 'Acesso à API', 'access.description': 'Conecte clientes SDK com a chave raiz de integração e as URLs base específicas de cada protocolo.', 'access.root_key': 'Chave raiz de integração', 'access.root_key_description': 'Esta chave de todo o deployment permite inferência sem restrições. Faça a rotação de forma planejada e atualize todos os clientes conectados.' },
    ru: { 'access.label': 'Доступ', 'access.title': 'Доступ к API', 'access.description': 'Подключайте SDK-клиенты с помощью корневого ключа интеграции и базовых URL для каждого протокола.', 'access.root_key': 'Корневой ключ интеграции', 'access.root_key_description': 'Этот ключ действует на всё развёртывание и предоставляет неограниченный доступ к инференсу. Планируйте его ротацию и обновляйте все подключённые клиенты.' },
    th: { 'access.label': 'การเข้าถึง', 'access.title': 'การเข้าถึง API', 'access.description': 'เชื่อมต่อไคลเอนต์ SDK ด้วยคีย์การผสานรวมหลักและ URL ฐานเฉพาะโปรโตคอล', 'access.root_key': 'คีย์การผสานรวมหลัก', 'access.root_key_description': 'คีย์ระดับการติดตั้งนี้มีสิทธิ์เรียกใช้โมเดลโดยไม่จำกัด ควรวางแผนหมุนเวียนคีย์และอัปเดตไคลเอนต์ที่เชื่อมต่อทั้งหมด' },
    tr: { 'access.label': 'Erişim', 'access.title': 'API Erişimi', 'access.description': 'SDK istemcilerini kök entegrasyon anahtarı ve protokole özel temel URL’lerle bağlayın.', 'access.root_key': 'Kök entegrasyon anahtarı', 'access.root_key_description': 'Dağıtım genelindeki bu anahtar sınırsız çıkarım erişimine sahiptir. Planlı biçimde yenileyin ve bağlı tüm istemcileri güncelleyin.' },
    vi: { 'access.label': 'Quyền truy cập', 'access.title': 'Truy cập API', 'access.description': 'Kết nối ứng dụng khách SDK bằng khóa tích hợp gốc và URL cơ sở riêng cho từng giao thức.', 'access.root_key': 'Khóa tích hợp gốc', 'access.root_key_description': 'Khóa dùng chung cho toàn bộ bản triển khai này có quyền suy luận không giới hạn. Hãy chủ động lên kế hoạch xoay vòng và cập nhật mọi ứng dụng khách đang kết nối.' }
};

for (const [locale, messages] of Object.entries(ACCESS_MESSAGES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], messages);
}

const ACCESS_DYNAMIC_MESSAGES = {
    en: { 'access.api_key_copy_label': 'API key. Copy API key.', 'access.hide_api_key': 'Hide API key', 'access.api_key_managed_env': 'API key is managed by the API_KEY environment variable' },
    'zh-CN': { 'access.api_key_copy_label': 'API 密钥。复制 API 密钥。', 'access.hide_api_key': '隐藏 API 密钥', 'access.api_key_managed_env': 'API 密钥由 API_KEY 环境变量管理' },
    'zh-TW': { 'access.api_key_copy_label': 'API 金鑰。複製 API 金鑰。', 'access.hide_api_key': '隱藏 API 金鑰', 'access.api_key_managed_env': 'API 金鑰由 API_KEY 環境變數管理' },
    de: { 'access.api_key_copy_label': 'API-Schlüssel. API-Schlüssel kopieren.', 'access.hide_api_key': 'API-Schlüssel ausblenden', 'access.api_key_managed_env': 'Der API-Schlüssel wird durch die Umgebungsvariable API_KEY verwaltet' },
    es: { 'access.api_key_copy_label': 'Clave de API. Copiar clave de API.', 'access.hide_api_key': 'Ocultar clave de API', 'access.api_key_managed_env': 'La clave de API se administra mediante la variable de entorno API_KEY' },
    fr: { 'access.api_key_copy_label': 'Clé API. Copier la clé API.', 'access.hide_api_key': 'Masquer la clé API', 'access.api_key_managed_env': 'La clé API est gérée par la variable d’environnement API_KEY' },
    id: { 'access.api_key_copy_label': 'Kunci API. Salin kunci API.', 'access.hide_api_key': 'Sembunyikan kunci API', 'access.api_key_managed_env': 'Kunci API dikelola oleh variabel lingkungan API_KEY' },
    it: { 'access.api_key_copy_label': 'Chiave API. Copia chiave API.', 'access.hide_api_key': 'Nascondi chiave API', 'access.api_key_managed_env': 'La chiave API è gestita dalla variabile di ambiente API_KEY' },
    ja: { 'access.api_key_copy_label': 'API キー。API キーをコピー。', 'access.hide_api_key': 'API キーを隠す', 'access.api_key_managed_env': 'API キーは環境変数 API_KEY で管理されています' },
    ko: { 'access.api_key_copy_label': 'API 키. API 키 복사.', 'access.hide_api_key': 'API 키 숨기기', 'access.api_key_managed_env': 'API 키는 API_KEY 환경 변수에서 관리됩니다' },
    pt: { 'access.api_key_copy_label': 'Chave de API. Copiar chave de API.', 'access.hide_api_key': 'Ocultar chave de API', 'access.api_key_managed_env': 'A chave de API é gerenciada pela variável de ambiente API_KEY' },
    ru: { 'access.api_key_copy_label': 'Ключ API. Копировать ключ API.', 'access.hide_api_key': 'Скрыть ключ API', 'access.api_key_managed_env': 'Ключ API управляется переменной окружения API_KEY' },
    th: { 'access.api_key_copy_label': 'คีย์ API คัดลอกคีย์ API', 'access.hide_api_key': 'ซ่อนคีย์ API', 'access.api_key_managed_env': 'คีย์ API จัดการโดยตัวแปรสภาพแวดล้อม API_KEY' },
    tr: { 'access.api_key_copy_label': 'API anahtarı. API anahtarını kopyala.', 'access.hide_api_key': 'API anahtarını gizle', 'access.api_key_managed_env': 'API anahtarı API_KEY ortam değişkeni tarafından yönetiliyor' },
    vi: { 'access.api_key_copy_label': 'Khóa API. Sao chép khóa API.', 'access.hide_api_key': 'Ẩn khóa API', 'access.api_key_managed_env': 'Khóa API do biến môi trường API_KEY quản lý' }
};

for (const [locale, messages] of Object.entries(ACCESS_DYNAMIC_MESSAGES)) {
    Object.assign(PAGE_LOCALE_TRANSLATIONS[locale], messages);
}
