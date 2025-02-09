# 📌 Proyecto Flask

Este es un proyecto basado en **Flask**, diseñado para proporcionar una API modular y escalable.

---

## 🚀 Instalación y Configuración

### 1️⃣ **Requisitos Previos**
Asegúrate de tener instalado:
- **Python 3.12**
- **pip** (Administrador de paquetes de Python)

### 2️⃣ **Crear un Entorno Virtual**
```bash
python -m venv env
```

### 3️⃣ **Activar el Entorno Virtual**
#### 🔹 En Windows:
```bash
env\Scripts\activate
```

#### 🔹 En Mac/Linux:
```bash
source env/bin/activate
```

### 4️⃣ **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 5️⃣ **Configurar Variables de Entorno**
Crea un archivo **.env** en la raíz del proyecto y agrega las siguientes variables:
```ini
JWT_SECRET_KEY=tu_clave_secreta
APP_TIMEZONE=UTC
JWT_ACCESS_TOKEN_EXPIRES=15
PORT=5000
```

### 6️⃣ **Ejecutar la Aplicación**
```bash
python app.py
```

---

## 📁 Estructura del Proyecto
```
📂 app/
 ├── 📂 models/
 ├── 📂 routes/
 │   ├── __init__.py
 │   ├── auth.py
 │   ├── empleado.py
 │   ├── ...
 ├── app.py
 ├── requirements.txt
 ├── .env
 ├── .gitignore
 ├── README.md
```

---

## 🛠 Herramientas Utilizadas
- **Flask** - Microframework web en Python.
- **Flask-JWT-Extended** - Autenticación JWT.
- **Flask-CORS** - Soporte para solicitudes CORS.
- **dotenv** - Manejo de variables de entorno.

---

## 📜 Archivo .gitignore
Asegúrate de no subir archivos sensibles al repositorio.
Contenido recomendado para **.gitignore**:
```
# Entorno Virtual
env/
venv/

# Configuración y Variables de Entorno
*.env
__pycache__/

# Archivos generados
*.pyc
*.pyo
*.log
.DS_Store
```

---

## 📌 Notas Adicionales
Si tienes problemas con la instalación, verifica que Python 3.12 esté instalado y configurado correctamente en tu sistema.

