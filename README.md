# 💸 AI Refund Assistant

An intelligent Refund & Policy Assistant built using Retrieval-Augmented Generation (RAG), LangChain, ChromaDB, Groq LLM, and Streamlit.

The assistant helps customers understand refund policies, check refund eligibility, retrieve return/exchange procedures, and verify refund claims using image-based evidence analysis.

---

## 🚀 Features

### ✅ Refund Eligibility Check
- Determines whether a customer is eligible for a refund, exchange, or cancellation.
- Evaluates return windows, policy conditions, and eligibility criteria.

### 📋 Policy Information Retrieval
Provides answers related to:
- Refund policies
- Return windows
- Exchange rules
- Cancellation policies
- Eligible conditions
- Non-eligible conditions

### 🔄 Refund, Exchange & Cancellation Process
- Returns step-by-step instructions for:
  - Refund requests
  - Exchange requests
  - Order cancellations

### 🏢 Multi-Company Support
- Supports multiple companies and product categories.
- Automatically detects the relevant company from user queries.

### 📸 Image-Based Claim Verification
Supports image uploads for:
- Damaged products
- Defective items
- Spoiled or expired food
- Torn clothing
- Wrong item received
- Digital subscription billing issues

### 🤖 AI-Powered Evidence Analysis
- Uses Groq Vision models to analyze uploaded images.
- Generates refund approval recommendations based on visible evidence.

### 📊 Structured AI Responses
- Uses Pydantic Output Parsers for reliable and structured responses.
- Ensures consistency across all refund-related queries.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|----------|
| Python | Core Development |
| Streamlit | User Interface |
| LangChain | LLM Orchestration |
| ChromaDB | Vector Database |
| HuggingFace Embeddings | Semantic Search |
| Groq LLaMA 3.3 70B | Response Generation |
| Groq Vision Model | Image Analysis |
| Pydantic | Structured Output Validation |
| HTTPX | API Communication |

---

## 🏗️ System Architecture

```text
User Query
     │
     ▼
Streamlit UI
     │
     ▼
Company Detection
     │
     ▼
ChromaDB Retrieval
     │
     ▼
Policy Context + Process Context
     │
     ▼
LangChain Prompt Pipeline
     │
     ▼
Groq LLM
     │
     ▼
Pydantic Output Parser
     │
     ▼
Structured Response
```

### Image Verification Workflow

```text
User Uploads Image
        │
        ▼
Groq Vision Model
        │
        ▼
Evidence Analysis
        │
        ▼
Refund Confirmation Chain
        │
        ▼
Final Approval Decision
```

---

## 🔄 Project Workflow

### Step 1: User Query
The user asks a refund-related question.

**Example:**
```text
I ordered a laptop but received a mobile phone.
```

### Step 2: Context Retrieval
Relevant policy and process documents are retrieved from ChromaDB using semantic search.

### Step 3: Query Classification
The query is classified into:
- Eligibility
- Process
- Policy Information
- General Query

### Step 4: Response Generation
Retrieved context is passed to the Groq LLM through LangChain.

### Step 5: Structured Output
Responses are validated using Pydantic schemas to ensure consistent output.

### Step 6: Image Verification (Optional)
For claims involving:
- Product damage
- Manufacturing defects
- Spoiled food
- Wrong item received
- Missing items

the assistant requests image proof before confirming the refund.

---

## 💬 Example Queries

### Eligibility

```text
My food arrived spoiled. Can I get a refund?
```

```text
I ordered a laptop but received a mobile phone.
```

### Policy Information

```text
What is the refund policy for TechZone?
```

### Process

```text
How do I return my order?
```

```text
How can I request an exchange?
```

### Cancellation

```text
Can I cancel my order?
```

---

## 🧠 AI Concepts Used

- Retrieval-Augmented Generation (RAG)
- Vector Search
- Semantic Retrieval
- Embeddings
- Prompt Engineering
- Structured Output Parsing
- Multimodal AI
- Vision-Language Models
- Metadata Filtering
- Context-Aware Question Answering

---

## 📈 Future Enhancements

- User Authentication
- Refund Ticket Generation
- Email Notifications
- Order Tracking Integration
- Human Agent Escalation
- Support for Additional Retailers
- Analytics Dashboard

---

## 👨‍💻 Author

**Harshith**

AI / GenAI Developer

**Skills**
- Python
- Machine Learning
- LangChain
- RAG
- ChromaDB
- Streamlit
- Groq LLM
- Generative AI

---
⭐ If you found this project useful, consider giving it a star.
