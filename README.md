# 🚀 PDF Chat Assistant

Welcome to the PDF Chat Assistant project! This cutting-edge application leverages the power of AI to transform the way you interact with PDF documents. Say goodbye to endless scrolling and manual searches - our intelligent assistant is here to help you extract information from PDFs with ease and precision.

## 🌟 Features

- **Smart PDF Processing**: Automatically splits and analyzes PDF content.
- **AI-Powered Conversations**: Engage in natural language conversations about your PDF content.
- **Semantic Search**: Find relevant information quickly using advanced embedding techniques.
- **Multi-PDF Support**: Search across multiple documents or focus on a specific PDF.
- **Serverless Architecture**: Built on AWS for scalability and performance.

## 🛠️ Technology Stack

- **AWS Lambda**: For serverless compute.
- **AWS Step Functions**: For orchestrating the PDF processing workflow.
- **Amazon S3**: For storing PDF files and chunks.
- **PostgreSQL with pgvector**: For storing and querying embeddings.
- **OpenAI API**: For generating embeddings and powering conversations.
- **Python**: The core programming language used.

## 🏗️ Architecture

1. **PDF Upload**: Users upload PDFs through a frontend interface.
2. **Processing Pipeline**: 
   - PDF splitting
   - Text extraction
   - Embedding generation
   - Database storage
3. **Chat Interface**: Users can ask questions about the PDF content.
4. **AI-Powered Responses**: The system retrieves relevant information and generates human-like responses.

## 🚀 Getting Started

### Prerequisites

- AWS Account
- OpenAI API Key
- PostgreSQL database with pgvector extension

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/inquisitour/AWS_PDFChat.git
   ```

2. Set up your environment variables:
   ```
   export OPENAI_API_KEY=your_api_key_here
   export DB_NAME=your_db_name
   export DB_USER=your_db_user
   export DB_PASSWORD=your_db_password
   export DB_HOST=your_db_host
   export DB_PORT=your_db_port
   ```

3. Deploy the AWS Lambda functions and Step Functions state machine using AWS CLI or AWS Console.

4. Set up your frontend to interact with the AWS services.

## 💬 Usage

1. Upload a PDF through the frontend interface.
2. Wait for the processing to complete.
3. Start asking questions about your PDF in natural language!
4. Enjoy accurate, context-aware responses from your AI assistant.

---

Built with ❤️ by [Gravitas AI Team]

Got questions? Reach out to us at [deshmukhpratik931@gmail.com](deshmukhpratik931@gmail.com)
