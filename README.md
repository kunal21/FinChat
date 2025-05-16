# FinChat - A Conversational Finance Assistant

A responsive, AI-powered financial management application designed to aggregate your financial data, provide real-time insights, and respond to natural-language queries about your personal finances.

## 🚀 Features

* **Conversational AI:** Leverages GPT-4 (LLMs) and Retrieval-Augmented Generation (RAG) to accurately interpret and respond to natural-language financial queries.
* **Interactive Dashboard:** Built with TypeScript, displaying aggregated financial metrics including net worth, income, expenses, and categorized transactions.
* **Secure Integration:** Seamlessly integrates with Plaid APIs to fetch transaction and balance data across multiple financial institutions.
* **Structured Data Pipelines:** Containerized ETL pipelines ensure efficient processing, storage, and retrieval of financial data.
* **Containerized Deployment:** Application and services deployed using Docker, ensuring portability, scalability, and ease of management.

## 🛠️ Tech Stack

* **Frontend:** React, TypeScript, TailwindCSS
* **Backend:** Python (Flask/FastAPI), OpenAI API, Plaid API
* **AI & NLP:** GPT-4, Prompt Engineering, RAG
* **Database:** PostgreSQL
* **Containerization:** Docker

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kunal21/FinChat.git
   cd finance-assistant
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   # Fill in your OpenAI and Plaid API keys
   ```

3. Build and run containers:

   ```bash
   docker-compose up --build
   ```

## 🎯 Usage

* Visit the application on `http://localhost:3000`
* Connect your financial accounts securely using Plaid.
* Ask natural-language financial queries (e.g., "How much did I spend on groceries last month?")
* View real-time updates of your financial metrics and dashboards.

## ✅ Future Enhancements

* Fine-tuning LLM models for improved accuracy
* Enhanced analytics and predictive insights
* Mobile application support

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Built with ❤️ by \[Your Name]
