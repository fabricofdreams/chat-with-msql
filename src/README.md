# Chat to MySQL

Chat to MySQL is a Streamlit application that allows users to interact with a MySQL database using natural language. The application uses GPT-3.5 and Mixtral-8x7b-32768 to understand and respond to user queries.

## Features

- **Natural Language Interaction**: Users can interact with the application using natural language, making it easy to use for non-technical users.
- **SQL Query Generation**: The application can generate SQL queries based on user queries and the database schema.
- **Database Connection**: Users can connect to their MySQL database and start chatting immediately.

## Getting Started

1. Clone the repository: `git clone https://github.com/username/repo.git`
2. Install the required dependencies: `poetry init`
3. Set up your environment variables in a `.env` file. You will need to set the following variables:
   - `DB1_PASSWORD`: The password for your MySQL database.
   - `DB_USER`: The username for your MySQL database.
   - `HOST`: The host for your MySQL database.
   - `PORT`: The port for your MySQL database.
   - `DATABASE`: The name of your MySQL database.
4. Run the application: `streamlit run src/app.py`

## Usage

1. Connect to your database by entering your credentials in the sidebar and clicking "Connect".
2. Start chatting by typing your queries in the chat input box.
3. The application will generate SQL queries and run them on your database, then display the results in the chat.

## Contributing

Contributions are welcome! Please follow the [GitHub Flow](https://guides.github.com/introduction/flow/) when making contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
