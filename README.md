# Data Insights App - Chat with Data

**Midterm 1 Project**

Bu loyiha ma'lumotlar bazasi bilan suhbatlashuvchi AI agent bo'lib, foydalanuvchi savollariga to'g'ridan-to'g'ri DB'dan olingan natijalar asosida javob beradi.

## 🎯 Loyiha Maqsadi

- Chat orqali data analytics
- LLM'ni DB'dan to'liq ajratish
- Function calling ishlatish
- Support ticket tizimini integratsiya qilish

## ✨ Xususiyatlar

- 🤖 **AI Agent**: Cerebras LLM (Llama-3.3-70b) orqali tabiiy til bilan ma'lumotlar bilan suhbatlashish
- 🔒 **Xavfsizlik**: 
  - LLM to'g'ridan-to'g'ri ma'lumotlar bazasiga kirish huquqiga ega emas
  - DELETE/DROP va boshqa xavfli operatsiyalar bloklangan
  - Faqat belgilangan funksiya chaqiruvlari orqali ishlaydi
- 📊 **Vizualizatsiya**: 
  - Jadval formatida ma'lumotlar
  - Chart.js orqali grafiklar (bar, pie)
  - Statistik ma'lumotlar
- 🎫 **Support Ticket**: 
  - GitHub Issues integratsiyasi
  - Trello integratsiyasi
  - Jira integratsiyasi
- 🛠️ **Tool-based Architecture**: Agent faqat belgilangan funksiyalar orqali ma'lumotlarga kirish huquqiga ega

## 🛠️ Texnologiyalar

### Backend
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Cerebras Cloud SDK**: LLM integratsiyasi
- **SQLite**: Ma'lumotlar bazasi
- **Pydantic**: Data validation

### Frontend
- **HTML5, CSS3, JavaScript**: Frontend interfeys
- **Chart.js**: Grafiklar va diagrammalar

## 📋 Talablar

- Python 3.8+
- Node.js (faqat development uchun)

## 🚀 O'rnatish

1. **Repository ni klonlang:**
```bash
git clone <repository-url>
cd DATA-INSIGHTS-APP-(CHAT-WITH-DATA)
```

2. **Virtual environment yarating va faollashtiring:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Kerakli paketlarni o'rnating:**
```bash
pip install -r requirements.txt
```

4. **`.env` faylini yarating va API kalitni qo'shing:**
```bash
CEREBRAS_API_KEY=your_api_key_here

# Ixtiyoriy: External service integratsiyalari
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo
TRELLO_API_KEY=your_trello_key
TRELLO_TOKEN=your_trello_token
TRELLO_LIST_ID=your_list_id
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email
JIRA_TOKEN=your_jira_token
JIRA_PROJECT=PROJECT_KEY
```

5. **Ma'lumotlar bazasini yarating va ma'lumotlarni to'ldiring:**
```bash
python scripts/seed_data.py
```

## ▶️ Ishga tushirish

**Backend server ni ishga tushiring:**
```bash
uvicorn app.main:app --reload
```

**Frontend ni ochish:**
- Brauzerda oching: `http://localhost:8000/static/index.html`
- Yoki: `http://localhost:8000/` (API endpointlar ro'yxati)

**API dokumentatsiyasini ko'rish:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/api/chat` | Chat so'rovi |
| GET | `/api/data/summary` | DB statistikasi |
| POST | `/api/ticket/create` | Support ticket yaratish |
| GET | `/api/ticket/list` | Ticketlar ro'yxati |
| GET | `/api/tools` | Mavjud functionlar ro'yxati |

### POST /api/chat

Ma'lumotlar haqida savol berish uchun endpoint.

**Request:**
```json
{
  "message": "Jami nechta foydalanuvchi bor?"
}
```

**Response:**
```json
{
  "tool_used": "get_row_count",
  "result": 150,
  "visualization": {
    "type": "stat",
    "value": 150
  }
}
```

### GET /api/data/summary

Ma'lumotlar bazasi statistikasini olish.

**Response:**
```json
{
  "tables": {
    "users": {"count": 150},
    "orders": {"count": 600, "avg_amount": 255.5},
    "sales": {"count": 750, "total_revenue": 287500.0, "avg_revenue": 383.33}
  },
  "summary": {
    "total_users": 150,
    "total_orders": 600,
    "total_sales": 750,
    "total_revenue": 287500.0
  }
}
```

### POST /api/ticket/create

Support ticket yaratish.

**Request:**
```json
{
  "title": "Bug report",
  "description": "Detailed description",
  "priority": "high",
  "integrate_with": "github"
}
```

## 🛠️ Mavjud Tool'lar

1. **get_row_count**: Jadvaldagi qatorlar sonini olish
   - Parametrlar: `table` (users, orders, sales)
   - Qaytaradi: Integer

2. **get_recent_records**: Eng so'nggi yozuvlarni olish
   - Parametrlar: `table` (orders, sales), `limit` (default: 5, max: 100)
   - Qaytaradi: Array of records

3. **get_sales_stats**: Sales statistikasini olish
   - Parametrlar: yo'q
   - Qaytaradi: Object (total_sales, avg_sales, max_sale)

## 📁 Loyiha Strukturasi

```
.
├── app/
│   ├── api/
│   │   ├── chat.py          # Chat endpoint
│   │   ├── data.py          # Data summary endpoint
│   │   ├── ticket.py        # Ticket endpoints
│   │   └── tools.py         # Tools listing endpoint
│   ├── core/
│   │   ├── config.py        # Konfiguratsiya
│   │   ├── safety.py        # Safety mexanizmlar
│   │   └── security.py      # Xavfsizlik
│   ├── db/
│   │   ├── database.py      # DB sozlamalari
│   │   └── models.py        # SQLAlchemy modellari
│   ├── services/
│   │   ├── agent.py         # AI agent logikasi
│   │   ├── tools.py          # Tool funksiyalari
│   │   └── ticket_service.py # Ticket service
│   └── main.py              # FastAPI app
├── static/
│   ├── index.html           # Frontend HTML
│   ├── style.css            # CSS styles
│   └── app.js               # Frontend JavaScript
├── scripts/
│   └── seed_data.py         # Ma'lumotlar to'ldirish
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔒 Xavfsizlik

- ✅ API kalit `.env` faylida saqlanadi va `.gitignore` ga qo'shilgan
- ✅ LLM to'g'ridan-to'ri SQL so'rovlar yozishga qodir emas
- ✅ Faqat belgilangan tool'lar orqali ma'lumotlarga kirish mumkin
- ✅ DELETE, DROP, TRUNCATE va boshqa xavfli operatsiyalar bloklangan
- ✅ Input sanitization va validation
- ✅ Table name validation

## 📊 Ma'lumotlar Bazasi

Loyiha SQLite ma'lumotlar bazasidan foydalanadi:

- **users**: Foydalanuvchilar (150+ qator)
- **orders**: Buyurtmalar (600+ qator)
- **sales**: Savdolar (750+ qator)
- **support_tickets**: Support ticketlar

## 🎨 Frontend Xususiyatlari

- 💬 **Chat Interfeys**: Real-time chat bilan AI agent
- 📊 **Vizualizatsiya**: 
  - Jadval formatida ma'lumotlar
  - Bar va Pie chartlar
  - Statistik kartalar
- 🎫 **Ticket Yaratish**: Modal oyna orqali support ticket yaratish
- 📱 **Responsive Design**: Mobil va desktop uchun moslashtirilgan

## 🔧 Rivojlantirish

### Yangi tool qo'shish:

1. `app/services/tools.py` ga yangi funksiya qo'shing
2. `app/services/agent.py` dagi `tools_schema` ga yangi tool qo'shing
3. `app/api/tools.py` dagi ro'yxatni yangilang

### External service integratsiyasi:

1. `.env` fayliga kerakli tokenlar va sozlamalarni qo'shing
2. `app/services/ticket_service.py` da integratsiya logikasini yaxshilang

## 🐛 Muammolar

Agar muammo yuzaga kelsa, quyidagilarni tekshiring:

- `.env` fayli mavjudligi va API kalit to'g'riligini
- Ma'lumotlar bazasi yaratilganligini (`data.db` fayli)
- Barcha paketlar o'rnatilganligini
- Server ishga tushganligini (port 8000)
- CORS sozlamalari (agar frontend boshqa portda ishlayotgan bo'lsa)

## 📝 Misollar

### Savollar:

- "Nechta foydalanuvchi bor?"
- "Oxirgi 10 ta buyurtma"
- "Sales statistikasini ko'rsating"
- "Eng ko'p daromad qilgan savdo"
- "Jami nechta buyurtma bor?"

### Vizualizatsiya:

- **Stat**: Raqamli natijalar statistik kartalar sifatida
- **Table**: Ko'p qatorli ma'lumotlar jadval formatida
- **Chart**: Statistik ma'lumotlar grafik formatida

## 🚀 Production Deployment

Production uchun:

1. `.env` faylida production API kalitlarini sozlang
2. CORS sozlamalarini cheklang (faqat kerakli domainlar)
3. Database backup mexanizmini qo'shing
4. Logging tizimini qo'shing
5. Error monitoring qo'shing

## 📄 License

Bu loyiha o'quv maqsadida yaratilgan.

## 👥 Muallif

PDP University - Third Course - 1st Semester - API Course

---

**Eslatma**: Bu loyiha Midterm 1 project sifatida yaratilgan va barcha talablar bajarilgan.
