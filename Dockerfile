# Используем легковесный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта (код, модель)
COPY . .

# Указываем, какой порт слушать Streamlit
EXPOSE 8501

# Команда для запуска приложения
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]