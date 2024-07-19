# 🚀 PDF Chat Assistant

Welcome to the PDF Chat Assistant project! This advanced application leverages the power of AI to transform how you interact with PDF documents. Say goodbye to endless scrolling and manual searches—our intelligent assistant is here to help you extract information from PDFs with ease and precision.

## 🌟 Features

- **Smart PDF Processing**: Automatically splits and analyzes PDF content, preserving structure and context.
- **AI-Powered Conversations**: Engage in natural language conversations about your PDF content using advanced language models.
- **Semantic Search**: Quickly find relevant information using state-of-the-art embedding techniques.
- **Multi-PDF Support**: Search across multiple documents or focus on a specific PDF.
- **Serverless Architecture**: Built on AWS for scalability and performance.
- **Real-time Processing Updates**: Users are notified when PDF processing is complete.
- **Robust Error Handling**: Comprehensive error management and notification system.

## 🛠️ Technology Stack

- **AWS Lambda**: For serverless compute.
- **AWS Step Functions**: For orchestrating the PDF processing workflow.
- **Amazon S3**: For storing PDF files, chunks, and embeddings.
- **PostgreSQL with pgvector**: For efficient storage and querying of embeddings.
- **Amazon Lex**: For natural language understanding and conversation management.
- **OpenAI API**: For generating embeddings and powering conversations.
- **Python**: The core programming language used.
- **Amazon SNS**: For error notifications and system alerts.

## 🏗️ Architecture

1. **PDF Upload**: Users upload PDFs through a frontend interface.
2. **Processing Pipeline**:
   - PDF splitting with context-aware chunking
   - Text extraction and cleaning
   - Embedding generation using OpenAI's latest models
   - Efficient storage in PostgreSQL with pgvector
3. **Chat Interface**: Users can ask questions about the PDF content using natural language.
4. **AI-Powered Responses**: The system retrieves relevant information and generates human-like responses using advanced language models.
5. **Session Management**: Amazon Lex maintains conversation context and processing status.

## 🚀 Getting Started

### Prerequisites

- AWS Account
- OpenAI API Key
- PostgreSQL database with pgvector extension
- Amazon Lex bot configured for PDF chat

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-chat-assistant.git
   ```

2. Set up your environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   export DB_NAME=your_db_name
   export DB_USER=your_db_user
   export DB_PASSWORD=your_db_password
   export DB_HOST=your_db_host
   export DB_PORT=your_db_port
   export BOT_NAME=your_lex_bot_name
   export BOT_ALIAS=your_lex_bot_alias
   export SNS_TOPIC_ARN=your_sns_topic_arn
   ```

3. Deploy the AWS Lambda functions and Step Functions state machine using AWS SAM or CloudFormation.

4. Configure your Amazon Lex bot with the appropriate intents and slot types for PDF chat.

5. Set up your frontend to interact with the AWS services and Lex bot.

## 💬 Usage

1. Upload a PDF through the frontend interface.
2. Wait for the processing to complete (you'll receive a notification).
3. Start asking questions about your PDF in natural language.
4. Enjoy accurate, context-aware responses from your AI assistant.

## 🛠️ Development

To contribute to the project or customize it for your needs:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes, ensuring you follow the existing code style and patterns.
4. Write or update tests as necessary.
5. Submit a pull request with a clear description of your changes.

## 🐛 Troubleshooting

If you encounter any issues:

1. Check the CloudWatch logs for the relevant Lambda functions.
2. Ensure all environment variables are correctly set.
3. Verify that the PostgreSQL database is accessible and the pgvector extension is enabled.
4. Check the SNS topic for any error notifications.

---

Built with ❤️ by Gravitas AI Team

Got questions? Reach out to us at [deshmukhpratik931@gmail.com](deshmukhpratik931@gmail.com)
