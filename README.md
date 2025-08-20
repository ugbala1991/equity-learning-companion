# equity-learning-companion

An **AI-powered tutoring and feedback platform** designed to reduce the **equity gap in access to quality education**.  
It provides **instant feedback**, **multilingual support**, and **offline fallback options** for students in under-resourced environments, while also giving teachers insight into classroom learning patterns.  


**Features**
- **AI-Powered Feedback**: Provides instant, rubric-aligned feedback on student answers.  
- **Multilingual Support**: Translates feedback and prompts into multiple languages for inclusivity.  
- **Offline Mode**: Falls back to a rule-based engine when AI API or internet is unavailable.  
- **Teacher Insights**: Clusters common misconceptions across student answers.  
- **Simple UI**: Students type in their answers, click a button, and instantly receive constructive feedback.  

**Setup**

1. Clone the Repository
```bash
git clone https://github.com/your-username/equity-learning-companion.git
cd equity-learning-companion

Backend Setup (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload


Backend will run at: http://localhost:8000

3. Frontend Setup (Next.js + React)
cd frontend
npm install
npm run dev


Frontend will run at: http://localhost:3000

▶️ **Usage**

Open the frontend app in your browser (http://localhost:3000).

Enter your question and answer.

Click “Get Feedback”.

Review the AI-generated or rule-based feedback.

Teachers can view analytics (future feature) to see trends in misconceptions.


****Testing****

Run backend tests:

pytest tests/


**Impact**

This project empowers students in under-resourced schools by giving them personalized learning support, regardless of class size, teacher availability, or language barriers.
By combining AI-driven feedback with offline resilience, it ensures every learner has equitable access to quality education.
