# MeasureIT API

MeasureIT API is a scalable FastAPI application designed for the ingestion and querying of (time-series) data from a multitude of signal sources. It offers a robust, efficient, and reliable solution for managing and processing data in a streamlined and organized manner.


<div style="color: red;">
Please note: MeasureIt is still an active work in progress
</div>

## 📌 Features

- **CRUD Endpoints**: Comprehensive Create, Read, Update, and Delete (CRUD) endpoints for managing clients, users, devices, units, tariffs, signals, and measurements.

- **Swagger UI Documentation**: In-built Swagger UI documentation for effortless API exploration and understanding.
- **PostgreSQL Database with PostGIS Extension**: Utilizes PostgreSQL with the PostGIS extension for secure, efficient data storage and advanced geospatial data processing.
- **Pydantic Models and Validation**: Ensures data integrity with the help of Pydantic models and validation.
- **Docker Containerization**: The entire application is containerized with Docker and docker-compose for hassle-free deployment and scalability.

## 🚀 Endpoints

The API provides the following principal endpoints:

- `/clients` - Manage clients
- `/users` - Manage user accounts associated with clients
- `/devices` - Manage device info for signals (optional associated with clients)
- `/units` - Manage unit info for signals
- `/tariffs` - Manage pricing tariffs for measurements
- `/signals` - Manage signal info for measurements
- `/measurements` - Store measurements 
- `/utils` - initiate and populate the database
- `/geo` - Geospatial endpoints leveraging PostGIS for geographical queries (Coming Soon)


## 🚀 Getting Started

### 🛠️ Install Dependencies

To get started, make sure you have the following tools installed on your system:

- Docker
- Docker Compose

### 📦 Run with Docker

Follow these steps to run the API using Docker:

```bash
# Build images
docker compose build --no-cache 

# Start containers 
docker compose up -d

# View logs
docker compose logs -f

# Enter the terminal
docker exec -it measureIt bash
```
Then, navigate to http://localhost:8000 to access the API.

### 📚 Database

Measurements are stored in a PostgreSQL database with the PostGIS extension, which is automatically configured for you when you run the application.

### 📜 Documentation

API documentation is auto-generated using Swagger UI. It provides an interactive exploration of your API's functionality. You can access it at http://localhost:8000/docs.

## 🤝 Contributing

Your contributions to the improvement of MeasureIT API are most welcome! Feel free to make pull requests. If you have any ideas or suggestions for enhancements, don't hesitate to open an issue first to discuss them.

## 📄 License

MeasureIT API is open-source software licensed under the MIT license. For more details, please see the LICENSE file in the repository.