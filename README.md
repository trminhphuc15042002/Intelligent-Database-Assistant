<img width="975" height="814" alt="image" src="https://github.com/user-attachments/assets/fac2a5df-a2d3-487d-ac94-2ff73ab28d1d" /># Intelligent Database Assistant

## 📌 Overview
Intelligent Database Assistant is a Streamlit-based application that allows users to interactively query and analyze relational databases using an AI-powered agent.  
The system connects to SQL databases, processes user queries, and generates insights and visualizations in a user-friendly interface.

---

## 🚀 Features
- Connect to relational databases (PostgreSQL, MySQL)
- AI-powered database query and analysis agent
- Interactive data exploration and visualization
- Modular and extensible agent-based architecture
- User-friendly Streamlit web interface

---

## 🛠 Tech Stack
- **Python**
- **Streamlit**
- **SQLAlchemy**
- **OpenAI API**
- **Pandas / Matplotlib**
- **PostgreSQL / MySQL**

---

## 📂 Project Structure
database_agent_ui/
│
├── graph/ # Agent workflow and graph logic
├── routers/ # Application routing logic
├── state/ # Agent state management
├── tools/ # Database and visualization tools
├── database_query_agent_ui.py
├── requirement.txt
└── .gitignore

---
## WorkFlow
<img width="975" height="814" alt="image" src="https://github.com/user-attachments/assets/df1faf72-3acc-4780-8720-1ebae5197025" />


## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2.Create and activate a virtual environment:
python -m venv myenv
source myenv/bin/activate   # On Windows: myenv\Scripts\activate
3.Install dependencies:
pip install -r requirement.txt
🔐 Environment Variables
Create a .env file in the project root and add:
OPENAI_API_KEY=your_openai_api_key
▶️ Usage
Run the Streamlit application:
streamlit run database_query_agent_ui.py
📈 Future Improvements

Support for additional database engines

Advanced query optimization

Enhanced data visualization options

User authentication and access control
