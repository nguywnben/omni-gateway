// Omni Gateway management console: supported interface locales.

const SUPPORTED_LOCALES = {
    en: {
        label: 'English',
        messages: {
            language: 'Language', dashboard: 'Dashboard', pool: 'Pool', models: 'Models', providers: 'Providers', settings: 'Settings', logs: 'Logs', about: 'About',
            sign_out: 'Sign out', sign_in_title: 'Sign In to the Console', login_copy: 'Manage routing, credentials, fallback behavior, and protocol translation from one focused workspace.',
            console_password: 'Console password', enter_password: 'Enter password', continue: 'Continue', setup_title: 'Create Your Console Password', setup_copy: 'Secure this new Omni Gateway instance before opening the management console.',
            confirm_password: 'Confirm password', create_password: 'Create password', footer_tagline: 'Universal AI routing for coding tools.',
            dashboard_title: 'Omni Gateway Dashboard', dashboard_description: 'Monitor request flow, provider capacity, and integration details for coding-tool traffic.',
            pool_title: 'Provider Credential Pool', pool_description: 'Manage accounts and API keys from every connected provider. Monitor credential health, routing capacity, and pool backups from one place.',
            models_title: 'Routing Models', models_description: 'Manage virtual model routes and inspect provider models available to the shared credential pool.',
            providers_title: 'Add Provider Credentials', providers_description: 'Choose a provider, connect an account or API key, and add it to the shared routing pool.',
            settings_title: 'System Configuration', settings_description: 'Tune console access, storage, proxy, retry policy, response translation, and keep-alive behavior.',
            logs_title: 'Runtime Log Stream', logs_description: 'Watch routing decisions, upstream responses, credential rotation, and application errors.',
            about_description: 'A universal AI router for coding tools with smart auto-fallback, token-aware request cleanup, usage visibility, and seamless format translation.'
        }
    },
    'zh-CN': {
        label: '中文(简体)',
        messages: {
            language: '语言', dashboard: '仪表板', pool: '凭据池', models: '模型', providers: '提供商', settings: '设置', logs: '日志', about: '关于',
            sign_out: '退出登录', sign_in_title: '登录控制台', login_copy: '在一个专注的工作区中管理路由、凭据、故障转移策略和协议转换。',
            console_password: '控制台密码', enter_password: '输入密码', continue: '继续', setup_title: '创建控制台密码', setup_copy: '在打开管理控制台前，请先保护这个新的 Omni Gateway 实例。',
            confirm_password: '确认密码', create_password: '创建密码', footer_tagline: '面向编码工具的通用 AI 路由。',
            dashboard_title: 'Omni Gateway 仪表板', dashboard_description: '监控编码工具流量的请求流、提供商容量和集成详情。',
            pool_title: '提供商凭据池', pool_description: '集中管理所有已连接提供商的账户和 API 密钥，并监控凭据健康度、路由容量和池备份。',
            models_title: '路由模型', models_description: '管理虚拟模型路由，并查看共享凭据池中可用的提供商模型。',
            providers_title: '添加提供商凭据', providers_description: '选择提供商，连接账户或 API 密钥，然后将其加入共享路由池。',
            settings_title: '系统配置', settings_description: '调整控制台访问、存储、代理、重试策略、响应转换和保活行为。',
            logs_title: '运行时日志流', logs_description: '查看路由决策、上游响应、凭据轮换和应用错误。',
            about_description: '面向编码工具的通用 AI 路由器，提供智能自动故障转移、令牌感知的请求清理、使用情况可见性和无缝格式转换。'
        }
    },
    'zh-TW': {
        label: '中文(繁體)',
        messages: {
            language: '語言', dashboard: '儀表板', pool: '憑證集區', models: '模型', providers: '供應商', settings: '設定', logs: '日誌', about: '關於',
            sign_out: '登出', sign_in_title: '登入主控台', login_copy: '在單一專注的工作區中管理路由、憑證、容錯行為與通訊協定轉換。',
            console_password: '主控台密碼', enter_password: '輸入密碼', continue: '繼續', setup_title: '建立主控台密碼', setup_copy: '開啟管理主控台前，請先保護這個新的 Omni Gateway 執行個體。',
            confirm_password: '確認密碼', create_password: '建立密碼', footer_tagline: '適用於程式開發工具的通用 AI 路由。',
            dashboard_title: 'Omni Gateway 儀表板', dashboard_description: '監控程式開發工具流量的請求流程、供應商容量與整合詳細資料。',
            pool_title: '供應商憑證集區', pool_description: '集中管理每個已連線供應商的帳戶與 API 金鑰，並監控憑證健康度、路由容量與集區備份。',
            models_title: '路由模型', models_description: '管理虛擬模型路由，並檢視共用憑證集區可用的供應商模型。',
            providers_title: '新增供應商憑證', providers_description: '選擇供應商、連線帳戶或 API 金鑰，然後加入共用路由集區。',
            settings_title: '系統設定', settings_description: '調整主控台存取、儲存空間、Proxy、重試策略、回應轉換與保活行為。',
            logs_title: '執行階段日誌串流', logs_description: '檢視路由決策、上游回應、憑證輪替與應用程式錯誤。',
            about_description: '適用於程式開發工具的通用 AI 路由器，提供智慧自動容錯、權杖感知請求清理、用量可見性與無縫格式轉換。'
        }
    },
    de: {
        label: 'Deutsch',
        messages: {
            language: 'Sprache', dashboard: 'Dashboard', pool: 'Pool', models: 'Modelle', providers: 'Anbieter', settings: 'Einstellungen', logs: 'Protokolle', about: 'Info',
            sign_out: 'Abmelden', sign_in_title: 'Bei der Konsole anmelden', login_copy: 'Verwalten Sie Routing, Zugangsdaten, Failover-Verhalten und Protokollübersetzung in einem fokussierten Arbeitsbereich.',
            console_password: 'Konsolenpasswort', enter_password: 'Passwort eingeben', continue: 'Weiter', setup_title: 'Konsolenpasswort erstellen', setup_copy: 'Sichern Sie diese neue Omni-Gateway-Instanz, bevor Sie die Verwaltungskonsole öffnen.',
            confirm_password: 'Passwort bestätigen', create_password: 'Passwort erstellen', footer_tagline: 'Universelles KI-Routing für Coding-Tools.',
            dashboard_title: 'Omni Gateway Dashboard', dashboard_description: 'Überwachen Sie Anfragefluss, Anbieterkapazität und Integrationsdetails für den Traffic Ihrer Coding-Tools.',
            pool_title: 'Anbieter-Zugangsdatenpool', pool_description: 'Verwalten Sie Konten und API-Schlüssel aller verbundenen Anbieter. Behalten Sie Zustand, Routing-Kapazität und Pool-Backups an einem Ort im Blick.',
            models_title: 'Routing-Modelle', models_description: 'Verwalten Sie virtuelle Modellrouten und prüfen Sie die im gemeinsamen Zugangsdatenpool verfügbaren Anbietermodelle.',
            providers_title: 'Anbieter-Zugangsdaten hinzufügen', providers_description: 'Wählen Sie einen Anbieter, verbinden Sie ein Konto oder einen API-Schlüssel und fügen Sie ihn dem gemeinsamen Routing-Pool hinzu.',
            settings_title: 'Systemkonfiguration', settings_description: 'Konfigurieren Sie Konsolenzugriff, Speicher, Proxy, Wiederholungsstrategie, Antwortübersetzung und Keep-Alive-Verhalten.',
            logs_title: 'Laufzeit-Protokollstream', logs_description: 'Beobachten Sie Routing-Entscheidungen, Upstream-Antworten, Zugangsdatenrotation und Anwendungsfehler.',
            about_description: 'Ein universeller KI-Router für Coding-Tools mit intelligentem Auto-Failover, tokenbewusster Anfragebereinigung, Nutzungsübersicht und nahtloser Formatübersetzung.'
        }
    },
    es: {
        label: 'Español',
        messages: {
            language: 'Idioma', dashboard: 'Panel', pool: 'Grupo', models: 'Modelos', providers: 'Proveedores', settings: 'Configuración', logs: 'Registros', about: 'Acerca de',
            sign_out: 'Cerrar sesión', sign_in_title: 'Iniciar sesión en la consola', login_copy: 'Administra el enrutamiento, las credenciales, el comportamiento de conmutación por error y la traducción de protocolos desde un espacio de trabajo enfocado.',
            console_password: 'Contraseña de la consola', enter_password: 'Introduce la contraseña', continue: 'Continuar', setup_title: 'Crea la contraseña de la consola', setup_copy: 'Protege esta nueva instancia de Omni Gateway antes de abrir la consola de administración.',
            confirm_password: 'Confirmar contraseña', create_password: 'Crear contraseña', footer_tagline: 'Enrutamiento universal de IA para herramientas de programación.',
            dashboard_title: 'Panel de Omni Gateway', dashboard_description: 'Supervisa el flujo de solicitudes, la capacidad de los proveedores y los detalles de integración del tráfico de herramientas de programación.',
            pool_title: 'Grupo de credenciales de proveedores', pool_description: 'Administra cuentas y claves API de todos los proveedores conectados. Supervisa el estado de las credenciales, la capacidad de enrutamiento y las copias de seguridad desde un solo lugar.',
            models_title: 'Modelos de enrutamiento', models_description: 'Administra rutas de modelos virtuales e inspecciona los modelos de proveedores disponibles en el grupo compartido de credenciales.',
            providers_title: 'Añadir credenciales de proveedor', providers_description: 'Elige un proveedor, conecta una cuenta o una clave API y añádela al grupo de enrutamiento compartido.',
            settings_title: 'Configuración del sistema', settings_description: 'Ajusta el acceso a la consola, el almacenamiento, el proxy, la política de reintentos, la traducción de respuestas y el comportamiento de keep-alive.',
            logs_title: 'Flujo de registros de ejecución', logs_description: 'Consulta decisiones de enrutamiento, respuestas ascendentes, rotación de credenciales y errores de la aplicación.',
            about_description: 'Un router de IA universal para herramientas de programación con conmutación automática inteligente, limpieza de solicitudes basada en tokens, visibilidad de uso y traducción de formatos fluida.'
        }
    },
    fr: {
        label: 'Français',
        messages: {
            language: 'Langue', dashboard: 'Tableau de bord', pool: 'Pool', models: 'Modèles', providers: 'Fournisseurs', settings: 'Paramètres', logs: 'Journaux', about: 'À propos',
            sign_out: 'Se déconnecter', sign_in_title: 'Se connecter à la console', login_copy: 'Gérez le routage, les identifiants, le basculement et la traduction de protocoles depuis un espace de travail unique.',
            console_password: 'Mot de passe de la console', enter_password: 'Saisir le mot de passe', continue: 'Continuer', setup_title: 'Créer le mot de passe de la console', setup_copy: 'Sécurisez cette nouvelle instance Omni Gateway avant d’ouvrir la console d’administration.',
            confirm_password: 'Confirmer le mot de passe', create_password: 'Créer le mot de passe', footer_tagline: 'Routage IA universel pour les outils de développement.',
            dashboard_title: 'Tableau de bord Omni Gateway', dashboard_description: 'Suivez le flux des requêtes, la capacité des fournisseurs et les détails d’intégration du trafic des outils de développement.',
            pool_title: 'Pool d’identifiants fournisseurs', pool_description: 'Gérez les comptes et clés API de chaque fournisseur connecté. Suivez l’état des identifiants, la capacité de routage et les sauvegardes du pool au même endroit.',
            models_title: 'Modèles de routage', models_description: 'Gérez les routes de modèles virtuels et examinez les modèles fournisseurs disponibles dans le pool d’identifiants partagé.',
            providers_title: 'Ajouter des identifiants fournisseur', providers_description: 'Choisissez un fournisseur, connectez un compte ou une clé API, puis ajoutez-le au pool de routage partagé.',
            settings_title: 'Configuration système', settings_description: 'Réglez l’accès à la console, le stockage, le proxy, la politique de relance, la traduction des réponses et le keep-alive.',
            logs_title: 'Flux de journaux d’exécution', logs_description: 'Consultez les décisions de routage, les réponses amont, la rotation des identifiants et les erreurs applicatives.',
            about_description: 'Un routeur IA universel pour les outils de développement, avec basculement automatique intelligent, nettoyage des requêtes tenant compte des tokens, visibilité de l’utilisation et traduction de formats fluide.'
        }
    },
    id: {
        label: 'Indonesia',
        messages: {
            language: 'Bahasa', dashboard: 'Dasbor', pool: 'Pool', models: 'Model', providers: 'Penyedia', settings: 'Pengaturan', logs: 'Log', about: 'Tentang',
            sign_out: 'Keluar', sign_in_title: 'Masuk ke Konsol', login_copy: 'Kelola perutean, kredensial, perilaku failover, dan penerjemahan protokol dari satu ruang kerja yang terfokus.',
            console_password: 'Kata sandi konsol', enter_password: 'Masukkan kata sandi', continue: 'Lanjutkan', setup_title: 'Buat Kata Sandi Konsol', setup_copy: 'Amankan instans Omni Gateway baru ini sebelum membuka konsol pengelolaan.',
            confirm_password: 'Konfirmasi kata sandi', create_password: 'Buat kata sandi', footer_tagline: 'Perutean AI universal untuk alat pemrograman.',
            dashboard_title: 'Dasbor Omni Gateway', dashboard_description: 'Pantau aliran permintaan, kapasitas penyedia, dan detail integrasi untuk trafik alat pemrograman.',
            pool_title: 'Pool Kredensial Penyedia', pool_description: 'Kelola akun dan kunci API dari setiap penyedia yang terhubung. Pantau kesehatan kredensial, kapasitas perutean, dan cadangan pool dari satu tempat.',
            models_title: 'Model Perutean', models_description: 'Kelola rute model virtual dan periksa model penyedia yang tersedia bagi pool kredensial bersama.',
            providers_title: 'Tambahkan Kredensial Penyedia', providers_description: 'Pilih penyedia, hubungkan akun atau kunci API, lalu tambahkan ke pool perutean bersama.',
            settings_title: 'Konfigurasi Sistem', settings_description: 'Atur akses konsol, penyimpanan, proxy, kebijakan percobaan ulang, penerjemahan respons, dan perilaku keep-alive.',
            logs_title: 'Aliran Log Runtime', logs_description: 'Pantau keputusan perutean, respons upstream, rotasi kredensial, dan kesalahan aplikasi.',
            about_description: 'Router AI universal untuk alat pemrograman dengan failover otomatis yang cerdas, pembersihan permintaan sadar token, visibilitas penggunaan, dan penerjemahan format yang mulus.'
        }
    },
    it: {
        label: 'Italiano',
        messages: {
            language: 'Lingua', dashboard: 'Dashboard', pool: 'Pool', models: 'Modelli', providers: 'Provider', settings: 'Impostazioni', logs: 'Log', about: 'Informazioni',
            sign_out: 'Esci', sign_in_title: 'Accedi alla console', login_copy: 'Gestisci routing, credenziali, comportamento di failover e traduzione dei protocolli da un unico spazio di lavoro.',
            console_password: 'Password della console', enter_password: 'Inserisci la password', continue: 'Continua', setup_title: 'Crea la password della console', setup_copy: 'Proteggi questa nuova istanza Omni Gateway prima di aprire la console di gestione.',
            confirm_password: 'Conferma password', create_password: 'Crea password', footer_tagline: 'Routing IA universale per strumenti di sviluppo.',
            dashboard_title: 'Dashboard Omni Gateway', dashboard_description: 'Monitora il flusso delle richieste, la capacità dei provider e i dettagli di integrazione per il traffico degli strumenti di sviluppo.',
            pool_title: 'Pool di credenziali provider', pool_description: 'Gestisci account e chiavi API di ogni provider connesso. Monitora stato delle credenziali, capacità di routing e backup del pool da un unico punto.',
            models_title: 'Modelli di routing', models_description: 'Gestisci percorsi di modelli virtuali e controlla i modelli provider disponibili nel pool condiviso di credenziali.',
            providers_title: 'Aggiungi credenziali provider', providers_description: 'Scegli un provider, collega un account o una chiave API e aggiungilo al pool di routing condiviso.',
            settings_title: 'Configurazione di sistema', settings_description: 'Regola accesso alla console, archiviazione, proxy, criteri di tentativo, traduzione delle risposte e comportamento keep-alive.',
            logs_title: 'Flusso log di runtime', logs_description: 'Osserva decisioni di routing, risposte upstream, rotazione delle credenziali ed errori dell’applicazione.',
            about_description: 'Un router IA universale per strumenti di sviluppo con failover automatico intelligente, pulizia delle richieste basata sui token, visibilità dell’utilizzo e traduzione dei formati senza interruzioni.'
        }
    },
    ja: {
        label: '日本語',
        messages: {
            language: '言語', dashboard: 'ダッシュボード', pool: 'プール', models: 'モデル', providers: 'プロバイダー', settings: '設定', logs: 'ログ', about: '概要',
            sign_out: 'サインアウト', sign_in_title: 'コンソールにサインイン', login_copy: 'ルーティング、認証情報、フェイルオーバー動作、プロトコル変換を一つのワークスペースで管理します。',
            console_password: 'コンソールのパスワード', enter_password: 'パスワードを入力', continue: '続行', setup_title: 'コンソールのパスワードを作成', setup_copy: '管理コンソールを開く前に、この新しい Omni Gateway インスタンスを保護してください。',
            confirm_password: 'パスワードを確認', create_password: 'パスワードを作成', footer_tagline: 'コーディングツールのためのユニバーサル AI ルーティング。',
            dashboard_title: 'Omni Gateway ダッシュボード', dashboard_description: 'コーディングツールのトラフィックについて、リクエストフロー、プロバイダー容量、統合の詳細を監視します。',
            pool_title: 'プロバイダー認証情報プール', pool_description: '接続済みプロバイダーのアカウントと API キーを管理し、認証情報の状態、ルーティング容量、プールのバックアップを一か所で確認します。',
            models_title: 'ルーティングモデル', models_description: '仮想モデルルートを管理し、共有認証情報プールで利用できるプロバイダーモデルを確認します。',
            providers_title: 'プロバイダー認証情報を追加', providers_description: 'プロバイダーを選択し、アカウントまたは API キーを接続して、共有ルーティングプールに追加します。',
            settings_title: 'システム設定', settings_description: 'コンソールアクセス、ストレージ、プロキシ、再試行ポリシー、応答変換、キープアライブ動作を調整します。',
            logs_title: 'ランタイムログストリーム', logs_description: 'ルーティングの判断、上流応答、認証情報のローテーション、アプリケーションエラーを確認します。',
            about_description: 'スマートな自動フェイルオーバー、トークンを考慮したリクエスト整理、利用状況の可視化、シームレスな形式変換を備えたコーディングツール向けユニバーサル AI ルーター。'
        }
    },
    ko: {
        label: '한국어',
        messages: {
            language: '언어', dashboard: '대시보드', pool: '풀', models: '모델', providers: '공급자', settings: '설정', logs: '로그', about: '정보',
            sign_out: '로그아웃', sign_in_title: '콘솔에 로그인', login_copy: '하나의 집중된 작업 공간에서 라우팅, 자격 증명, 장애 조치 동작, 프로토콜 변환을 관리하세요.',
            console_password: '콘솔 비밀번호', enter_password: '비밀번호 입력', continue: '계속', setup_title: '콘솔 비밀번호 만들기', setup_copy: '관리 콘솔을 열기 전에 새 Omni Gateway 인스턴스를 보호하세요.',
            confirm_password: '비밀번호 확인', create_password: '비밀번호 만들기', footer_tagline: '코딩 도구를 위한 범용 AI 라우팅.',
            dashboard_title: 'Omni Gateway 대시보드', dashboard_description: '코딩 도구 트래픽의 요청 흐름, 공급자 용량, 통합 세부 정보를 모니터링합니다.',
            pool_title: '공급자 자격 증명 풀', pool_description: '연결된 모든 공급자의 계정과 API 키를 관리하세요. 자격 증명 상태, 라우팅 용량, 풀 백업을 한곳에서 확인할 수 있습니다.',
            models_title: '라우팅 모델', models_description: '가상 모델 경로를 관리하고 공유 자격 증명 풀에서 사용할 수 있는 공급자 모델을 확인하세요.',
            providers_title: '공급자 자격 증명 추가', providers_description: '공급자를 선택하고 계정 또는 API 키를 연결한 후 공유 라우팅 풀에 추가하세요.',
            settings_title: '시스템 구성', settings_description: '콘솔 접근, 저장소, 프록시, 재시도 정책, 응답 변환, keep-alive 동작을 조정합니다.',
            logs_title: '런타임 로그 스트림', logs_description: '라우팅 결정, 업스트림 응답, 자격 증명 순환, 애플리케이션 오류를 확인합니다.',
            about_description: '스마트 자동 장애 조치, 토큰 인식 요청 정리, 사용량 가시성, 원활한 형식 변환을 제공하는 코딩 도구용 범용 AI 라우터입니다.'
        }
    },
    pt: {
        label: 'Português',
        messages: {
            language: 'Idioma', dashboard: 'Painel', pool: 'Pool', models: 'Modelos', providers: 'Provedores', settings: 'Configurações', logs: 'Logs', about: 'Sobre',
            sign_out: 'Sair', sign_in_title: 'Entrar no Console', login_copy: 'Gerencie roteamento, credenciais, comportamento de failover e tradução de protocolos em um espaço de trabalho focado.',
            console_password: 'Senha do console', enter_password: 'Digite a senha', continue: 'Continuar', setup_title: 'Crie a Senha do Console', setup_copy: 'Proteja esta nova instância do Omni Gateway antes de abrir o console de gerenciamento.',
            confirm_password: 'Confirmar senha', create_password: 'Criar senha', footer_tagline: 'Roteamento universal de IA para ferramentas de programação.',
            dashboard_title: 'Painel do Omni Gateway', dashboard_description: 'Monitore o fluxo de solicitações, a capacidade dos provedores e os detalhes de integração do tráfego de ferramentas de programação.',
            pool_title: 'Pool de Credenciais de Provedores', pool_description: 'Gerencie contas e chaves de API de todos os provedores conectados. Acompanhe a integridade das credenciais, a capacidade de roteamento e os backups do pool em um só lugar.',
            models_title: 'Modelos de Roteamento', models_description: 'Gerencie rotas de modelos virtuais e inspecione os modelos de provedores disponíveis no pool compartilhado de credenciais.',
            providers_title: 'Adicionar Credenciais de Provedor', providers_description: 'Escolha um provedor, conecte uma conta ou chave de API e adicione-a ao pool de roteamento compartilhado.',
            settings_title: 'Configuração do Sistema', settings_description: 'Ajuste o acesso ao console, armazenamento, proxy, política de tentativas, tradução de respostas e comportamento de keep-alive.',
            logs_title: 'Fluxo de Logs de Execução', logs_description: 'Acompanhe decisões de roteamento, respostas upstream, rotação de credenciais e erros da aplicação.',
            about_description: 'Um roteador de IA universal para ferramentas de programação com failover automático inteligente, limpeza de solicitações orientada por tokens, visibilidade de uso e tradução de formatos integrada.'
        }
    },
    ru: {
        label: 'Русский',
        messages: {
            language: 'Язык', dashboard: 'Панель', pool: 'Пул', models: 'Модели', providers: 'Провайдеры', settings: 'Настройки', logs: 'Журналы', about: 'О проекте',
            sign_out: 'Выйти', sign_in_title: 'Войти в консоль', login_copy: 'Управляйте маршрутизацией, учётными данными, отказоустойчивостью и преобразованием протоколов в едином рабочем пространстве.',
            console_password: 'Пароль консоли', enter_password: 'Введите пароль', continue: 'Продолжить', setup_title: 'Создайте пароль консоли', setup_copy: 'Защитите новый экземпляр Omni Gateway перед открытием консоли управления.',
            confirm_password: 'Подтвердите пароль', create_password: 'Создать пароль', footer_tagline: 'Универсальная маршрутизация ИИ для инструментов разработки.',
            dashboard_title: 'Панель Omni Gateway', dashboard_description: 'Отслеживайте поток запросов, возможности провайдеров и детали интеграции трафика инструментов разработки.',
            pool_title: 'Пул учётных данных провайдеров', pool_description: 'Управляйте аккаунтами и API-ключами всех подключённых провайдеров. Контролируйте состояние учётных данных, ресурсы маршрутизации и резервные копии пула в одном месте.',
            models_title: 'Модели маршрутизации', models_description: 'Управляйте маршрутами виртуальных моделей и просматривайте модели провайдеров, доступные в общем пуле учётных данных.',
            providers_title: 'Добавить учётные данные провайдера', providers_description: 'Выберите провайдера, подключите аккаунт или API-ключ и добавьте его в общий пул маршрутизации.',
            settings_title: 'Конфигурация системы', settings_description: 'Настройте доступ к консоли, хранилище, прокси, политику повторов, преобразование ответов и keep-alive.',
            logs_title: 'Поток журналов выполнения', logs_description: 'Просматривайте решения маршрутизации, ответы upstream, ротацию учётных данных и ошибки приложения.',
            about_description: 'Универсальный ИИ-маршрутизатор для инструментов разработки с интеллектуальным автоматическим failover, очисткой запросов с учётом токенов, прозрачностью использования и бесшовным преобразованием форматов.'
        }
    },
    th: {
        label: 'ภาษาไทย',
        messages: {
            language: 'ภาษา', dashboard: 'แดชบอร์ด', pool: 'พูล', models: 'โมเดล', providers: 'ผู้ให้บริการ', settings: 'การตั้งค่า', logs: 'บันทึก', about: 'เกี่ยวกับ',
            sign_out: 'ออกจากระบบ', sign_in_title: 'ลงชื่อเข้าใช้คอนโซล', login_copy: 'จัดการการกำหนดเส้นทาง ข้อมูลรับรอง การทำงานเมื่อเกิดข้อผิดพลาด และการแปลงโปรโตคอลจากพื้นที่ทำงานเดียว',
            console_password: 'รหัสผ่านคอนโซล', enter_password: 'ป้อนรหัสผ่าน', continue: 'ดำเนินการต่อ', setup_title: 'สร้างรหัสผ่านคอนโซล', setup_copy: 'ปกป้องอินสแตนซ์ Omni Gateway ใหม่นี้ก่อนเปิดคอนโซลการจัดการ',
            confirm_password: 'ยืนยันรหัสผ่าน', create_password: 'สร้างรหัสผ่าน', footer_tagline: 'การกำหนดเส้นทาง AI สากลสำหรับเครื่องมือเขียนโค้ด',
            dashboard_title: 'แดชบอร์ด Omni Gateway', dashboard_description: 'ติดตามการไหลของคำขอ ความจุของผู้ให้บริการ และรายละเอียดการผสานรวมสำหรับทราฟฟิกของเครื่องมือเขียนโค้ด',
            pool_title: 'พูลข้อมูลรับรองผู้ให้บริการ', pool_description: 'จัดการบัญชีและ API key จากผู้ให้บริการที่เชื่อมต่อทั้งหมด ตรวจสอบสถานะข้อมูลรับรอง ความจุการกำหนดเส้นทาง และข้อมูลสำรองของพูลได้ในที่เดียว',
            models_title: 'โมเดลการกำหนดเส้นทาง', models_description: 'จัดการเส้นทางโมเดลเสมือนและตรวจสอบโมเดลของผู้ให้บริการที่มีในพูลข้อมูลรับรองร่วม',
            providers_title: 'เพิ่มข้อมูลรับรองผู้ให้บริการ', providers_description: 'เลือกผู้ให้บริการ เชื่อมต่อบัญชีหรือ API key แล้วเพิ่มลงในพูลการกำหนดเส้นทางร่วม',
            settings_title: 'การกำหนดค่าระบบ', settings_description: 'ปรับการเข้าถึงคอนโซล พื้นที่จัดเก็บ พร็อกซี นโยบายการลองใหม่ การแปลงการตอบกลับ และ keep-alive',
            logs_title: 'สตรีมบันทึกขณะทำงาน', logs_description: 'ดูการตัดสินใจกำหนดเส้นทาง การตอบกลับจากต้นทาง การหมุนเวียนข้อมูลรับรอง และข้อผิดพลาดของแอปพลิเคชัน',
            about_description: 'เราเตอร์ AI สากลสำหรับเครื่องมือเขียนโค้ด พร้อมการสลับเส้นทางอัตโนมัติอัจฉริยะ การล้างคำขอโดยคำนึงถึงโทเค็น การมองเห็นการใช้งาน และการแปลงรูปแบบอย่างราบรื่น'
        }
    },
    tr: {
        label: 'Türkçe',
        messages: {
            language: 'Dil', dashboard: 'Pano', pool: 'Havuz', models: 'Modeller', providers: 'Sağlayıcılar', settings: 'Ayarlar', logs: 'Günlükler', about: 'Hakkında',
            sign_out: 'Oturumu kapat', sign_in_title: 'Konsolda oturum aç', login_copy: 'Yönlendirmeyi, kimlik bilgilerini, yük devretme davranışını ve protokol çevirisini tek bir odaklı çalışma alanından yönetin.',
            console_password: 'Konsol parolası', enter_password: 'Parolayı girin', continue: 'Devam et', setup_title: 'Konsol Parolasını Oluştur', setup_copy: 'Yönetim konsolunu açmadan önce bu yeni Omni Gateway örneğini güvence altına alın.',
            confirm_password: 'Parolayı onayla', create_password: 'Parola oluştur', footer_tagline: 'Kodlama araçları için evrensel yapay zekâ yönlendirmesi.',
            dashboard_title: 'Omni Gateway Panosu', dashboard_description: 'Kodlama aracı trafiğinin istek akışını, sağlayıcı kapasitesini ve entegrasyon ayrıntılarını izleyin.',
            pool_title: 'Sağlayıcı Kimlik Bilgileri Havuzu', pool_description: 'Bağlı tüm sağlayıcıların hesaplarını ve API anahtarlarını yönetin. Kimlik bilgisi durumunu, yönlendirme kapasitesini ve havuz yedeklerini tek yerden izleyin.',
            models_title: 'Yönlendirme Modelleri', models_description: 'Sanal model rotalarını yönetin ve ortak kimlik bilgileri havuzunda bulunan sağlayıcı modellerini inceleyin.',
            providers_title: 'Sağlayıcı Kimlik Bilgileri Ekle', providers_description: 'Bir sağlayıcı seçin, hesap veya API anahtarı bağlayın ve ortak yönlendirme havuzuna ekleyin.',
            settings_title: 'Sistem Yapılandırması', settings_description: 'Konsol erişimini, depolamayı, proxy’yi, yeniden deneme ilkesini, yanıt çevirisini ve keep-alive davranışını ayarlayın.',
            logs_title: 'Çalışma Zamanı Günlük Akışı', logs_description: 'Yönlendirme kararlarını, upstream yanıtlarını, kimlik bilgisi dönüşümünü ve uygulama hatalarını izleyin.',
            about_description: 'Akıllı otomatik yük devretme, belirteç farkındalıklı istek temizleme, kullanım görünürlüğü ve sorunsuz biçim çevirisi sunan kodlama araçları için evrensel bir yapay zekâ yönlendiricisi.'
        }
    },
    vi: {
        label: 'Tiếng Việt',
        messages: {
            language: 'Ngôn ngữ', dashboard: 'Tổng quan', pool: 'Kho thông tin xác thực', models: 'Mô hình', providers: 'Nhà cung cấp', settings: 'Cài đặt', logs: 'Nhật ký', about: 'Giới thiệu',
            sign_out: 'Đăng xuất', sign_in_title: 'Đăng nhập vào bảng điều khiển', login_copy: 'Quản lý định tuyến, thông tin xác thực, cơ chế dự phòng và chuyển đổi giao thức trong một không gian làm việc tập trung.',
            console_password: 'Mật khẩu bảng điều khiển', enter_password: 'Nhập mật khẩu', continue: 'Tiếp tục', setup_title: 'Tạo mật khẩu bảng điều khiển', setup_copy: 'Bảo vệ phiên bản Omni Gateway mới này trước khi mở bảng điều khiển quản trị.',
            confirm_password: 'Xác nhận mật khẩu', create_password: 'Tạo mật khẩu', footer_tagline: 'Định tuyến AI phổ quát cho công cụ lập trình.',
            dashboard_title: 'Bảng điều khiển Omni Gateway', dashboard_description: 'Theo dõi luồng yêu cầu, năng lực nhà cung cấp và chi tiết tích hợp cho lưu lượng công cụ lập trình.',
            pool_title: 'Kho thông tin xác thực nhà cung cấp', pool_description: 'Quản lý tài khoản và khóa API từ mọi nhà cung cấp đã kết nối. Theo dõi trạng thái thông tin xác thực, năng lực định tuyến và bản sao lưu tại một nơi.',
            models_title: 'Mô hình định tuyến', models_description: 'Quản lý các tuyến mô hình ảo và kiểm tra mô hình của nhà cung cấp có trong kho thông tin xác thực dùng chung.',
            providers_title: 'Thêm thông tin xác thực nhà cung cấp', providers_description: 'Chọn nhà cung cấp, kết nối tài khoản hoặc khóa API, rồi thêm vào kho định tuyến dùng chung.',
            settings_title: 'Cấu hình hệ thống', settings_description: 'Điều chỉnh quyền truy cập bảng điều khiển, lưu trữ, proxy, chính sách thử lại, chuyển đổi phản hồi và cơ chế keep-alive.',
            logs_title: 'Luồng nhật ký thời gian chạy', logs_description: 'Theo dõi quyết định định tuyến, phản hồi upstream, quá trình luân phiên thông tin xác thực và lỗi ứng dụng.',
            about_description: 'Bộ định tuyến AI phổ quát cho công cụ lập trình với cơ chế dự phòng thông minh, làm sạch yêu cầu theo token, hiển thị mức sử dụng và chuyển đổi định dạng liền mạch.'
        }
    }
};

const COMMON_UI_TRANSLATIONS = {
    en: { save: 'Save', refresh: 'Refresh', import_zip: 'Import ZIP', download_zip: 'Download ZIP', download: 'Download', clear: 'Clear', reset_defaults: 'Reset defaults', check_for_updates: 'Check for updates', time_range: 'Time range', one_day: '1 day', seven_days: '7 days', thirty_days: '30 days', all: 'All', api_key: 'API key', openai_base_url: 'OpenAI base URL', anthropic_base_url: 'Anthropic base URL', google_genai_base_url: 'Google GenAI base URL' },
    'zh-CN': { save: '保存', refresh: '刷新', import_zip: '导入 ZIP', download_zip: '下载 ZIP', download: '下载', clear: '清除', reset_defaults: '恢复默认值', check_for_updates: '检查更新', time_range: '时间范围', one_day: '1 天', seven_days: '7 天', thirty_days: '30 天', all: '全部', api_key: 'API 密钥', openai_base_url: 'OpenAI 基础 URL', anthropic_base_url: 'Anthropic 基础 URL', google_genai_base_url: 'Google GenAI 基础 URL' },
    'zh-TW': { save: '儲存', refresh: '重新整理', import_zip: '匯入 ZIP', download_zip: '下載 ZIP', download: '下載', clear: '清除', reset_defaults: '還原預設值', check_for_updates: '檢查更新', time_range: '時間範圍', one_day: '1 天', seven_days: '7 天', thirty_days: '30 天', all: '全部', api_key: 'API 金鑰', openai_base_url: 'OpenAI 基礎 URL', anthropic_base_url: 'Anthropic 基礎 URL', google_genai_base_url: 'Google GenAI 基礎 URL' },
    de: { save: 'Speichern', refresh: 'Aktualisieren', import_zip: 'ZIP importieren', download_zip: 'ZIP herunterladen', download: 'Herunterladen', clear: 'Leeren', reset_defaults: 'Standardwerte wiederherstellen', check_for_updates: 'Nach Updates suchen', time_range: 'Zeitraum', one_day: '1 Tag', seven_days: '7 Tage', thirty_days: '30 Tage', all: 'Alle', api_key: 'API-Schlüssel', openai_base_url: 'OpenAI-Basis-URL', anthropic_base_url: 'Anthropic-Basis-URL', google_genai_base_url: 'Google-GenAI-Basis-URL' },
    es: { save: 'Guardar', refresh: 'Actualizar', import_zip: 'Importar ZIP', download_zip: 'Descargar ZIP', download: 'Descargar', clear: 'Limpiar', reset_defaults: 'Restablecer valores predeterminados', check_for_updates: 'Buscar actualizaciones', time_range: 'Periodo', one_day: '1 día', seven_days: '7 días', thirty_days: '30 días', all: 'Todo', api_key: 'Clave API', openai_base_url: 'URL base de OpenAI', anthropic_base_url: 'URL base de Anthropic', google_genai_base_url: 'URL base de Google GenAI' },
    fr: { save: 'Enregistrer', refresh: 'Actualiser', import_zip: 'Importer un ZIP', download_zip: 'Télécharger le ZIP', download: 'Télécharger', clear: 'Effacer', reset_defaults: 'Rétablir les valeurs par défaut', check_for_updates: 'Rechercher des mises à jour', time_range: 'Période', one_day: '1 jour', seven_days: '7 jours', thirty_days: '30 jours', all: 'Tout', api_key: 'Clé API', openai_base_url: 'URL de base OpenAI', anthropic_base_url: 'URL de base Anthropic', google_genai_base_url: 'URL de base Google GenAI' },
    id: { save: 'Simpan', refresh: 'Muat ulang', import_zip: 'Impor ZIP', download_zip: 'Unduh ZIP', download: 'Unduh', clear: 'Bersihkan', reset_defaults: 'Pulihkan default', check_for_updates: 'Periksa pembaruan', time_range: 'Rentang waktu', one_day: '1 hari', seven_days: '7 hari', thirty_days: '30 hari', all: 'Semua', api_key: 'Kunci API', openai_base_url: 'URL dasar OpenAI', anthropic_base_url: 'URL dasar Anthropic', google_genai_base_url: 'URL dasar Google GenAI' },
    it: { save: 'Salva', refresh: 'Aggiorna', import_zip: 'Importa ZIP', download_zip: 'Scarica ZIP', download: 'Scarica', clear: 'Cancella', reset_defaults: 'Ripristina predefiniti', check_for_updates: 'Verifica aggiornamenti', time_range: 'Intervallo di tempo', one_day: '1 giorno', seven_days: '7 giorni', thirty_days: '30 giorni', all: 'Tutti', api_key: 'Chiave API', openai_base_url: 'URL di base OpenAI', anthropic_base_url: 'URL di base Anthropic', google_genai_base_url: 'URL di base Google GenAI' },
    ja: { save: '保存', refresh: '更新', import_zip: 'ZIP をインポート', download_zip: 'ZIP をダウンロード', download: 'ダウンロード', clear: '消去', reset_defaults: '既定値に戻す', check_for_updates: '更新を確認', time_range: '期間', one_day: '1 日', seven_days: '7 日', thirty_days: '30 日', all: 'すべて', api_key: 'API キー', openai_base_url: 'OpenAI ベース URL', anthropic_base_url: 'Anthropic ベース URL', google_genai_base_url: 'Google GenAI ベース URL' },
    ko: { save: '저장', refresh: '새로 고침', import_zip: 'ZIP 가져오기', download_zip: 'ZIP 다운로드', download: '다운로드', clear: '지우기', reset_defaults: '기본값으로 재설정', check_for_updates: '업데이트 확인', time_range: '기간', one_day: '1일', seven_days: '7일', thirty_days: '30일', all: '전체', api_key: 'API 키', openai_base_url: 'OpenAI 기본 URL', anthropic_base_url: 'Anthropic 기본 URL', google_genai_base_url: 'Google GenAI 기본 URL' },
    pt: { save: 'Salvar', refresh: 'Atualizar', import_zip: 'Importar ZIP', download_zip: 'Baixar ZIP', download: 'Baixar', clear: 'Limpar', reset_defaults: 'Restaurar padrão', check_for_updates: 'Verificar atualizações', time_range: 'Período', one_day: '1 dia', seven_days: '7 dias', thirty_days: '30 dias', all: 'Todos', api_key: 'Chave de API', openai_base_url: 'URL base do OpenAI', anthropic_base_url: 'URL base do Anthropic', google_genai_base_url: 'URL base do Google GenAI' },
    ru: { save: 'Сохранить', refresh: 'Обновить', import_zip: 'Импортировать ZIP', download_zip: 'Скачать ZIP', download: 'Скачать', clear: 'Очистить', reset_defaults: 'Восстановить по умолчанию', check_for_updates: 'Проверить обновления', time_range: 'Период', one_day: '1 день', seven_days: '7 дней', thirty_days: '30 дней', all: 'Все', api_key: 'Ключ API', openai_base_url: 'Базовый URL OpenAI', anthropic_base_url: 'Базовый URL Anthropic', google_genai_base_url: 'Базовый URL Google GenAI' },
    th: { save: 'บันทึก', refresh: 'รีเฟรช', import_zip: 'นำเข้า ZIP', download_zip: 'ดาวน์โหลด ZIP', download: 'ดาวน์โหลด', clear: 'ล้าง', reset_defaults: 'คืนค่าเริ่มต้น', check_for_updates: 'ตรวจสอบการอัปเดต', time_range: 'ช่วงเวลา', one_day: '1 วัน', seven_days: '7 วัน', thirty_days: '30 วัน', all: 'ทั้งหมด', api_key: 'คีย์ API', openai_base_url: 'URL หลักของ OpenAI', anthropic_base_url: 'URL หลักของ Anthropic', google_genai_base_url: 'URL หลักของ Google GenAI' },
    tr: { save: 'Kaydet', refresh: 'Yenile', import_zip: 'ZIP içe aktar', download_zip: 'ZIP indir', download: 'İndir', clear: 'Temizle', reset_defaults: 'Varsayılanları geri yükle', check_for_updates: 'Güncellemeleri denetle', time_range: 'Zaman aralığı', one_day: '1 gün', seven_days: '7 gün', thirty_days: '30 gün', all: 'Tümü', api_key: 'API anahtarı', openai_base_url: 'OpenAI temel URL’si', anthropic_base_url: 'Anthropic temel URL’si', google_genai_base_url: 'Google GenAI temel URL’si' },
    vi: { save: 'Lưu', refresh: 'Làm mới', import_zip: 'Nhập ZIP', download_zip: 'Tải ZIP xuống', download: 'Tải xuống', clear: 'Xóa', reset_defaults: 'Khôi phục mặc định', check_for_updates: 'Kiểm tra bản cập nhật', time_range: 'Khoảng thời gian', one_day: '1 ngày', seven_days: '7 ngày', thirty_days: '30 ngày', all: 'Tất cả', api_key: 'Khóa API', openai_base_url: 'URL cơ sở OpenAI', anthropic_base_url: 'URL cơ sở Anthropic', google_genai_base_url: 'URL cơ sở Google GenAI' }
};
